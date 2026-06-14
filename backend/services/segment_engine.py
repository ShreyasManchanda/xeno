from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import cast
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy import String
from models.db import Customer


def build_query(filter_rules: dict, db: Session):
    q = db.query(Customer)
    
    if not filter_rules:
        return q
    
    operator = filter_rules.get("operator", "AND")
    rules = filter_rules.get("rules", [])
    
    for rule in rules:
        field = rule.get("field")
        op = rule.get("op")
        value = rule.get("value")
        
        if not field or not op:
            continue
            
        col = getattr(Customer, field, None)
        if col is None:
            continue
        
        if op == "gt":
            q = q.filter(col > value)
        elif op == "lt":
            q = q.filter(col < value)
        elif op == "gte":
            q = q.filter(col >= value)
        elif op == "lte":
            q = q.filter(col <= value)
        elif op == "eq":
            q = q.filter(col == value)
        elif op == "neq":
            q = q.filter(col != value)
        elif op == "in":
            q = q.filter(col.in_(value))
        elif op == "lt_days_ago":
            q = q.filter(col < datetime.now().date() - timedelta(days=value))
        elif op == "gt_days_ago":
            q = q.filter(col > datetime.now().date() - timedelta(days=value))
        elif op == "contains":
            if isinstance(value, list):
                q = q.filter(col.op("@>")(value))
            else:
                q = q.filter(col.contains(value))
    
    return q
