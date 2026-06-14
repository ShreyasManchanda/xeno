"""
CampaignExecutor node — pure Python, no LLM call.
Assigns each customer in the segment the best-matching message variant
and substitutes {name} and {city} placeholders.
"""
from services.sse_bus import publish
from services.segment_engine import build_query

_AGE_MIDPOINTS = {"18-25": 21, "26-35": 30, "36-45": 40, "45+": 52}


def _age_matches(customer_group: str, target_range: str) -> bool:
    if not customer_group or not target_range:
        return False

    customer_mid = _AGE_MIDPOINTS.get(customer_group)
    if customer_mid is None:
        return False

    if target_range.endswith("+"):
        try:
            return customer_mid >= int(target_range[:-1])
        except ValueError:
            return False

    if "-" in target_range:
        try:
            low, high = target_range.split("-", 1)
            return int(low) <= customer_mid <= int(high)
        except ValueError:
            return False

    return customer_group == target_range


def assign_variant(customer, variants: list) -> dict:
    if not variants:
        return {"id": "A", "targets": {}, "message": "Hi {name}, check out our latest collection."}

    if getattr(customer, "region", None) == "international":
        for v in variants:
            if v.get("targets", {}).get("region") == "international":
                return v

    for v in variants:
        targets = v.get("targets", {})
        ag = targets.get("age_group", "")
        if ag and _age_matches(customer.age_group, ag):
            return v

    return variants[0]


def personalize(message: str, customer) -> str:
    name_parts = (customer.name or "").split()
    first_name = name_parts[0] if name_parts else "there"
    city = getattr(customer, "city", "") or ""
    return message.replace("{name}", first_name).replace("{city}", city)


async def run_executor(state: dict, db) -> dict:
    session_id = state.get("session_id", "")
    filter_rules = state.get("filter_rules", {})
    message_variants = state.get("message_variants", [])

    await publish(
        session_id,
        {
            "type": "agent_start",
            "agent": "executor",
            "message": "Preparing message variants...",
        },
    )

    query = build_query(filter_rules, db)
    customers = query.all()
    total = len(customers)

    variant_assignments = {}
    for i, customer in enumerate(customers):
        variant = assign_variant(customer, message_variants)
        variant_assignments[str(customer.id)] = {
            "variant_id": variant.get("id", "A"),
            "message": personalize(variant.get("message", ""), customer),
        }
        if total > 0 and (i + 1) % max(1, total // 5) == 0:
            await publish(
                session_id,
                {
                    "type": "agent_progress",
                    "agent": "executor",
                    "message": f"Personalizing messages… {i + 1}/{total}",
                    "data": {"current": i + 1, "total": total},
                },
            )

    await publish(
        session_id,
        {
            "type": "agent_complete",
            "agent": "executor",
            "data": {
                "variants": message_variants,
                "variant_count": len(message_variants),
                "assignments_count": len(variant_assignments),
            },
        },
    )

    await publish(
        session_id,
        {
            "type": "proposal_ready",
            "data": {
                "segment_name": state.get("segment_name", ""),
                "segment": filter_rules,
                "customer_count": total,
                "channel": state.get("channel", "whatsapp"),
                "message_variants": message_variants,
                "reasoning": state.get("ai_reasoning", ""),
                "channel_reasoning": state.get("channel_reasoning", ""),
                "message_style": state.get("message_style", ""),
                "trend_highlights": state.get("trend_highlights", []),
                "trend_context": state.get("trend_context", ""),
                "predicted_open_rate": state.get("predicted_open_rate", ""),
                "sample_customers": state.get("sample_customers", []),
            },
        },
    )

    return {
        **state,
        "variant_assignments": variant_assignments,
    }
