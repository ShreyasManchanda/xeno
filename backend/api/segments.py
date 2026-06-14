from typing import Optional, List, Any
from pydantic import BaseModel
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, case
from db.session import get_db
from models.db import Customer, Segment, Campaign, Communication
from services.segment_engine import build_query


class FilterRule(BaseModel):
    field: str
    op: str
    value: Any


class FilterRules(BaseModel):
    operator: str = "AND"
    rules: List[FilterRule]


class SegmentCreate(BaseModel):
    name: str
    nl_query: Optional[str] = None
    filter_rules: FilterRules
    created_by: str = "manual"


class SegmentUpdate(BaseModel):
    filter_rules: FilterRules


class SegmentPreviewRequest(BaseModel):
    nl_query: str


class SegmentResponse(BaseModel):
    id: str
    name: Optional[str]
    nl_query: Optional[str]
    filter_rules: Optional[dict]
    customer_count: Optional[int]
    created_by: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class SegmentPreviewResponse(BaseModel):
    filter_rules: dict
    customer_count: int
    reasoning: str
    sample_customers: List[dict]


class SegmentPerformance(BaseModel):
    campaigns_run: int
    avg_read_rate: float
    avg_click_rate: float
    avg_order_rate: float


class SegmentDetailResponse(BaseModel):
    segment: SegmentResponse
    customers: List[dict]
    performance: SegmentPerformance


router = APIRouter()


@router.get("/segments", response_model=List[SegmentResponse])
def list_segments(db: Session = Depends(get_db)):
    segments = db.query(Segment).order_by(desc(Segment.created_at)).all()
    return [SegmentResponse(
        id=str(s.id),
        name=s.name,
        nl_query=s.nl_query,
        filter_rules=s.filter_rules,
        customer_count=s.customer_count,
        created_by=s.created_by,
        created_at=s.created_at
    ) for s in segments]


@router.post("/segments/preview", response_model=SegmentPreviewResponse)
async def preview_segment(data: SegmentPreviewRequest, db: Session = Depends(get_db)):
    from agents.analyst import run_analyst
    
    result = await run_analyst({
        "goal": data.nl_query,
        "session_id": "preview",
        "season_india": "summer",
        "season_intl": "winter"
    }, db)
    
    return SegmentPreviewResponse(
        filter_rules=result.get("filter_rules", {"operator": "AND", "rules": []}),
        customer_count=result.get("customer_count", 0),
        reasoning=result.get("reasoning", ""),
        sample_customers=result.get("sample_customers", [])
    )


@router.post("/segments", response_model=SegmentResponse)
def create_segment(data: SegmentCreate, db: Session = Depends(get_db)):
    query = build_query(data.filter_rules.model_dump(), db)
    customer_count = query.count()
    
    segment = Segment(
        name=data.name,
        nl_query=data.nl_query,
        filter_rules=data.filter_rules.model_dump(),
        customer_count=customer_count,
        created_by=data.created_by
    )
    db.add(segment)
    db.commit()
    db.refresh(segment)
    
    return SegmentResponse(
        id=str(segment.id),
        name=segment.name,
        nl_query=segment.nl_query,
        filter_rules=segment.filter_rules,
        customer_count=segment.customer_count,
        created_by=segment.created_by,
        created_at=segment.created_at
    )


@router.get("/segments/{segment_id}", response_model=SegmentDetailResponse)
def get_segment(segment_id: str, page: int = 1, limit: int = 20, db: Session = Depends(get_db)):
    segment = db.query(Segment).filter(Segment.id == segment_id).first()
    if not segment:
        raise HTTPException(status_code=404, detail="Segment not found")
    
    query = build_query(segment.filter_rules or {}, db)
    total = query.count()
    customers = query.offset((page - 1) * limit).limit(limit).all()
    
    campaign_ids = db.query(Campaign.id).filter(Campaign.segment_id == segment_id).all()
    campaign_ids = [str(c[0]) for c in campaign_ids]
    
    campaigns_run = len(campaign_ids)
    
    if campaign_ids:
        stats = db.query(
            func.count(Communication.id).label("total"),
            func.sum(
                case(
                    (Communication.status.in_(["read", "clicked", "order_attributed"]), 1),
                    else_=0,
                )
            ).label("reads"),
            func.sum(
                case(
                    (Communication.status.in_(["clicked", "order_attributed"]), 1),
                    else_=0,
                )
            ).label("clicks"),
            func.sum(
                case((Communication.status == "order_attributed", 1), else_=0)
            ).label("orders"),
        ).filter(Communication.campaign_id.in_(campaign_ids)).first()
        
        total_sent = stats.total or 0
        avg_read_rate = (stats.reads or 0) / total_sent if total_sent > 0 else 0
        avg_click_rate = (stats.clicks or 0) / total_sent if total_sent > 0 else 0
        avg_order_rate = (stats.orders or 0) / total_sent if total_sent > 0 else 0
    else:
        avg_read_rate = 0
        avg_click_rate = 0
        avg_order_rate = 0
    
    return SegmentDetailResponse(
        segment=SegmentResponse(
            id=str(segment.id),
            name=segment.name,
            nl_query=segment.nl_query,
            filter_rules=segment.filter_rules,
            customer_count=segment.customer_count,
            created_by=segment.created_by,
            created_at=segment.created_at
        ),
        customers=[{
            "id": str(c.id),
            "name": c.name,
            "email": c.email,
            "city": c.city,
            "total_spent": float(c.total_spent or 0)
        } for c in customers],
        performance=SegmentPerformance(
            campaigns_run=campaigns_run,
            avg_read_rate=round(avg_read_rate, 4),
            avg_click_rate=round(avg_click_rate, 4),
            avg_order_rate=round(avg_order_rate, 4)
        )
    )


@router.put("/segments/{segment_id}", response_model=SegmentResponse)
def update_segment(segment_id: str, data: SegmentUpdate, db: Session = Depends(get_db)):
    segment = db.query(Segment).filter(Segment.id == segment_id).first()
    if not segment:
        raise HTTPException(status_code=404, detail="Segment not found")
    
    segment.filter_rules = data.filter_rules.model_dump()
    
    query = build_query(data.filter_rules.model_dump(), db)
    segment.customer_count = query.count()
    
    db.commit()
    db.refresh(segment)
    
    return SegmentResponse(
        id=str(segment.id),
        name=segment.name,
        nl_query=segment.nl_query,
        filter_rules=segment.filter_rules,
        customer_count=segment.customer_count,
        created_by=segment.created_by,
        created_at=segment.created_at
    )


@router.delete("/segments/{segment_id}")
def delete_segment(segment_id: str, db: Session = Depends(get_db)):
    segment = db.query(Segment).filter(Segment.id == segment_id).first()
    if not segment:
        raise HTTPException(status_code=404, detail="Segment not found")
    
    db.delete(segment)
    db.commit()
    
    return {"deleted": True}
