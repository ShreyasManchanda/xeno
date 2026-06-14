from typing import TypedDict, List


class CustomerBrief(TypedDict, total=False):
    id: str
    name: str
    email: str
    city: str
    total_spent: float
    age_group: str
    region: str


class Variant(TypedDict):
    id: str
    targets: dict
    message: str


class CampaignState(TypedDict, total=False):
    goal: str
    session_id: str
    season_india: str
    season_intl: str

    filter_rules: dict
    segment_name: str
    customer_count: int
    reasoning: str
    sample_customers: List[CustomerBrief]

    trend_highlights: List[str]
    trend_context: str
    channel: str
    message_variants: List[Variant]
    ai_reasoning: str
    channel_reasoning: str
    message_style: str
    predicted_open_rate: str

    variant_assignments: dict
    error: str
