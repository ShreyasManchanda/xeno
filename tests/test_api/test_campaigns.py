import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

from models.db import Customer, Segment, Campaign, Communication


def test_list_campaigns_empty(test_client, db_session):
    response = test_client.get("/api/campaigns")
    assert response.status_code == 200
    assert response.json() == []


def test_create_campaign(test_client, db_session):
    segment = Segment(
        name="Test Segment",
        filter_rules={},
        customer_count=0,
        created_by="manual"
    )
    db_session.add(segment)
    db_session.commit()
    
    campaign_data = {
        "name": "Test Campaign",
        "goal": "Test goal",
        "segment_id": str(segment.id),
        "channel": "whatsapp",
        "message_variants": [
            {"id": "A", "targets": {}, "message": "Test message"}
        ]
    }
    
    response = test_client.post("/api/campaigns", json=campaign_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Campaign"
    assert data["status"] == "draft"


def test_get_campaign_not_found(test_client, db_session):
    import uuid
    fake_id = str(uuid.uuid4())
    response = test_client.get(f"/api/campaigns/{fake_id}")
    assert response.status_code == 404


def test_get_campaign_detail(test_client, db_session):
    segment = Segment(
        name="Test Segment",
        filter_rules={},
        customer_count=0,
        created_by="manual"
    )
    db_session.add(segment)
    db_session.commit()
    
    campaign = Campaign(
        name="Test Campaign",
        goal="Test goal",
        segment_id=segment.id,
        channel="whatsapp",
        status="draft",
        message_variants=[{"id": "A", "targets": {}, "message": "Test"}]
    )
    db_session.add(campaign)
    db_session.commit()
    
    response = test_client.get(f"/api/campaigns/{campaign.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["campaign"]["name"] == "Test Campaign"
    assert "stats" in data
    assert "variant_breakdown" in data


def test_delete_draft_campaign(test_client, db_session):
    segment = Segment(
        name="Test Segment",
        filter_rules={},
        customer_count=0,
        created_by="manual"
    )
    db_session.add(segment)
    db_session.commit()
    
    campaign = Campaign(
        name="Draft Campaign",
        goal="Test",
        segment_id=segment.id,
        channel="whatsapp",
        status="draft"
    )
    db_session.add(campaign)
    db_session.commit()
    
    response = test_client.delete(f"/api/campaigns/{campaign.id}")
    assert response.status_code == 200


def test_delete_running_campaign_fails(test_client, db_session):
    segment = Segment(
        name="Test Segment",
        filter_rules={},
        customer_count=0,
        created_by="manual"
    )
    db_session.add(segment)
    db_session.commit()
    
    campaign = Campaign(
        name="Running Campaign",
        goal="Test",
        segment_id=segment.id,
        channel="whatsapp",
        status="running"
    )
    db_session.add(campaign)
    db_session.commit()
    
    response = test_client.delete(f"/api/campaigns/{campaign.id}")
    assert response.status_code == 400


def test_campaign_filter_by_status(test_client, db_session):
    segment = Segment(
        name="Test Segment",
        filter_rules={},
        customer_count=0,
        created_by="manual"
    )
    db_session.add(segment)
    db_session.commit()
    
    campaign1 = Campaign(
        name="Draft",
        goal="Test",
        segment_id=segment.id,
        channel="whatsapp",
        status="draft"
    )
    campaign2 = Campaign(
        name="Completed",
        goal="Test",
        segment_id=segment.id,
        channel="whatsapp",
        status="completed"
    )
    db_session.add(campaign1)
    db_session.add(campaign2)
    db_session.commit()
    
    response = test_client.get("/api/campaigns?status=draft")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["status"] == "draft"


def test_launch_campaign(test_client, db_session):
    customer = Customer(
        name="Test User",
        email="test@example.com",
        phone="+919999999999"
    )
    db_session.add(customer)
    db_session.commit()
    
    segment = Segment(
        name="Test Segment",
        filter_rules={"operator": "AND", "rules": []},
        customer_count=1,
        created_by="manual"
    )
    db_session.add(segment)
    db_session.commit()
    
    campaign = Campaign(
        name="Test Campaign",
        goal="Test",
        segment_id=segment.id,
        channel="whatsapp",
        status="draft",
        message_variants=[{"id": "A", "targets": {}, "message": "Hi {name}"}]
    )
    db_session.add(campaign)
    db_session.commit()
    
    response = test_client.post(f"/api/campaigns/{campaign.id}/launch")
    assert response.status_code == 200
    data = response.json()
    assert data["launched"] == True
