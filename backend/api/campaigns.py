import asyncio
import json
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from db.session import get_db
from models.db import Campaign, Segment, Communication, Customer
from services.sse_bus import create_queue_sync, publish, cleanup, get_queue


class CampaignCreate(BaseModel):
    name: str
    goal: str
    segment_id: str
    channel: str
    message_variants: List[dict]
    ai_reasoning: Optional[str] = None
    trend_context: Optional[str] = None


class CampaignResponse(BaseModel):
    id: str
    name: Optional[str]
    goal: Optional[str]
    segment_id: Optional[str]
    channel: Optional[str]
    status: str
    message_variants: Optional[List[dict]]
    ai_reasoning: Optional[str]
    trend_context: Optional[str]
    insight_summary: Optional[str] = None
    launched_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class CampaignStats(BaseModel):
    sent: int
    delivered: int
    failed: int
    read: int
    clicked: int
    orders: int
    revenue: float


class VariantStats(BaseModel):
    variant_id: str
    targeting: dict
    sent: int
    read: int
    clicked: int
    orders: int


class CampaignDetailResponse(BaseModel):
    campaign: CampaignResponse
    stats: CampaignStats
    variant_breakdown: List[VariantStats]
    recent_events: List[dict]


class CopilotRequest(BaseModel):
    goal: str
    session_id: str


class LaunchResponse(BaseModel):
    launched: bool
    total_queued: int


router = APIRouter()


@router.get("/campaigns", response_model=List[CampaignResponse])
def list_campaigns(status: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Campaign)
    if status:
        query = query.filter(Campaign.status == status)
    campaigns = query.order_by(desc(Campaign.created_at)).all()
    return [CampaignResponse(
        id=str(c.id),
        name=c.name,
        goal=c.goal,
        segment_id=str(c.segment_id) if c.segment_id else None,
        channel=c.channel,
        status=c.status or "draft",
        message_variants=c.message_variants,
        ai_reasoning=c.ai_reasoning,
        trend_context=c.trend_context,
        insight_summary=c.insight_summary,
        launched_at=c.launched_at,
        completed_at=c.completed_at,
        created_at=c.created_at
    ) for c in campaigns]


@router.get("/campaigns/{campaign_id}", response_model=CampaignDetailResponse)
def get_campaign(campaign_id: str, db: Session = Depends(get_db)):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    comms = db.query(Communication).filter(Communication.campaign_id == campaign_id).all()
    
    sent = len([c for c in comms if c.status in ["sent", "delivered", "read", "clicked", "order_attributed", "failed"]])
    delivered = len([c for c in comms if c.status in ["delivered", "read", "clicked", "order_attributed"]])
    failed = len([c for c in comms if c.status == "failed"])
    read = len([c for c in comms if c.status in ["read", "clicked", "order_attributed"]])
    clicked = len([c for c in comms if c.status in ["clicked", "order_attributed"]])
    orders = len([c for c in comms if c.status == "order_attributed"])
    revenue = sum(float(c.attributed_revenue or 0) for c in comms if c.attributed_revenue)
    
    stats = CampaignStats(
        sent=sent,
        delivered=delivered,
        failed=failed,
        read=read,
        clicked=clicked,
        orders=orders,
        revenue=revenue
    )
    
    variant_stats: dict[str, dict] = {}
    for c in comms:
        vid = c.variant_id or "A"
        if vid not in variant_stats:
            variant_stats[vid] = {"sent": 0, "read": 0, "clicked": 0, "orders": 0}
        if c.status in ["sent", "delivered", "read", "clicked", "order_attributed", "failed"]:
            variant_stats[vid]["sent"] += 1
        if c.status in ["read", "clicked", "order_attributed"]:
            variant_stats[vid]["read"] += 1
        if c.status in ["clicked", "order_attributed"]:
            variant_stats[vid]["clicked"] += 1
        if c.status == "order_attributed":
            variant_stats[vid]["orders"] += 1

    variants = campaign.message_variants or []
    variant_meta = {v.get("id", "A"): v for v in variants}
    all_variant_ids = set(variant_stats.keys()) | set(variant_meta.keys())

    variant_breakdown = []
    for vid in sorted(all_variant_ids):
        meta = variant_meta.get(vid, {})
        vs = variant_stats.get(vid, {"sent": 0, "read": 0, "clicked": 0, "orders": 0})
        variant_breakdown.append(
            VariantStats(
                variant_id=vid,
                targeting=meta.get("targets", meta.get("targeting", {})),
                sent=vs["sent"],
                read=vs["read"],
                clicked=vs["clicked"],
                orders=vs["orders"],
            )
        )
    
    from services.campaign_service import build_recent_events

    recent = (
        db.query(Communication)
        .filter(Communication.campaign_id == campaign_id)
        .all()
    )
    recent_events = build_recent_events(recent, db)
    
    return CampaignDetailResponse(
        campaign=CampaignResponse(
            id=str(campaign.id),
            name=campaign.name,
            goal=campaign.goal,
            segment_id=str(campaign.segment_id) if campaign.segment_id else None,
            channel=campaign.channel,
            status=campaign.status or "draft",
            message_variants=campaign.message_variants,
            ai_reasoning=campaign.ai_reasoning,
            trend_context=campaign.trend_context,
            insight_summary=campaign.insight_summary,
            launched_at=campaign.launched_at,
            completed_at=campaign.completed_at,
            created_at=campaign.created_at
        ),
        stats=stats,
        variant_breakdown=variant_breakdown,
        recent_events=recent_events
    )


