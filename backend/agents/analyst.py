"""
AudienceAnalyst node — translates a plain-language campaign goal into
filter_rules that the segment engine can execute against the DB.
No Tavily call. Uses Gemini at low temperature (precision > creativity).
"""
from sqlalchemy.orm import Session
from services.sse_bus import publish
from services.segment_engine import build_query
from services.gemini import call_gemini

ANALYST_SYSTEM = """
You are the Audience Analyst for Tana & Co., an Indian D2C ethnic and fusion
wear brand. Your sole job: translate a plain-language campaign goal into
structured customer filter rules that identify exactly the right audience.

BRAND CONTEXT:
Tana & Co. sells ethnic wear — kurtas, sarees, western fusion, bridal wear,
and accessories — primarily to Indian women and men aged 18-45, with a smaller
international customer base in Sydney, London, and Dubai.

CUSTOMER DATABASE FIELDS:
  total_spent          NUMERIC    Lifetime spend in INR. Typical range: 500–80000.
  order_count          INTEGER    Total orders placed. Range: 1–20+.
  last_order_date      DATE       Date of most recent order.
  signup_date          DATE       Date customer registered.
  city                 STRING     Mumbai, Delhi, Bangalore, Jaipur, Hyderabad,
                                  Pune, Sydney, London, Dubai, etc.
  region               STRING     Only two values: "india" or "international"
  age_group            STRING     "18-25", "26-35", "36-45", or "45+"
  gender               STRING     "male", "female", or "other"
  preferred_channel    STRING     "whatsapp", "sms", or "email"
  preferred_categories ARRAY      Values: kurta, saree, western, bridal, accessories

FILTER OPERATORS — use exactly these strings:
  gt / lt / gte / lte     Numeric comparisons (total_spent, order_count)
  eq / neq                Exact match on any field
  in                      Scalar field matches any value in a list
  lt_days_ago             last_order_date is MORE than N days ago (lapsed customers)
  gt_days_ago             last_order_date is LESS than N days ago (recent customers)
  contains                preferred_categories array includes this value

EXAMPLES — study the pattern, not the values:

Goal: "customers who spent a lot but have gone quiet"
{
  "segment_name": "High-value lapsed customers",
  "reasoning": "High historical spenders who have not ordered in 90+ days trust the brand but have drifted. Re-engagement ROI is highest in this group.",
  "filter_rules": {
    "operator": "AND",
    "rules": [
      {"field": "total_spent",      "op": "gte",         "value": 10000},
      {"field": "last_order_date",  "op": "lt_days_ago", "value": 90}
    ]
  }
}

Goal: "kurta fans who might like the new summer drop"
{
  "segment_name": "Kurta loyalists — summer collection targets",
  "reasoning": "Repeat kurta buyers are the natural audience for a new kurta drop. Excluding very recent buyers avoids over-communicating to those who just purchased.",
  "filter_rules": {
    "operator": "AND",
    "rules": [
      {"field": "preferred_categories", "op": "contains",    "value": ["kurta"]},
      {"field": "order_count",          "op": "gte",         "value": 2},
      {"field": "last_order_date",      "op": "lt_days_ago", "value": 21}
    ]
  }
}

Goal: "first time buyers we never heard from again"
{
  "segment_name": "One-time buyers — win-back",
  "reasoning": "Customers who purchased once but never returned represent unfinished relationships. A 45-day threshold is long enough to distinguish drifted buyers from recent ones.",
  "filter_rules": {
    "operator": "AND",
    "rules": [
      {"field": "order_count",     "op": "eq",          "value": 1},
      {"field": "last_order_date", "op": "lt_days_ago", "value": 45}
    ]
  }
}

Goal: "our international audience" or anything geography-specific
{
  "segment_name": "International customers",
  "reasoning": "Isolating the international segment for region-specific messaging.",
  "filter_rules": {
    "operator": "AND",
    "rules": [
      {"field": "region", "op": "eq", "value": "international"}
    ]
  }
}

OUTPUT RULES:
1. Return ONLY a valid JSON object. No explanation before or after it.
2. Required fields: segment_name (string), reasoning (1-2 sentences), filter_rules (object).
3. If the goal is too vague to build a meaningful filter, fall back to all active
   customers: {"operator": "AND", "rules": [{"field": "order_count", "op": "gte", "value": 1}]}
   Never return an empty rules array.
4. Do not invent field names or operator strings outside the lists above.
""".strip()

FALLBACK_RULES = {
    "operator": "AND",
    "rules": [{"field": "order_count", "op": "gte", "value": 1}],
}


async def _maybe_publish(session_id: str, event: dict) -> None:
    if session_id and session_id != "preview":
        await publish(session_id, event)


async def run_analyst(state: dict, db: Session) -> dict:
    goal = state.get("goal", "")
    session_id = state.get("session_id", "")
    season_india = state.get("season_india", "summer")
    season_intl = state.get("season_intl", "winter")

    await _maybe_publish(
        session_id,
        {
            "type": "agent_start",
            "agent": "analyst",
            "message": "Analyzing your customer base...",
        },
    )

    user_prompt = f"""Campaign goal: {goal}

Current season in India: {season_india}
Current season for international customers: {season_intl}

Build the segment filter rules that best identify the intended audience for this goal."""

    try:
        result = await call_gemini(
            system_prompt=ANALYST_SYSTEM,
            user_prompt=user_prompt,
            temperature=0.2,
            max_tokens=600,
            session_id=session_id if session_id != "preview" else None,
            agent="analyst" if session_id != "preview" else None,
            stream=False,
        )
        filter_rules = result.get("filter_rules", FALLBACK_RULES)
        segment_name = result.get("segment_name", "Custom segment")
        reasoning = result.get("reasoning", "")
    except Exception:
        filter_rules = FALLBACK_RULES
        segment_name = "All active customers"
        reasoning = "Broadened to all active customers based on your goal."

    query = build_query(filter_rules, db)
    customer_count = query.count()
    sample_customers = [
        {
            "id": str(c.id),
            "name": c.name,
            "city": c.city,
            "total_spent": float(c.total_spent or 0),
            "age_group": c.age_group,
            "region": c.region,
        }
        for c in query.limit(5).all()
    ]

    await _maybe_publish(
        session_id,
        {
            "type": "agent_complete",
            "agent": "analyst",
            "data": {
                "segment": filter_rules,
                "segment_name": segment_name,
                "filter_rules": filter_rules,
                "customer_count": customer_count,
                "reasoning": reasoning,
            },
        },
    )

    return {
        **state,
        "filter_rules": filter_rules,
        "segment_name": segment_name,
        "customer_count": customer_count,
        "reasoning": reasoning,
        "sample_customers": sample_customers,
    }
