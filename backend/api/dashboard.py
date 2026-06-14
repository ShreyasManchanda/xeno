from typing import Optional
from pydantic import BaseModel
from datetime import date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from models.db import Customer, Segment, Campaign, Communication
from services.segment_engine import build_query


class DashboardStats(BaseModel):
    total_customers: int
    active_segments: int
    campaigns_run: int
    avg_read_rate: float


class Nudge(BaseModel):
    title: str
    body: str
    cta: str
    segment_id: Optional[str] = None
    prefill_goal: Optional[str] = None


class DashboardResponse(BaseModel):
    kpis: DashboardStats
    nudges: list[Nudge]


def get_dashboard_stats(db: Session) -> DashboardStats:
    total_customers = db.query(func.count(Customer.id)).scalar() or 0
    active_segments = db.query(func.count(Segment.id)).scalar() or 0
    campaigns_run = db.query(func.count(Campaign.id)).filter(
        Campaign.status.in_(["completed", "running"])
    ).scalar() or 0

    total_read = db.query(func.count(Communication.id)).filter(
        Communication.status.in_(["read", "clicked", "order_attributed"])
    ).scalar() or 0

    total_delivered = db.query(func.count(Communication.id)).filter(
        Communication.status.in_(["delivered", "read", "clicked", "order_attributed"])
    ).scalar() or 0

    avg_read_rate = total_read / total_delivered if total_delivered > 0 else 0.0

    return DashboardStats(
        total_customers=total_customers,
        active_segments=active_segments,
        campaigns_run=campaigns_run,
        avg_read_rate=round(avg_read_rate, 4),
    )


def get_dashboard_nudges(db: Session) -> list[Nudge]:
    nudges: list[Nudge] = []
    cutoff = date.today() - timedelta(days=90)

    high_value_lapsed = build_query(
        {
            "operator": "AND",
            "rules": [
                {"field": "total_spent", "op": "gte", "value": 15000},
                {"field": "last_order_date", "op": "lt_days_ago", "value": 90},
            ],
        },
        db,
    ).count()

    if high_value_lapsed > 0:
        nudges.append(
            Nudge(
                title="Inactive High-Value Customers",
                body=f"{high_value_lapsed} customers spent over ₹15,000 but haven't ordered in 90+ days. Win them back with a personalized offer.",
                cta="Create Segment",
                prefill_goal="Customers who spent over ₹15,000 but haven't ordered in 90 days",
            )
        )

    kurta_recent = build_query(
        {
            "operator": "AND",
            "rules": [
                {"field": "preferred_categories", "op": "contains", "value": ["kurta"]},
                {"field": "last_order_date", "op": "gt_days_ago", "value": 60},
            ],
        },
        db,
    ).count()

    if kurta_recent > 0:
        nudges.append(
            Nudge(
                title="Repeat Purchase Opportunity",
                body=f"{kurta_recent} customers bought kurta in the last 60 days. Suggest matching accessories from the new collection.",
                cta="Launch Campaign",
                prefill_goal="Customers who bought kurta in the last 60 days — suggest matching accessories",
            )
        )

    international = build_query(
        {
            "operator": "AND",
            "rules": [{"field": "region", "op": "eq", "value": "international"}],
        },
        db,
    ).count()

    if international > 0:
        intl_segment = (
            db.query(Segment)
            .filter(Segment.name == "International Customers")
            .first()
        )
        nudges.append(
            Nudge(
                title="International Audience",
                body=f"{international} international customers in your base. Highlight global shipping in your next campaign.",
                cta="Launch Campaign",
                segment_id=str(intl_segment.id) if intl_segment else None,
                prefill_goal="International customers — highlight global shipping and new arrivals",
            )
        )

    return nudges[:3]


from fastapi import APIRouter, Depends
from db.session import get_db

router = APIRouter()


@router.get("/dashboard/stats", response_model=DashboardResponse)
def get_dashboard(db: Session = Depends(get_db)):
    stats = get_dashboard_stats(db)
    nudges = get_dashboard_nudges(db)

    return DashboardResponse(kpis=stats, nudges=nudges)
