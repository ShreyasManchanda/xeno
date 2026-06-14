import sys
import os
import pytest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

from unittest.mock import patch, AsyncMock


STRATEGIST_GEMINI_RESPONSE = {
    "recommended_channel": "whatsapp",
    "reasoning": "WhatsApp fits this segment.",
    "channel_reasoning": "Highest read rates.",
    "message_style": "informational",
    "trend_highlights": ["Summer trends ready"],
    "predicted_open_rate": "32-40%",
    "variants": [
        {"id": "A", "targets": {"age_group": "18-25"}, "message": "Test A"},
        {"id": "B", "targets": {"age_group": "26-35"}, "message": "Test B"},
        {"id": "C", "targets": {"region": "international"}, "message": "Test C"},
    ],
}


def test_strategist_returns_variants(db_session):
    from agents.strategist import run_strategist

    state = {
        "goal": "Test campaign",
        "session_id": "test_session",
        "season_india": "summer",
        "season_intl": "winter",
        "customer_count": 100,
        "segment_name": "Test segment",
        "filter_rules": {"operator": "AND", "rules": []},
    }

    with patch("agents.strategist.call_gemini", new_callable=AsyncMock, return_value=STRATEGIST_GEMINI_RESPONSE):
        with patch("agents.strategist._search_trends", new_callable=AsyncMock, return_value=["Trend snippet"]):
            with patch("agents.strategist.publish", new_callable=AsyncMock):
                with patch("agents.strategist.get_recent_learnings", return_value=[]):
                    with patch("agents.strategist.format_learnings_for_prompt", return_value=""):
                        import asyncio
                        result = asyncio.run(run_strategist(state, db_session))

    assert "message_variants" in result
    assert result["channel"] == "whatsapp"
    assert result["trend_context"]


def test_strategist_uses_tavily(db_session):
    from agents.strategist import run_strategist

    mock_search = AsyncMock(return_value=["Trend 1", "Trend 2"])

    state = {
        "goal": "Test",
        "session_id": "test",
        "season_india": "summer",
        "season_intl": "winter",
        "customer_count": 100,
        "segment_name": "Test",
        "filter_rules": {},
    }

    with patch("agents.strategist.call_gemini", new_callable=AsyncMock, return_value=STRATEGIST_GEMINI_RESPONSE):
        with patch("agents.strategist._search_trends", mock_search):
            with patch("agents.strategist.publish", new_callable=AsyncMock):
                with patch("agents.strategist.get_recent_learnings", return_value=[]):
                    with patch("agents.strategist.format_learnings_for_prompt", return_value=""):
                        import asyncio
                        result = asyncio.run(run_strategist(state, db_session))

    mock_search.assert_called_once()
    assert "trend_highlights" in result


def test_strategist_handles_tavily_failure(db_session):
    from agents.strategist import run_strategist

    state = {
        "goal": "Test",
        "session_id": "test",
        "season_india": "summer",
        "season_intl": "winter",
        "customer_count": 100,
        "segment_name": "Test",
        "filter_rules": {},
    }

    with patch("agents.strategist.call_gemini", new_callable=AsyncMock, return_value=STRATEGIST_GEMINI_RESPONSE):
        with patch("agents.strategist._search_trends", new_callable=AsyncMock, return_value=[]):
            with patch("agents.strategist.publish", new_callable=AsyncMock):
                with patch("agents.strategist.get_recent_learnings", return_value=[]):
                    with patch("agents.strategist.format_learnings_for_prompt", return_value=""):
                        import asyncio
                        result = asyncio.run(run_strategist(state, db_session))

    assert "trend_highlights" in result


def test_strategist_empty_variants_uses_fallback(db_session):
    from agents.strategist import run_strategist

    empty_response = {**STRATEGIST_GEMINI_RESPONSE, "variants": []}

    state = {
        "goal": "Test",
        "session_id": "test",
        "season_india": "summer",
        "season_intl": "winter",
        "customer_count": 100,
        "segment_name": "Test",
        "filter_rules": {},
    }

    with patch("agents.strategist.call_gemini", new_callable=AsyncMock, return_value=empty_response):
        with patch("agents.strategist._search_trends", new_callable=AsyncMock, return_value=[]):
            with patch("agents.strategist.publish", new_callable=AsyncMock):
                with patch("agents.strategist.get_recent_learnings", return_value=[]):
                    with patch("agents.strategist.format_learnings_for_prompt", return_value=""):
                        import asyncio
                        result = asyncio.run(run_strategist(state, db_session))

    assert len(result["message_variants"]) >= 3


@pytest.mark.asyncio
async def test_strategist_publishes_events(db_session):
    from agents.strategist import run_strategist

    mock_publish = AsyncMock()

    state = {
        "goal": "Test",
        "session_id": "test",
        "season_india": "summer",
        "season_intl": "winter",
        "customer_count": 100,
        "segment_name": "Test",
        "filter_rules": {},
    }

    with patch("agents.strategist.call_gemini", new_callable=AsyncMock, return_value=STRATEGIST_GEMINI_RESPONSE):
        with patch("agents.strategist._search_trends", new_callable=AsyncMock, return_value=["trend"]):
            with patch("agents.strategist.publish", mock_publish):
                with patch("agents.strategist.get_recent_learnings", return_value=[]):
                    with patch("agents.strategist.format_learnings_for_prompt", return_value=""):
                        await run_strategist(state, db_session)

    assert mock_publish.call_count >= 2
