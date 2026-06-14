from typing import List, Optional
from pydantic import BaseModel
from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from db.session import get_db
from models.db import Customer, Order


class OrderItemIn(BaseModel):
    name: str
    category: str
    price: float
    qty: int


class OrderIn(BaseModel):
    customer_email: str
    amount: float
    items: List[OrderItemIn]
    order_date: date
    season: Optional[str] = None


class CustomerIn(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    city: Optional[str] = None
    region: Optional[str] = None
    gender: Optional[str] = None
    age_group: Optional[str] = None
    signup_date: Optional[date] = None
    total_spent: Optional[float] = None
    order_count: Optional[int] = None
    last_order_date: Optional[date] = None
    preferred_channel: Optional[str] = None
    preferred_categories: Optional[List[str]] = None


class IngestPayload(BaseModel):
    customers: List[CustomerIn]
    orders: List[OrderIn]


class IngestResponse(BaseModel):
    customers_upserted: int
    orders_inserted: int
    errors: List[str]


router = APIRouter()


@router.post("/ingest", response_model=IngestResponse)
def ingest_data(payload: IngestPayload, db: Session = Depends(get_db)):
    customers_upserted = 0
    orders_inserted = 0
    errors = []
    
    customer_email_to_id = {}
    
    for c in payload.customers:
        if not c.email:
            errors.append(f"Customer '{c.name}' missing email - skipped")
            continue
        
        existing = db.query(Customer).filter(Customer.email == c.email).first()
        
        if existing:
            if c.total_spent is not None:
                existing.total_spent = c.total_spent
            if c.order_count is not None:
                existing.order_count = c.order_count
            if c.last_order_date is not None:
                existing.last_order_date = c.last_order_date
            if c.preferred_categories is not None:
                existing.preferred_categories = c.preferred_categories
            customer_email_to_id[c.email] = existing.id
        else:
            new_customer = Customer(
                name=c.name,
                email=c.email,
                phone=c.phone,
                city=c.city,
                region=c.region or "india",
                gender=c.gender,
                age_group=c.age_group,
                signup_date=c.signup_date,
                total_spent=c.total_spent or 0,
                order_count=c.order_count or 0,
                last_order_date=c.last_order_date,
                preferred_channel=c.preferred_channel or "whatsapp",
                preferred_categories=c.preferred_categories or []
            )
            db.add(new_customer)
            db.flush()
            customer_email_to_id[c.email] = new_customer.id
        
        customers_upserted += 1
    
    for o in payload.orders:
        customer_id = customer_email_to_id.get(o.customer_email)
        if not customer_id:
            existing_customer = db.query(Customer).filter(Customer.email == o.customer_email).first()
            if existing_customer:
                customer_id = existing_customer.id
            else:
                errors.append(f"Order customer '{o.customer_email}' not found - skipped")
                continue
        
        category_tags = list(set(item.category for item in o.items))
        
        new_order = Order(
            customer_id=customer_id,
            amount=o.amount,
            items=[item.model_dump() for item in o.items],
            order_date=o.order_date,
            season=o.season,
            category_tags=category_tags
        )
        db.add(new_order)
        orders_inserted += 1
    
    db.commit()
    
    return IngestResponse(
        customers_upserted=customers_upserted,
        orders_inserted=orders_inserted,
        errors=errors
    )
