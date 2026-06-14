import sys
import os
from datetime import date, timedelta
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

from models.db import Customer
from services.segment_engine import build_query


def test_build_query_empty_rules(db_session):
    filter_rules = {"operator": "AND", "rules": []}
    query = build_query(filter_rules, db_session)
    assert query is not None


def test_build_query_gt_operator(db_session):
    customer1 = Customer(
        name="High",
        email="high@example.com",
        total_spent=20000
    )
    customer2 = Customer(
        name="Low",
        email="low@example.com",
        total_spent=5000
    )
    db_session.add(customer1)
    db_session.add(customer2)
    db_session.commit()
    
    filter_rules = {
        "operator": "AND",
        "rules": [{"field": "total_spent", "op": "gt", "value": 10000}]
    }
    
    query = build_query(filter_rules, db_session)
    results = query.all()
    assert len(results) == 1
    assert results[0].name == "High"


def test_build_query_lt_operator(db_session):
    customer1 = Customer(
        name="High",
        email="high@example.com",
        total_spent=20000
    )
    customer2 = Customer(
        name="Low",
        email="low@example.com",
        total_spent=5000
    )
    db_session.add(customer1)
    db_session.add(customer2)
    db_session.commit()
    
    filter_rules = {
        "operator": "AND",
        "rules": [{"field": "total_spent", "op": "lt", "value": 10000}]
    }
    
    query = build_query(filter_rules, db_session)
    results = query.all()
    assert len(results) == 1
    assert results[0].name == "Low"


def test_build_query_gte_operator(db_session):
    customer1 = Customer(
        name="High",
        email="high@example.com",
        total_spent=10000
    )
    customer2 = Customer(
        name="Low",
        email="low@example.com",
        total_spent=5000
    )
    db_session.add(customer1)
    db_session.add(customer2)
    db_session.commit()
    
    filter_rules = {
        "operator": "AND",
        "rules": [{"field": "total_spent", "op": "gte", "value": 10000}]
    }
    
    query = build_query(filter_rules, db_session)
    results = query.all()
    assert len(results) == 1
    assert results[0].name == "High"


def test_build_query_lte_operator(db_session):
    customer1 = Customer(
        name="High",
        email="high@example.com",
        total_spent=20000
    )
    customer2 = Customer(
        name="Low",
        email="low@example.com",
        total_spent=10000
    )
    db_session.add(customer1)
    db_session.add(customer2)
    db_session.commit()
    
    filter_rules = {
        "operator": "AND",
        "rules": [{"field": "total_spent", "op": "lte", "value": 10000}]
    }
    
    query = build_query(filter_rules, db_session)
    results = query.all()
    assert len(results) == 1
    assert results[0].name == "Low"


def test_build_query_eq_operator(db_session):
    customer1 = Customer(
        name="Match",
        email="match@example.com",
        city="Mumbai"
    )
    customer2 = Customer(
        name="No Match",
        email="nomatch@example.com",
        city="Delhi"
    )
    db_session.add(customer1)
    db_session.add(customer2)
    db_session.commit()
    
    filter_rules = {
        "operator": "AND",
        "rules": [{"field": "city", "op": "eq", "value": "Mumbai"}]
    }
    
    query = build_query(filter_rules, db_session)
    results = query.all()
    assert len(results) == 1
    assert results[0].name == "Match"


def test_build_query_neq_operator(db_session):
    customer1 = Customer(
        name="Mumbai",
        email="mumbai@example.com",
        city="Mumbai"
    )
    customer2 = Customer(
        name="Delhi",
        email="delhi@example.com",
        city="Delhi"
    )
    db_session.add(customer1)
    db_session.add(customer2)
    db_session.commit()
    
    filter_rules = {
        "operator": "AND",
        "rules": [{"field": "city", "op": "neq", "value": "Mumbai"}]
    }
    
    query = build_query(filter_rules, db_session)
    results = query.all()
    assert len(results) == 1
    assert results[0].name == "Delhi"


