import sys
import os
import pytest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

from unittest.mock import MagicMock, patch, AsyncMock
from models.db import Customer


ANALYST_GEMINI_RESPONSE = {
    "segment_name": "High value customers",
    "reasoning": "Targeting customers with high spend.",
    "filter_rules": {
        "operator": "AND",
        "rules": [{"field": "total_spent", "op": "gt", "value": 10000}],
    },
}


def test_analyst_returns_filter_rules(db_session):
    from agents.analyst import run_analyst

    customer = Customer(
        name="Test User",
        email="test@example.com",
        total_spent=15000,
        order_count=2,
    )
    db_session.add(customer)
    db_session.commit()

    state = {
        "goal": "Find high value customers",
        "session_id": "test_session",
        "season_india": "summer",
        "season_intl": "winter",
    }

    with patch("agents.analyst.call_gemini", new_callable=AsyncMock, return_value=ANALYST_GEMINI_RESPONSE):
        with patch("agents.analyst.publish", new_callable=AsyncMock):
            import asyncio
            result = asyncio.run(run_analyst(state, db_session))

    assert "filter_rules" in result
    assert "customer_count" in result
    assert "segment_name" in result
    assert result["customer_count"] >= 1


def test_analyst_handles_gemini_failure(db_session):
    from agents.analyst import run_analyst

    customer = Customer(name="Test User", email="test@example.com", order_count=1)
    db_session.add(customer)
    db_session.commit()

    state = {
        "goal": "Test goal",
        "session_id": "test_session",
        "season_india": "summer",
        "season_intl": "winter",
    }

    with patch("agents.analyst.call_gemini", new_callable=AsyncMock, side_effect=Exception("API error")):
        with patch("agents.analyst.publish", new_callable=AsyncMock):
            import asyncio
            result = asyncio.run(run_analyst(state, db_session))

    assert result["filter_rules"]["operator"] == "AND"
    assert len(result["filter_rules"]["rules"]) >= 1


def test_analyst_skips_sse_for_preview(db_session):
    from agents.analyst import run_analyst

    mock_publish = AsyncMock()

    state = {
        "goal": "Test goal",
        "session_id": "preview",
        "season_india": "summer",
        "season_intl": "winter",
    }

    with patch("agents.analyst.call_gemini", new_callable=AsyncMock, return_value=ANALYST_GEMINI_RESPONSE):
        with patch("agents.analyst.publish", mock_publish):
            import asyncio
            asyncio.run(run_analyst(state, db_session))

    mock_publish.assert_not_called()


@pytest.mark.asyncio
async def test_analyst_publishes_events(db_session):
    from agents.analyst import run_analyst

    mock_publish = AsyncMock()

    customer = Customer(name="Test User", email="test@example.com", order_count=1)
    db_session.add(customer)
    db_session.commit()

    state = {
        "goal": "Test goal",
        "session_id": "test_session",
        "season_india": "summer",
        "season_intl": "winter",
    }

    with patch("agents.analyst.call_gemini", new_callable=AsyncMock, return_value=ANALYST_GEMINI_RESPONSE):
        with patch("agents.analyst.publish", mock_publish):
            await run_analyst(state, db_session)

    assert mock_publish.call_count >= 2
    calls = [c[0][1] for c in mock_publish.call_args_list]
    assert any(c.get("type") == "agent_start" for c in calls)
    assert any(c.get("type") == "agent_complete" for c in calls)


def test_analyst_sample_customers(db_session):
    from agents.analyst import run_analyst

    for i in range(10):
        db_session.add(
            Customer(
                name=f"Customer {i}",
                email=f"customer{i}@example.com",
                total_spent=10000 + i * 1000,
                order_count=1,
            )
        )
    db_session.commit()

    state = {
        "goal": "Test goal",
        "session_id": "test_session",
        "season_india": "summer",
        "season_intl": "winter",
    }

    with patch("agents.analyst.call_gemini", new_callable=AsyncMock, return_value=ANALYST_GEMINI_RESPONSE):
        with patch("agents.analyst.publish", new_callable=AsyncMock):
            import asyncio
            result = asyncio.run(run_analyst(state, db_session))

    assert "sample_customers" in result
    assert len(result["sample_customers"]) <= 5