@router.post("/campaigns", response_model=CampaignResponse)
def create_campaign(data: CampaignCreate, db: Session = Depends(get_db)):
    campaign = Campaign(
        name=data.name,
        goal=data.goal,
        segment_id=data.segment_id,
        channel=data.channel,
        status="draft",
        message_variants=data.message_variants,
        ai_reasoning=data.ai_reasoning,
        trend_context=data.trend_context
    )
    db.add(campaign)
    db.commit()
    db.refresh(campaign)
    return CampaignResponse(
        id=str(campaign.id),
        name=campaign.name,
        goal=campaign.goal,
        segment_id=str(campaign.segment_id) if campaign.segment_id else None,
        channel=campaign.channel,
        status=campaign.status or "draft",
        message_variants=campaign.message_variants,
        ai_reasoning=campaign.ai_reasoning,
        trend_context=campaign.trend_context,
        insight_summary=campaign.insight_summary,
        launched_at=campaign.launched_at,
        completed_at=campaign.completed_at,
        created_at=campaign.created_at
    )


@router.post("/campaigns/{campaign_id}/launch", response_model=LaunchResponse)
async def launch_campaign(campaign_id: str, request: Request, db: Session = Depends(get_db)):
    from services.campaign_service import prepare_campaign_comms, dispatch_campaign_async
    from datetime import timezone

    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    if campaign.status != "draft":
        raise HTTPException(status_code=400, detail="Can only launch draft campaigns")

    total_queued = prepare_campaign_comms(campaign_id, db)

    campaign.status = "running"
    campaign.launched_at = datetime.now(timezone.utc)
    db.commit()

    http_client = request.app.state.http_client
    asyncio.create_task(dispatch_campaign_async(str(campaign.id), http_client))

    return LaunchResponse(launched=True, total_queued=total_queued)


@router.delete("/campaigns/{campaign_id}")
def delete_campaign(campaign_id: str, db: Session = Depends(get_db)):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    if campaign.status != "draft":
        raise HTTPException(status_code=400, detail="Can only delete draft campaigns")
    
    db.delete(campaign)
    db.commit()
    return {"deleted": True}


@router.post("/campaigns/copilot")
async def start_copilot(data: CopilotRequest):
    from agents.graph import graph
    
    create_queue_sync(data.session_id)
    
    asyncio.create_task(run_agent_pipeline(data.goal, data.session_id))
    
    return {"session_id": data.session_id}


async def run_agent_pipeline(goal: str, session_id: str):
    from datetime import datetime as dt
    from agents.graph import graph
    
    month = dt.now().month
    
    if month in [6, 7, 8, 9]:
        season_india = "summer"
    elif month in [11, 12, 1, 2]:
        season_india = "winter"
    elif month == 10 or month in [3, 4, 5]:
        season_india = "festive"
    else:
        season_india = "summer"
    
    if month >= 4 and month <= 9:
        season_intl = "winter"
    else:
        season_intl = "summer"
    
    initial_state = {
        "goal": goal,
        "session_id": session_id,
        "season_india": season_india,
        "season_intl": season_intl
    }
    
    try:
        result = await graph.ainvoke(initial_state)
    except Exception as e:
        await publish(session_id, {
            "type": "fatal_error",
            "message": str(e)
        })
    finally:
        cleanup(session_id)


@router.get("/campaigns/copilot/stream/{session_id}")
async def copilot_stream(session_id: str):
    from services.sse_bus import get_queue
    
    queue = get_queue(session_id)
    if not queue:
        queue = create_queue_sync(session_id)
    
    async def event_generator():
        while True:
            try:
                event = await asyncio.wait_for(queue.get(), timeout=60.0)
                yield f"data: {json.dumps(event)}\n\n"
                
                if event.get("type") in ["proposal_ready", "fatal_error"]:
                    break
            except asyncio.TimeoutError:
                yield f": keepalive\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }
    )


@router.get("/campaigns/{campaign_id}/stream")
async def campaign_stream(campaign_id: str, request: Request):
    from uuid import uuid4
    
    session_id = f"campaign_{campaign_id}_{uuid4().hex[:8]}"
    queue = create_queue_sync(session_id)
    
    async def event_generator():
        while True:
            if await request.is_disconnected():
                cleanup(session_id)
                break
            
            try:
                event = await asyncio.wait_for(queue.get(), timeout=30.0)
                yield f"data: {json.dumps(event)}\n\n"
                
                if event.get("type") == "campaign_complete":
                    cleanup(session_id)
                    break
            except asyncio.TimeoutError:
                yield f": keepalive\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }
    )