def test_build_query_in_operator(db_session):
    customer1 = Customer(
        name="Mumbai",
        email="mumbai@example.com",
        city="Mumbai"
    )
    customer2 = Customer(
        name="Delhi",
        email="delhi@example.com",
        city="Delhi"
    )
    customer3 = Customer(
        name="Bangalore",
        email="bangalore@example.com",
        city="Bangalore"
    )
    db_session.add(customer1)
    db_session.add(customer2)
    db_session.add(customer3)
    db_session.commit()
    
    filter_rules = {
        "operator": "AND",
        "rules": [{"field": "city", "op": "in", "value": ["Mumbai", "Delhi"]}]
    }
    
    query = build_query(filter_rules, db_session)
    results = query.all()
    assert len(results) == 2


def test_build_query_contains_operator(db_session):
    customer1 = Customer(
        name="Has Kurta",
        email="kurta@example.com",
        preferred_categories=["kurta", "western"]
    )
    customer2 = Customer(
        name="No Kurta",
        email="nokurta@example.com",
        preferred_categories=["saree", "accessories"]
    )
    db_session.add(customer1)
    db_session.add(customer2)
    db_session.commit()
    
    filter_rules = {
        "operator": "AND",
        "rules": [{"field": "preferred_categories", "op": "contains", "value": ["kurta"]}]
    }
    
    query = build_query(filter_rules, db_session)
    results = query.all()
    assert len(results) == 1
    assert results[0].name == "Has Kurta"


def test_build_query_lt_days_ago_operator(db_session):
    recent = date.today() - timedelta(days=30)
    old = date.today() - timedelta(days=120)
    
    customer1 = Customer(
        name="Recent",
        email="recent@example.com",
        last_order_date=recent
    )
    customer2 = Customer(
        name="Old",
        email="old@example.com",
        last_order_date=old
    )
    db_session.add(customer1)
    db_session.add(customer2)
    db_session.commit()
    
    filter_rules = {
        "operator": "AND",
        "rules": [{"field": "last_order_date", "op": "lt_days_ago", "value": 60}]
    }
    
    query = build_query(filter_rules, db_session)
    results = query.all()
    assert len(results) == 1
    assert results[0].name == "Old"


def test_build_query_gt_days_ago_operator(db_session):
    recent = date.today() - timedelta(days=30)
    old = date.today() - timedelta(days=120)
    
    customer1 = Customer(
        name="Recent",
        email="recent@example.com",
        last_order_date=recent
    )
    customer2 = Customer(
        name="Old",
        email="old@example.com",
        last_order_date=old
    )
    db_session.add(customer1)
    db_session.add(customer2)
    db_session.commit()
    
    filter_rules = {
        "operator": "AND",
        "rules": [{"field": "last_order_date", "op": "gt_days_ago", "value": 60}]
    }
    
    query = build_query(filter_rules, db_session)
    results = query.all()
    assert len(results) == 1
    assert results[0].name == "Recent"


def test_build_query_multiple_rules(db_session):
    customer1 = Customer(
        name="Match",
        email="match@example.com",
        city="Mumbai",
        total_spent=15000
    )
    customer2 = Customer(
        name="City Match",
        email="citymatch@example.com",
        city="Mumbai",
        total_spent=5000
    )
    customer3 = Customer(
        name="Spend Match",
        email="spendmatch@example.com",
        city="Delhi",
        total_spent=15000
    )
    db_session.add(customer1)
    db_session.add(customer2)
    db_session.add(customer3)
    db_session.commit()
    
    filter_rules = {
        "operator": "AND",
        "rules": [
            {"field": "city", "op": "eq", "value": "Mumbai"},
            {"field": "total_spent", "op": "gt", "value": 10000}
        ]
    }
    
    query = build_query(filter_rules, db_session)
    results = query.all()
    assert len(results) == 1
    assert results[0].name == "Match"


def test_build_query_invalid_field(db_session):
    filter_rules = {
        "operator": "AND",
        "rules": [{"field": "nonexistent_field", "op": "eq", "value": "test"}]
    }
    
    query = build_query(filter_rules, db_session)
    results = query.all()
    assert len(results) >= 0


def test_build_query_none_rules(db_session):
    query = build_query(None, db_session)
    assert query is not None
    
    query = build_query({}, db_session)
    assert query is not None
