import sys
import os
import pytest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

from unittest.mock import MagicMock, AsyncMock, patch
from models.db import Customer
from agents.executor import (
    assign_variant,
    personalize,
    _age_matches,
    run_executor,
)


def test_age_matches_exact():
    assert _age_matches("26-35", "26-35") is True
    assert _age_matches("18-25", "18-25") is True


def test_age_matches_overlap():
    assert _age_matches("26-35", "26-42") is True
    assert _age_matches("36-45", "26-42") is True
    assert _age_matches("18-25", "26-42") is False


def test_age_matches_plus_range():
    assert _age_matches("45+", "45+") is True
    assert _age_matches("36-45", "45+") is False


def test_age_matches_invalid():
    assert _age_matches("", "26-35") is False
    assert _age_matches("26-35", "") is False


def test_assign_variant_international_priority():
    customer = MagicMock()
    customer.region = "international"
    customer.age_group = "26-35"

    variants = [
        {"id": "A", "targets": {"age_group": "26-35"}, "message": "Age match"},
        {"id": "B", "targets": {"region": "international"}, "message": "Intl variant"},
    ]

    result = assign_variant(customer, variants)
    assert result["id"] == "B"


def test_assign_variant_age_match():
    customer = MagicMock()
    customer.region = "india"
    customer.age_group = "18-25"

    variants = [
        {"id": "A", "targets": {"age_group": "26-35"}, "message": "Older"},
        {"id": "B", "targets": {"age_group": "18-25"}, "message": "Young"},
    ]

    result = assign_variant(customer, variants)
    assert result["id"] == "B"


def test_assign_variant_fallback():
    customer = MagicMock()
    customer.region = "india"
    customer.age_group = "45+"

    variants = [
        {"id": "A", "targets": {"age_group": "18-25"}, "message": "Young"},
        {"id": "B", "targets": {"age_group": "26-35"}, "message": "Mid"},
    ]

    result = assign_variant(customer, variants)
    assert result["id"] == "A"


def test_personalize_name_and_city():
    customer = MagicMock()
    customer.name = "Priya Sharma"
    customer.city = "Mumbai"

    result = personalize("Hi {name} from {city}!", customer)
    assert result == "Hi Priya from Mumbai!"


def test_personalize_empty_name():
    customer = MagicMock()
    customer.name = ""
    customer.city = "Mumbai"

    result = personalize("Hi {name}!", customer)
    assert result == "Hi there!"


@pytest.mark.asyncio
async def test_run_executor_assigns_variants(db_session):
    customer1 = Customer(
        name="Priya Sharma",
        email="priya@example.com",
        city="Mumbai",
        region="india",
        age_group="26-35",
        order_count=1,
    )
    customer2 = Customer(
        name="John Doe",
        email="john@example.com",
        city="New York",
        region="international",
        age_group="36-45",
        order_count=1,
    )
    db_session.add(customer1)
    db_session.add(customer2)
    db_session.commit()

    variants = [
        {"id": "A", "targets": {"age_group": "26-35"}, "message": "Hi {name}!"},
        {"id": "B", "targets": {"region": "international"}, "message": "Hello {name}!"},
    ]

    state = {
        "session_id": "test_session",
        "filter_rules": {"operator": "AND", "rules": []},
        "message_variants": variants,
        "channel": "whatsapp",
        "segment_name": "Test",
        "ai_reasoning": "Test reasoning",
        "trend_context": "- trend",
    }

    mock_publish = AsyncMock()

    with patch("agents.executor.publish", mock_publish):
        result = await run_executor(state, db_session)

    assert len(result["variant_assignments"]) == 2


@pytest.mark.asyncio
async def test_run_executor_proposal_ready_event(db_session):
    customer = Customer(
        name="Test User",
        email="test@example.com",
        region="india",
        order_count=1,
    )
    db_session.add(customer)
    db_session.commit()

    variants = [{"id": "A", "targets": {}, "message": "Test"}]

    state = {
        "session_id": "test_session",
        "filter_rules": {"operator": "AND", "rules": []},
        "message_variants": variants,
        "channel": "whatsapp",
        "segment_name": "Win-back segment",
        "ai_reasoning": "Test reasoning",
        "trend_context": "Raw tavily output",
        "trend_highlights": ["Linen edit trending"],
    }

    mock_publish = AsyncMock()

    with patch("agents.executor.publish", mock_publish):
        await run_executor(state, db_session)

    proposal_events = [
        c[0][1] for c in mock_publish.call_args_list
        if c[0][1].get("type") == "proposal_ready"
    ]

    assert len(proposal_events) == 1
    data = proposal_events[0]["data"]
    assert data["segment_name"] == "Win-back segment"
    assert data["trend_context"] == "Raw tavily output"
    assert data["reasoning"] == "Test reasoning"
