# backend/models/__init__.py
from .db import Base, Customer, Order, Segment, Campaign, Communication, CampaignLearning

__all__ = ["Base", "Customer", "Order", "Segment", "Campaign", "Communication", "CampaignLearning"]
