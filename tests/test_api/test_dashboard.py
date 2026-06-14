import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

from models.db import Customer, Segment, Campaign, Communication


def test_dashboard_stats_empty(test_client, db_session):
    response = test_client.get("/api/dashboard/stats")
    assert response.status_code == 200
    data = response.json()
    assert "kpis" in data
    assert "nudges" in data
    assert data["kpis"]["total_customers"] == 0
    assert data["kpis"]["active_segments"] == 0
    assert data["kpis"]["campaigns_run"] == 0


def test_dashboard_stats_with_data(test_client, db_session):
    customer = Customer(
        name="Test User",
        email="test@example.com",
        city="Mumbai",
        region="india",
        age_group="26-35",
        total_spent=10000
    )
    db_session.add(customer)
    
    segment = Segment(
        name="Test Segment",
        nl_query="test query",
        filter_rules={"operator": "AND", "rules": []},
        customer_count=1,
        created_by="manual"
    )
    db_session.add(segment)
    db_session.commit()
    
    campaign = Campaign(
        name="Test Campaign",
        goal="Test goal",
        segment_id=str(segment.id),
        channel="whatsapp",
        status="completed"
    )
    db_session.add(campaign)
    db_session.commit()
    
    comm = Communication(
        campaign_id=str(campaign.id),
        customer_id=str(customer.id),
        variant_id="A",
        channel="whatsapp",
        status="delivered"
    )
    db_session.add(comm)
    db_session.commit()
    
    response = test_client.get("/api/dashboard/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["kpis"]["total_customers"] == 1
    assert data["kpis"]["active_segments"] == 1
    assert data["kpis"]["campaigns_run"] == 1


def test_dashboard_nudges_structure(test_client, db_session):
    response = test_client.get("/api/dashboard/stats")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["nudges"], list)
    for nudge in data["nudges"]:
        assert "title" in nudge
        assert "body" in nudge
        assert "cta" in nudge
