from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from starlette.concurrency import run_in_threadpool
from sqlalchemy.orm import Session
from db.session import get_db
from models.db import Communication, Campaign, Customer
from services.sse_bus import create_queue_sync, get_all_session_ids


VALID_STATUSES = ["queued", "sent", "delivered", "read", "clicked", "order_attributed", "failed"]

ALLOWED_TRANSITIONS = {
    "queued": {"sent", "failed"},
    "sent": {"delivered", "failed"},
    "delivered": {"read", "failed"},
    "read": {"clicked"},
    "clicked": {"order_attributed"},
    "order_attributed": set(),
    "failed": set(),
}


def is_valid_transition(current_status: str, new_status: str) -> bool:
    if new_status not in VALID_STATUSES:
        return False
    return new_status in ALLOWED_TRANSITIONS.get(current_status, set())


class ReceiptPayload(BaseModel):
    communication_id: str
    event: str
    timestamp: str
    revenue: Optional[float] = None


router = APIRouter()


@router.post("/receipts")
async def receive_receipt(payload: ReceiptPayload, db: Session = Depends(get_db)):
    def _process_receipt():
        comm = db.query(Communication).filter(Communication.id == payload.communication_id).first()
        if not comm:
            return {"ok": True, "skipped": True, "reason": "communication not found"}

        new_status = payload.event

        if new_status not in VALID_STATUSES:
            return {"ok": True, "skipped": True, "reason": "invalid status"}

        if new_status == comm.status:
            return {"ok": True, "skipped": True, "reason": "duplicate event"}

        if not is_valid_transition(comm.status, new_status):
            return {"error": "invalid_transition"}

        comm.status = new_status

        timestamp = datetime.fromisoformat(payload.timestamp.replace("Z", "+00:00"))

        if new_status == "sent":
            comm.sent_at = timestamp
        elif new_status == "delivered":
            comm.delivered_at = timestamp
        elif new_status == "read":
            comm.read_at = timestamp
        elif new_status == "clicked":
            comm.clicked_at = timestamp
        elif new_status == "order_attributed":
            comm.order_attributed_at = timestamp
            if payload.revenue:
                comm.attributed_revenue = payload.revenue

        db.commit()

        customer = db.query(Customer).filter(Customer.id == comm.customer_id).first()
        customer_name = customer.name if customer else "Customer"

        campaign_id = str(comm.campaign_id)

        comms = db.query(Communication).filter(Communication.campaign_id == campaign_id).all()
        sent = len([c for c in comms if c.status in ["sent", "delivered", "read", "clicked", "order_attributed", "failed"]])
        delivered = len([c for c in comms if c.status in ["delivered", "read", "clicked", "order_attributed"]])
        failed = len([c for c in comms if c.status == "failed"])
        reads = len([c for c in comms if c.status in ["read", "clicked", "order_attributed"]])
        clicks = len([c for c in comms if c.status in ["clicked", "order_attributed"]])
        orders = len([c for c in comms if c.status == "order_attributed"])
        revenue = sum(float(c.attributed_revenue or 0) for c in comms)

        stats = {
            "sent": sent,
            "delivered": delivered,
            "failed": failed,
            "read": reads,
            "clicked": clicks,
            "orders": orders,
            "revenue": revenue,
        }

        matching_sessions = [
            sid for sid in get_all_session_ids()
            if sid.startswith(f"campaign_{campaign_id}")
        ]

        events_to_publish = []
        for session_id in matching_sessions:
            events_to_publish.append((session_id, {"type": "stats_update", "data": stats}))
            event_data = {
                "customer_name": customer_name,
                "event": new_status,
                "variant_id": comm.variant_id,
                "timestamp": payload.timestamp,
            }
            if new_status == "order_attributed" and payload.revenue:
                event_data["revenue"] = payload.revenue
            events_to_publish.append((session_id, {"type": "comm_event", "data": event_data}))

        return {"ok": True, "events": events_to_publish}
    
    result = await run_in_threadpool(_process_receipt)
    
    if result.get("error") == "invalid_transition":
        return JSONResponse(status_code=409, content=result)
    
    events = result.get("events", [])
    for session_id, event_data in events:
        q = create_queue_sync(session_id)
        if q:
            await q.put(event_data)
    
    return {"ok": True}
