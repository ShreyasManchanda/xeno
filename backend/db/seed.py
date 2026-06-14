import os
import sys
import json
import random
from datetime import datetime, timedelta, date
from faker import Faker
from sqlalchemy.orm import Session

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.db import Base, Customer, Order, Segment, Campaign, Communication, CampaignLearning
from db.session import engine, SessionLocal
from services.segment_engine import build_query

fake = Faker()
random.seed(42)
Faker.seed(42)

CITIES_INDIA = ["Mumbai", "Delhi", "Bangalore", "Chennai", "Hyderabad", "Pune", "Kolkata", "Ahmedabad", "Jaipur", "Lucknow"]
CITIES_INTERNATIONAL = ["Dubai", "Singapore", "London", "Sydney", "New York", "Toronto", "Melbourne", "Kuala Lumpur"]
CATEGORIES = ["kurta", "western", "bridal", "saree", "accessories", "ethnic", "fusion"]
GENDERS = ["male", "female"]
AGE_GROUPS = ["18-25", "26-35", "36-45", "45+"]
SEASONS = ["summer", "winter", "festive"]
CHANNELS = ["whatsapp", "sms", "email"]
MESSAGE_STYLES = ["festive", "urgent", "emotional", "informational"]


def generate_customers(num_customers=200):
    customers = []
    for i in range(num_customers):
        is_international = i >= int(num_customers * 0.7)
        
        if is_international:
            city = random.choice(CITIES_INTERNATIONAL)
            region = "international"
        else:
            city = random.choice(CITIES_INDIA)
            region = "india"
        
        signup_date = fake.date_between(start_date=date(2022, 1, 1), end_date=date(2025, 12, 1))
        total_spent = round(random.uniform(0, 50000), 2)
        order_count = random.randint(0, 12) if total_spent > 0 else 0
        
        if order_count > 0:
            last_order_date = fake.date_between(start_date=signup_date, end_date=date.today())
        else:
            last_order_date = None
        
        num_categories = random.randint(1, 4)
        preferred_categories = random.sample(CATEGORIES, num_categories)
        
        customer = Customer(
            name=fake.name(),
            email=fake.email(),
            phone=f"+91{fake.msisdn()[3:13]}" if region == "india" else f"+{random.randint(1, 99)}{fake.msisdn()[4:14]}",
            city=city,
            region=region,
            gender=random.choice(GENDERS),
            age_group=random.choice(AGE_GROUPS),
            signup_date=signup_date,
            total_spent=total_spent,
            order_count=order_count,
            last_order_date=last_order_date,
            preferred_channel=random.choice(CHANNELS),
            preferred_categories=preferred_categories
        )
        customers.append(customer)
    
    return customers


def generate_orders(customers):
    orders = []
    for customer in customers:
        num_orders = customer.order_count
        for _ in range(num_orders):
            order_date = fake.date_between(start_date=customer.signup_date, end_date=date.today())
            amount = round(random.uniform(500, 15000), 2)
            
            month = order_date.month
            if month in [6, 7, 8, 9]:
                season = "summer"
            elif month in [11, 12, 1, 2]:
                season = "winter"
            else:
                season = "festive"
            
            num_items = random.randint(1, 4)
            items = []
            category_tags = set()
            for _ in range(num_items):
                cat = random.choice(customer.preferred_categories or CATEGORIES[:3])
                category_tags.add(cat)
                items.append({
                    "name": f"{cat.title()} {fake.word()}",
                    "category": cat,
                    "price": round(random.uniform(300, 5000), 2),
                    "qty": random.randint(1, 3)
                })
            
            order = Order(
                customer_id=customer.id,
                amount=amount,
                items=items,
                order_date=order_date,
                season=season,
                category_tags=list(category_tags)
            )
            orders.append(order)
    
    return orders


def generate_preseeded_learnings(num_learnings=5):
    learnings = []
    for i in range(num_learnings):
        learning = CampaignLearning(
            campaign_id=None,
            segment_description=random.choice([
                "High-value customers who bought bridal wear",
                "Customers inactive for 90+ days",
                "Summer collection enthusiasts in metro cities",
                "First-time buyers with high cart value",
                "Repeat customers interested in ethnic wear"
            ]),
            channel=random.choice(CHANNELS),
            message_style=random.choice(MESSAGE_STYLES),
            open_rate=round(random.uniform(0.35, 0.65), 4),
            click_rate=round(random.uniform(0.08, 0.25), 4),
            order_rate=round(random.uniform(0.02, 0.08), 4),
            customer_count=random.randint(50, 300)
        )
        learnings.append(learning)
    
    return learnings


def generate_prebuilt_segments(db: Session) -> list[Segment]:
    """Seed segments aligned with dashboard nudge patterns."""
    definitions = [
        {
            "name": "Inactive High-Value Customers",
            "filter_rules": {
                "operator": "AND",
                "rules": [
                    {"field": "total_spent", "op": "gte", "value": 15000},
                    {"field": "last_order_date", "op": "lt_days_ago", "value": 90},
                ],
            },
            "created_by": "seed",
        },
        {
            "name": "Recent Kurta Buyers",
            "filter_rules": {
                "operator": "AND",
                "rules": [
                    {"field": "preferred_categories", "op": "contains", "value": ["kurta"]},
                    {"field": "last_order_date", "op": "gt_days_ago", "value": 60},
                ],
            },
            "created_by": "seed",
        },
        {
            "name": "International Customers",
            "filter_rules": {
                "operator": "AND",
                "rules": [{"field": "region", "op": "eq", "value": "international"}],
            },
            "created_by": "seed",
        },
    ]

    segments = []
    for definition in definitions:
        count = build_query(definition["filter_rules"], db).count()
        segments.append(
            Segment(
                name=definition["name"],
                filter_rules=definition["filter_rules"],
                customer_count=count,
                created_by=definition["created_by"],
            )
        )
    return segments


def seed_database():
    db = SessionLocal()
    
    try:
        Base.metadata.create_all(bind=engine)
        
        existing = db.query(Customer).first()
        if existing:
            print("Database already seeded. Skipping...")
            return
        
        print("Generating customers...")
        customers = generate_customers(200)
        db.add_all(customers)
        db.commit()
        print(f"Created {len(customers)} customers")
        
        print("Generating orders...")
        orders = generate_orders(customers)
        db.add_all(orders)
        db.commit()
        print(f"Created {len(orders)} orders")

        print("Generating pre-built segments...")
        segments = generate_prebuilt_segments(db)
        db.add_all(segments)
        db.commit()
        print(f"Created {len(segments)} pre-built segments")

        print("Generating pre-seeded learnings...")
        learnings = generate_preseeded_learnings(5)
        for learning in learnings:
            db.add(learning)
        db.commit()
        print(f"Created {len(learnings)} pre-seeded learnings")
        
        print("\nDatabase seeding complete!")
        print(f"  - Customers: {len(customers)}")
        print(f"  - Orders: {len(orders)}")
        print(f"  - Pre-built segments: {len(segments)}")
        print(f"  - Pre-seeded learnings: {len(learnings)}")
        
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
