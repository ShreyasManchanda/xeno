"""
CampaignStrategist node — researches real-time fashion trends via Tavily,
then uses Gemini to propose channel, message style, and 3-4 personalised
message variants targeting different customer profiles.
"""
import os
from tavily import AsyncTavilyClient
from services.sse_bus import publish
from services.learnings import get_recent_learnings, format_learnings_for_prompt
from services.gemini import call_gemini
from services.trend_utils import (
    normalize_trend_highlights,
    normalize_variant_targets,
    tavily_result_to_snippet,
)

STRATEGIST_SYSTEM = """
You are the Campaign Strategist for Tana & Co., an Indian D2C ethnic and
fusion wear brand. You combine trend intelligence with customer segment data
to propose the channel, tone, and message variants most likely to convert.

BRAND VOICE:
Tana & Co. is warm, personal, and fashion-forward. Messages feel like they
come from a stylish friend, not a brand. Be specific — reference what is
trending, what is in season, what is new. Avoid: "check it out", "don't miss
out", "exciting offer", "click here", "shop now". These are banned phrases.

CHANNEL SELECTION LOGIC:
  whatsapp   Default. Best for re-engagement, personal tone, high read rates.
             Keep messages under 300 characters including placeholders.
  sms        Only for urgent, time-sensitive offers. Max 160 characters. Rare.
  email      Story-driven: new collection launches, lookbooks, brand moments.
             Max 500 characters. Use when the goal needs more than a sentence.
  If past campaign data shows a channel clearly outperforming, follow the data.

MESSAGE STYLE — pick exactly one:
  festive      Occasion-driven, celebratory, warm.
  urgent       Scarcity or deadline. Specific, never vague.
  emotional    Personal, miss-you energy. Builds connection before the ask.
  informational  Discovery-led, product-forward, no pressure.
  Match style to goal:
    re-engagement → emotional  |  new drop → informational or festive
    flash offer → urgent       |  seasonal push → festive or informational

VARIANT TARGETING — always create 3 or 4 variants:
  A  Young India (18-25)   Casual, trend-aware, emoji welcome
  B  Mid India (26-35)     Quality and occasion-led, slightly more refined
  C  Mature India (36-45 or 45+)  Include when segment likely has older customers.
  D  International         Always include. Mention global shipping.

Use ONLY these age_group values in targets: "18-25", "26-35", "36-45", "45+".

TEMPLATE PLACEHOLDERS:
  {name}   Customer's first name. Every message must include {name}.
  {city}   Customer's city. Use when it adds warmth.

TREND HIGHLIGHTS — array of exactly 2-3 strings:
  Each string is ONE plain-English sentence (max 120 characters).
  No markdown, no asterisks, no hashtags, no URLs, no page titles.
  Example: "Breathable linen kurta sets are trending for Indian summer wear."

OUTPUT RULES:
1. Return ONLY a valid JSON object. Escape quotes inside strings properly.
2. Required top-level fields:
     reasoning, recommended_channel, channel_reasoning, message_style,
     trend_highlights (array of 2-3 strings), predicted_open_rate, variants (3-4)
3. Each variant: id ("A"|"B"|"C"|"D"), targets (age_group and/or region), message
""".strip()


def _fallback_variants(season_india: str, goal: str = "campaign") -> list:
    return [
        {
            "id": "A",
            "targets": {"age_group": "18-25", "region": "india"},
            "message": f"Hey {{name}}, exciting new {season_india} styles just dropped at Tana & Co.! Discover fresh ethnic and fusion wear perfect for the season.",
        },
        {
            "id": "B",
            "targets": {"age_group": "26-35", "region": "india"},
            "message": f"Hi {{name}}, our {season_india} collection is live! We've handpicked beautiful pieces that blend tradition with modern style.",
        },
        {
            "id": "C",
            "targets": {"age_group": "36-45", "region": "india"},
            "message": f"Hello {{name}}, we thought you'd love our new {season_india} arrivals. Elegant designs crafted with care, perfect for you.",
        },
        {
            "id": "D",
            "targets": {"region": "international"},
            "message": f"Hi {{name}} from Tana & Co.! Our {season_india} collection is here, and we ship worldwide. Explore Indian elegance from wherever you are!",
        },
    ]


