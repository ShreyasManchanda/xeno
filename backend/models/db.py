from sqlalchemy import Column, String, Integer, Numeric, Date, DateTime, Text, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()


class Customer(Base):
    __tablename__ = "customers"

    id = Column(UUID(as_uuid=False), primary_key=True, server_default=text("gen_random_uuid()"))
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True)
    phone = Column(String(20))
    city = Column(String(50))
    region = Column(String(20))
    gender = Column(String(10))
    age_group = Column(String(10))
    signup_date = Column(Date)
    total_spent = Column(Numeric(10, 2), default=0)
    order_count = Column(Integer, default=0)
    last_order_date = Column(Date)
    preferred_channel = Column(String(20), default="whatsapp")
    preferred_categories = Column(ARRAY(Text))
    created_at = Column(DateTime(timezone=True), server_default=text("NOW()"))

    orders = relationship("Order", back_populates="customer", cascade="all, delete-orphan")
    communications = relationship("Communication", back_populates="customer", cascade="all, delete-orphan")


class Order(Base):
    __tablename__ = "orders"

    id = Column(UUID(as_uuid=False), primary_key=True, server_default=text("gen_random_uuid()"))
    customer_id = Column(UUID(as_uuid=False), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    amount = Column(Numeric(10, 2))
    items = Column(JSONB)
    order_date = Column(Date)
    season = Column(String(20))
    category_tags = Column(ARRAY(Text))
    created_at = Column(DateTime(timezone=True), server_default=text("NOW()"))

    customer = relationship("Customer", back_populates="orders")


class Segment(Base):
    __tablename__ = "segments"

    id = Column(UUID(as_uuid=False), primary_key=True, server_default=text("gen_random_uuid()"))
    name = Column(String(100))
    nl_query = Column(Text)
    filter_rules = Column(JSONB)
    customer_count = Column(Integer)
    created_by = Column(String(10))
    created_at = Column(DateTime(timezone=True), server_default=text("NOW()"))

    campaigns = relationship("Campaign", back_populates="segment", cascade="all, delete-orphan")


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(UUID(as_uuid=False), primary_key=True, server_default=text("gen_random_uuid()"))
    name = Column(String(150))
    goal = Column(Text)
    segment_id = Column(UUID(as_uuid=False), ForeignKey("segments.id"))
    channel = Column(String(20))
    status = Column(String(20), default="draft")
    message_variants = Column(JSONB)
    ai_reasoning = Column(Text)
    trend_context = Column(Text)
    insight_summary = Column(Text)
    launched_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=text("NOW()"))

    segment = relationship("Segment", back_populates="campaigns")
    communications = relationship("Communication", back_populates="campaign", cascade="all, delete-orphan")
    learnings = relationship("CampaignLearning", back_populates="campaign", uselist=False)


class Communication(Base):
    __tablename__ = "communications"

    id = Column(UUID(as_uuid=False), primary_key=True, server_default=text("gen_random_uuid()"))
    campaign_id = Column(UUID(as_uuid=False), ForeignKey("campaigns.id"))
    customer_id = Column(UUID(as_uuid=False), ForeignKey("customers.id"))
    variant_id = Column(String(5))
    personalized_message = Column(Text)
    channel = Column(String(20))
    status = Column(String(30), default="queued")
    sent_at = Column(DateTime(timezone=True))
    delivered_at = Column(DateTime(timezone=True))
    read_at = Column(DateTime(timezone=True))
    clicked_at = Column(DateTime(timezone=True))
    order_attributed_at = Column(DateTime(timezone=True))
    attributed_revenue = Column(Numeric(10, 2))
    created_at = Column(DateTime(timezone=True), server_default=text("NOW()"))

    campaign = relationship("Campaign", back_populates="communications")
    customer = relationship("Customer", back_populates="communications")


class CampaignLearning(Base):
    __tablename__ = "campaign_learnings"

    id = Column(UUID(as_uuid=False), primary_key=True, server_default=text("gen_random_uuid()"))
    campaign_id = Column(UUID(as_uuid=False), ForeignKey("campaigns.id"))
    segment_description = Column(Text)
    channel = Column(String(20))
    message_style = Column(String(30))
    open_rate = Column(Numeric(5, 4))
    click_rate = Column(Numeric(5, 4))
    order_rate = Column(Numeric(5, 4))
    customer_count = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=text("NOW()"))

    campaign = relationship("Campaign", back_populates="learnings")
