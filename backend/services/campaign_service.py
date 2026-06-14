import asyncio
import os
import random
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from models.db import Campaign, Communication, Customer, Segment
from services.segment_engine import build_query
from services.sse_bus import publish, get_all_session_ids

REST_STATUSES = {"failed", "order_attributed"}


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _event_timestamp(comm: Communication) -> datetime | None:
    """Latest lifecycle timestamp for recent-events ordering."""
    for field in (
        comm.order_attributed_at,
        comm.clicked_at,
        comm.read_at,
        comm.delivered_at,
        comm.sent_at,
        comm.created_at,
    ):
        if field is not None:
            return field
    return None


def should_complete_campaign(campaign: Campaign, comms: list[Communication]) -> bool:
    if not comms:
        return True

    if campaign.launched_at:
        launched = campaign.launched_at
        if launched.tzinfo is None:
            launched = launched.replace(tzinfo=timezone.utc)
        if (_utcnow() - launched).total_seconds() >= 300:
            return True

    return all(c.status in REST_STATUSES for c in comms)


def prepare_campaign_comms(campaign_id: str, db: Session) -> int:
    from agents.executor import assign_variant, personalize

    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        return 0

    segment = db.query(Segment).filter(Segment.id == campaign.segment_id).first()
    if not segment:
        return 0

    existing = db.query(Communication).filter(Communication.campaign_id == campaign_id).count()
    if existing > 0:
        return existing

    customers = build_query(segment.filter_rules or {}, db).all()
    variants = campaign.message_variants or []

    for customer in customers:
        variant = assign_variant(customer, variants)
        db.add(
            Communication(
                campaign_id=campaign_id,
                customer_id=customer.id,
                variant_id=variant.get("id", "A"),
                personalized_message=personalize(variant.get("message", ""), customer),
                channel=campaign.channel,
                status="queued",
            )
        )

    db.commit()
    return len(customers)


async def dispatch_campaign_async(campaign_id: str, http_client):
    from db.session import SessionLocal

    db = SessionLocal()
    try:
        comms = db.query(Communication).filter(Communication.campaign_id == campaign_id).all()
        if not comms:
            return

        # Fetch all customers for these communications in one query
        customer_ids = {c.customer_id for c in comms}
        customers = db.query(Customer).filter(Customer.id.in_(customer_ids)).all()
        customer_map = {c.id: c for c in customers}

        # Build payload data in memory
        tasks_data = []
        for comm in comms:
            cust = customer_map.get(comm.customer_id)
            tasks_data.append({
                "communication_id": str(comm.id),
                "email": cust.email if cust else None,
                "phone": cust.phone if cust else None,
                "message": comm.personalized_message,
                "channel": comm.channel
            })
    finally:
        db.close()

    # Run HTTP requests concurrently without holding any DB session open
    semaphore = asyncio.Semaphore(20)
    failed_comm_ids = []

    async def send_with_limit(data):
        async with semaphore:
            success = await send_payload_to_channel(data, http_client)
            if not success:
                failed_comm_ids.append(data["communication_id"])

    await asyncio.gather(*[send_with_limit(d) for d in tasks_data])

    # If any sends failed, update their status to failed in a single database transaction
    if failed_comm_ids:
        db = SessionLocal()
        try:
            db.query(Communication).filter(Communication.id.in_(failed_comm_ids)).update(
                {Communication.status: "failed"}, synchronize_session=False
            )
            db.commit()
        finally:
            db.close()


async def send_payload_to_channel(data: dict, http_client) -> bool:
    payload = {
        "communication_id": data["communication_id"],
        "recipient": {
            "email": data["email"],
            "phone": data["phone"],
        },
        "message": data["message"],
        "channel": data["channel"],
    }

    channel_url = os.getenv("CHANNEL_SERVICE_URL", "http://localhost:8001")

    for attempt in range(3):
        try:
            response = await http_client.post(
                f"{channel_url}/send",
                json=payload,
                timeout=5.0,
            )
            if response.status_code == 200:
                return True
        except Exception:
            pass

        delay = min(1 * (2 ** attempt), 10) + random.uniform(0, 0.5)
        await asyncio.sleep(delay)

    return False


