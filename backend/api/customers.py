from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime, date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from db.session import get_db
from models.db import Customer, Order


class CustomerResponse(BaseModel):
    id: str
    name: str
    email: Optional[str]
    phone: Optional[str]
    city: Optional[str]
    region: Optional[str]
    gender: Optional[str]
    age_group: Optional[str]
    signup_date: Optional[date]
    total_spent: float
    order_count: int
    last_order_date: Optional[date]
    preferred_channel: str
    preferred_categories: Optional[List[str]]
    created_at: datetime

    class Config:
        from_attributes = True


class OrderItem(BaseModel):
    name: str
    category: str
    price: float
    qty: int


class OrderResponse(BaseModel):
    id: str
    amount: float
    items: List[OrderItem]
    order_date: Optional[date]
    season: Optional[str]
    category_tags: Optional[List[str]]

    class Config:
        from_attributes = True


class CustomerDetailResponse(BaseModel):
    customer: CustomerResponse
    orders: List[OrderResponse]
    campaign_history: List[dict]


class PaginatedCustomersResponse(BaseModel):
    customers: List[CustomerResponse]
    total: int
    page: int
    limit: int


router = APIRouter()


@router.get("/customers", response_model=PaginatedCustomersResponse)
def list_customers(
    search: Optional[str] = Query(None),
    city: Optional[str] = Query(None),
    age_group: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(Customer)
    
    if search:
        query = query.filter(
            (Customer.name.ilike(f"%{search}%")) |
            (Customer.email.ilike(f"%{search}%"))
        )
    
    if city:
        query = query.filter(Customer.city == city)
    
    if age_group:
        query = query.filter(Customer.age_group == age_group)
    
    total = query.count()
    
    customers = query.order_by(desc(Customer.created_at))\
        .offset((page - 1) * limit)\
        .limit(limit)\
        .all()
    
    return PaginatedCustomersResponse(
        customers=[CustomerResponse(
            id=str(c.id),
            name=c.name,
            email=c.email,
            phone=c.phone,
            city=c.city,
            region=c.region,
            gender=c.gender,
            age_group=c.age_group,
            signup_date=c.signup_date,
            total_spent=float(c.total_spent or 0),
            order_count=c.order_count or 0,
            last_order_date=c.last_order_date,
            preferred_channel=c.preferred_channel or "whatsapp",
            preferred_categories=c.preferred_categories or [],
            created_at=c.created_at
        ) for c in customers],
        total=total,
        page=page,
        limit=limit
    )


@router.get("/customers/{customer_id}", response_model=CustomerDetailResponse)
def get_customer(customer_id: str, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Customer not found")
    
    orders = db.query(Order).filter(Order.customer_id == customer_id)\
        .order_by(desc(Order.order_date))\
        .all()
    
    from models.db import Communication, Campaign
    comms = db.query(Communication, Campaign)\
        .join(Campaign, Communication.campaign_id == Campaign.id)\
        .filter(Communication.customer_id == customer_id)\
        .order_by(desc(Communication.created_at))\
        .limit(10)\
        .all()
    
    campaign_history = []
    for comm, camp in comms:
        campaign_history.append({
            "campaign_id": str(camp.id),
            "campaign_name": camp.name,
            "channel": comm.channel,
            "status": comm.status,
            "sent_at": comm.sent_at.isoformat() if comm.sent_at else None,
            "variant_id": comm.variant_id
        })
    
    return CustomerDetailResponse(
        customer=CustomerResponse(
            id=str(customer.id),
            name=customer.name,
            email=customer.email,
            phone=customer.phone,
            city=customer.city,
            region=customer.region,
            gender=customer.gender,
            age_group=customer.age_group,
            signup_date=customer.signup_date,
            total_spent=float(customer.total_spent or 0),
            order_count=customer.order_count or 0,
            last_order_date=customer.last_order_date,
            preferred_channel=customer.preferred_channel or "whatsapp",
            preferred_categories=customer.preferred_categories or [],
            created_at=customer.created_at
        ),
        orders=[OrderResponse(
            id=str(o.id),
            amount=float(o.amount or 0),
            items=[OrderItem(**item) for item in (o.items or [])],
            order_date=o.order_date,
            season=o.season,
            category_tags=o.category_tags or []
        ) for o in orders],
        campaign_history=campaign_history
    )
