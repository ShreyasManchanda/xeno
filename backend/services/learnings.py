from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
from models.db import CampaignLearning


def write_learning(db: Session, campaign_id: str, data: dict):
    learning = CampaignLearning(
        campaign_id=campaign_id,
        segment_description=data.get("segment_description"),
        channel=data.get("channel"),
        message_style=data.get("message_style"),
        open_rate=data.get("open_rate"),
        click_rate=data.get("click_rate"),
        order_rate=data.get("order_rate"),
        customer_count=data.get("customer_count")
    )
    db.add(learning)
    db.commit()


def get_recent_learnings(db: Session, limit: int = 5):
    return db.query(CampaignLearning)\
        .order_by(CampaignLearning.created_at.desc())\
        .limit(limit)\
        .all()


def format_learnings_for_prompt(learnings: list) -> str:
    if not learnings:
        return ""
    
    lines = ["Past campaign performance for reference:"]
    for l in learnings:
        lines.append(
            f'- "{l.segment_description}" → {l.channel} → {l.message_style} → '
            f'{float(l.open_rate or 0)*100:.1f}% read, {float(l.order_rate or 0)*100:.1f}% orders (n={l.customer_count})'
        )
    lines.append("Use this to inform your channel and message tone recommendation.")
    lines.append("If no past data is relevant, proceed without it.")
    
    return "\n".join(lines)


def infer_style(message_variants: list) -> str:
    if not message_variants:
        return "informational"
    
    all_text = " ".join([v.get("message", "") for v in message_variants]).lower()
    
    if any(k in all_text for k in ["diwali", "festival", "celebrate", "occasion"]):
        return "festive"
    if any(k in all_text for k in ["limited", "hours", "ends", "last chance"]):
        return "urgent"
    if any(k in all_text for k in ["miss", "back", "thinking", "personal"]):
        return "emotional"
    
    return "informational"