async def _search_trends(query: str) -> list[str]:
    try:
        client = AsyncTavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
        result = await client.search(query=query, max_results=5)
        snippets = [
            tavily_result_to_snippet(r)
            for r in result.get("results", [])
            if tavily_result_to_snippet(r)
        ]
        return snippets
    except Exception:
        return []


async def run_strategist(state: dict, db) -> dict:
    goal = state.get("goal", "")
    session_id = state.get("session_id", "")
    season_india = state.get("season_india", "summer")
    season_intl = state.get("season_intl", "winter")
    customer_count = state.get("customer_count", 0)
    segment_name = state.get("segment_name", "Target segment")

    await publish(
        session_id,
        {
            "type": "agent_start",
            "agent": "strategist",
            "message": f"Searching {season_india} fashion trends...",
        },
    )

    trend_query = f"India fashion trends {season_india} 2026 ethnic wear D2C"
    trend_snippets = await _search_trends(trend_query)
    trend_context_raw = (
        "\n".join(f"- {t}" for t in trend_snippets) if trend_snippets else "No trend data available."
    )

    if trend_snippets:
        await publish(
            session_id,
            {
                "type": "agent_progress",
                "agent": "strategist",
                "message": f"Found {len(trend_snippets)} trend signals from the web",
            },
        )

    learnings = get_recent_learnings(db, limit=5)
    learnings_context = format_learnings_for_prompt(learnings)

    user_prompt = f"""Campaign goal: {goal}

Target segment: {segment_name} ({customer_count} customers)

Current season — India: {season_india} | International: {season_intl}

Trend research from the web:
{trend_context_raw}

Past campaign performance data:
{learnings_context}

Propose the channel, message style, and 3-4 message variants for this campaign."""

    fallback = _fallback_variants(season_india, goal)
    fallback_highlights = normalize_trend_highlights(trend_snippets, season=season_india)

    try:
        result = await call_gemini(
            system_prompt=STRATEGIST_SYSTEM,
            user_prompt=user_prompt,
            temperature=0.8,
            max_tokens=2500,
            session_id=session_id,
            agent="strategist",
            stream=False,
        )
        channel = result.get("recommended_channel", result.get("channel", "whatsapp"))
        variants = normalize_variant_targets(result.get("variants") or fallback)
        if not result.get("variants"):
            variants = fallback
        reasoning = result.get("reasoning", "")
        channel_reasoning = result.get("channel_reasoning", "")
        message_style = result.get("message_style", "informational")
        raw_highlights = result.get("trend_highlights") or trend_snippets
        trend_highlights = normalize_trend_highlights(raw_highlights, season=season_india)
        predicted_open_rate = result.get("predicted_open_rate", "")
    except Exception:
        channel = "whatsapp"
        variants = fallback
        reasoning = (
            f"Built a {season_india} campaign for '{goal[:50]}' using proven templates "
            "and current fashion trend signals. Personalized for maximum relevance."
        )
        channel_reasoning = "Defaulting to WhatsApp for highest reach."
        message_style = "informational"
        trend_highlights = fallback_highlights
        predicted_open_rate = ""

    await publish(
        session_id,
        {
            "type": "agent_complete",
            "agent": "strategist",
            "data": {
                "channel": channel,
                "message_style": message_style,
                "trend_highlights": trend_highlights,
                "predicted_open_rate": predicted_open_rate,
                "variant_count": len(variants),
            },
        },
    )

    return {
        **state,
        "channel": channel,
        "message_variants": variants,
        "ai_reasoning": reasoning,
        "channel_reasoning": channel_reasoning,
        "message_style": message_style,
        "trend_highlights": trend_highlights,
        "trend_context": trend_context_raw,
        "predicted_open_rate": predicted_open_rate,
    }
