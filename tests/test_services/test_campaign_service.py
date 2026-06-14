import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from models.db import Customer, Communication, Campaign, Segment
from agents.executor import assign_variant, personalize


def test_assign_variant_international_customer():
    customer = MagicMock()
    customer.region = "international"
    customer.age_group = "26-35"
    
    variants = [
        {"id": "A", "targets": {"age_group": "18-25"}, "message": "Test A"},
        {"id": "B", "targets": {"region": "international"}, "message": "Test B"},
        {"id": "C", "targets": {"age_group": "36-45"}, "message": "Test C"}
    ]
    
    result = assign_variant(customer, variants)
    assert result["id"] == "B"


def test_assign_variant_age_group_match():
    customer = MagicMock()
    customer.region = "india"
    customer.age_group = "26-35"
    
    variants = [
        {"id": "A", "targets": {"age_group": "18-25"}, "message": "Test A"},
        {"id": "B", "targets": {"age_group": "26-42"}, "message": "Test B"},
        {"id": "C", "targets": {"region": "international"}, "message": "Test C"}
    ]
    
    result = assign_variant(customer, variants)
    assert result["id"] == "B"


def test_assign_variant_fallback():
    customer = MagicMock()
    customer.region = "india"
    customer.age_group = "45+"
    
    variants = [
        {"id": "A", "targets": {"age_group": "18-25"}, "message": "Test A"},
        {"id": "B", "targets": {"age_group": "26-35"}, "message": "Test B"}
    ]
    
    result = assign_variant(customer, variants)
    assert result["id"] == "A"


def test_assign_variant_empty_variants():
    customer = MagicMock()
    customer.region = "india"
    customer.age_group = "26-35"
    
    result = assign_variant(customer, [])
    assert result["id"] == "A"


def test_personalize_basic():
    variant = {"message": "Hi {name}, welcome to {city}!"}
    customer = MagicMock()
    customer.name = "Priya Sharma"
    customer.city = "Mumbai"
    
    result = personalize(variant["message"], customer)
    assert result == "Hi Priya, welcome to Mumbai!"


def test_personalize_no_city():
    variant = {"message": "Hi {name}, check this out!"}
    customer = MagicMock()
    customer.name = "Amit Patel"
    customer.city = None
    
    result = personalize(variant["message"], customer)
    assert result == "Hi Amit, check this out!"


def test_personalize_missing_placeholders():
    variant = {"message": "Hello there, special offer!"}
    customer = MagicMock()
    customer.name = "Priya"
    customer.city = "Mumbai"
    
    result = personalize(variant["message"], customer)
    assert result == "Hello there, special offer!"


def test_infer_style_from_module():
    from services.learnings import infer_style
    
    festive = [{"message": "Celebrate Diwali with our new collection!"}]
    assert infer_style(festive) == "festive"
    
    urgent = [{"message": "Limited time offer! Ends in 24 hours!"}]
    assert infer_style(urgent) == "urgent"
    
    emotional = [{"message": "We miss you! Come back and see what's new."}]
    assert infer_style(emotional) == "emotional"
    
    informational = [{"message": "New arrivals available now."}]
    assert infer_style(informational) == "informational"


@pytest.mark.asyncio
async def test_send_to_channel_success(db_session):
    from services.campaign_service import send_payload_to_channel
    
    mock_client = AsyncMock()
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_client.post = AsyncMock(return_value=mock_response)
    
    data = {
        "communication_id": "test-comm-id",
        "email": "test@example.com",
        "phone": "+919999999999",
        "message": "Test message",
        "channel": "whatsapp"
    }
    
    with patch.dict(os.environ, {"CHANNEL_SERVICE_URL": "http://localhost:8001"}):
        result = await send_payload_to_channel(data, mock_client)
    
    assert result == True


@pytest.mark.asyncio
async def test_send_to_channel_failure(db_session):
    from services.campaign_service import send_payload_to_channel
    
    mock_client = AsyncMock()
    mock_client.post = AsyncMock(side_effect=Exception("Connection failed"))
    
    data = {
        "communication_id": "test-comm-id-2",
        "email": "test2@example.com",
        "phone": "+919999999998",
        "message": "Test message",
        "channel": "whatsapp"
    }
    
    with patch.dict(os.environ, {"CHANNEL_SERVICE_URL": "http://localhost:8001"}):
        result = await send_payload_to_channel(data, mock_client)
    
    assert result == False