async def poll_all_running_campaigns():
    from db.session import SessionLocal

    db = SessionLocal()
    try:
        running = db.query(Campaign).filter(Campaign.status == "running").all()
        for campaign in running:
            comms = (
                db.query(Communication)
                .filter(Communication.campaign_id == campaign.id)
                .all()
            )
            if should_complete_campaign(campaign, comms):
                await complete_campaign(str(campaign.id), db)
    finally:
        db.close()


async def start_completion_poller():
    while True:
        try:
            await asyncio.sleep(30)
            await poll_all_running_campaigns()
        except asyncio.CancelledError:
            break
        except Exception:
            pass


def build_insight_summary(campaign: Campaign, stats: dict) -> str:
    read_pct = (stats["read"] / stats["delivered"] * 100) if stats["delivered"] else 0
    click_pct = (stats["clicked"] / stats["read"] * 100) if stats["read"] else 0
    order_pct = (stats["orders"] / stats["clicked"] * 100) if stats["clicked"] else 0

    return (
        f'Campaign "{campaign.name}" via {campaign.channel} reached {stats["delivered"]} customers '
        f'with a {read_pct:.0f}% read rate and {stats["orders"]} attributed orders '
        f'(₹{stats["revenue"]:,.0f} revenue). '
        f'Click-through was {click_pct:.0f}% of readers; {order_pct:.0f}% of clickers converted.'
    )


async def complete_campaign(campaign_id: str, db: Session):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign or campaign.status != "running":
        return

    campaign.status = "completed"
    campaign.completed_at = _utcnow()
    db.commit()

    await write_learning_and_notify(campaign_id, db)


async def write_learning_and_notify(campaign_id: str, db: Session):
    from services.learnings import write_learning, infer_style

    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        return

    comms = db.query(Communication).filter(Communication.campaign_id == campaign_id).all()

    delivered = len([c for c in comms if c.status in ["delivered", "read", "clicked", "order_attributed"]])
    reads = len([c for c in comms if c.status in ["read", "clicked", "order_attributed"]])
    clicks = len([c for c in comms if c.status in ["clicked", "order_attributed"]])
    orders = len([c for c in comms if c.status == "order_attributed"])

    open_rate = reads / delivered if delivered > 0 else 0
    click_rate = clicks / reads if reads > 0 else 0
    order_rate = orders / clicks if clicks > 0 else 0

    style = infer_style(campaign.message_variants or [])

    write_learning(
        db=db,
        campaign_id=campaign_id,
        data={
            "segment_description": campaign.goal,
            "channel": campaign.channel,
            "message_style": style,
            "open_rate": open_rate,
            "click_rate": click_rate,
            "order_rate": order_rate,
            "customer_count": len(comms),
        },
    )

    stats = {
        "sent": len([c for c in comms if c.status in ["sent", "delivered", "read", "clicked", "order_attributed", "failed"]]),
        "delivered": delivered,
        "failed": len([c for c in comms if c.status == "failed"]),
        "read": reads,
        "clicked": clicks,
        "orders": orders,
        "revenue": sum(float(c.attributed_revenue or 0) for c in comms),
    }

    insight = build_insight_summary(campaign, stats)
    campaign.insight_summary = insight
    db.commit()

    for sid in [k for k in get_all_session_ids() if k.startswith(f"campaign_{campaign_id}")]:
        await publish(
            sid,
            {
                "type": "campaign_complete",
                "data": {"final_stats": stats, "insight_summary": insight},
            },
        )


def build_recent_events(comms: list[Communication], db: Session) -> list[dict]:
    customer_ids = {c.customer_id for c in comms}
    customers = {
        row.id: row.name
        for row in db.query(Customer).filter(Customer.id.in_(customer_ids)).all()
    } if customer_ids else {}

    events = []
    for comm in comms:
        ts = _event_timestamp(comm)
        if comm.status == "queued":
            continue
        events.append(
            {
                "customer_name": customers.get(comm.customer_id, "Customer"),
                "event": comm.status,
                "variant_id": comm.variant_id,
                "timestamp": ts.isoformat() if ts else None,
                "revenue": float(comm.attributed_revenue) if comm.attributed_revenue else None,
            }
        )

    events.sort(key=lambda e: e["timestamp"] or "", reverse=True)
    return events[:20]
