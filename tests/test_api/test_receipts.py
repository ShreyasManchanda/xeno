import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

from datetime import datetime
from models.db import Customer, Campaign, Communication, Segment
from api.receipts import ALLOWED_TRANSITIONS, is_valid_transition


def test_receipt_status_upgrade_queued_to_sent(test_client, db_session):
    customer = Customer(
        name="Test User",
        email="test@example.com"
    )
    db_session.add(customer)
    
    segment = Segment(
        name="Test Segment",
        filter_rules={},
        customer_count=0,
        created_by="manual"
    )
    db_session.add(segment)
    
    campaign = Campaign(
        name="Test Campaign",
        goal="Test",
        segment_id=segment.id,
        channel="whatsapp",
        status="running"
    )
    db_session.add(campaign)
    db_session.commit()
    
    comm = Communication(
        campaign_id=campaign.id,
        customer_id=customer.id,
        variant_id="A",
        channel="whatsapp",
        status="queued"
    )
    db_session.add(comm)
    db_session.commit()
    
    payload = {
        "communication_id": str(comm.id),
        "event": "sent",
        "timestamp": "2026-06-10T12:00:00Z"
    }
    
    response = test_client.post("/api/receipts", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] == True


def test_receipt_status_upgrade_sent_to_delivered(test_client, db_session):
    customer = Customer(
        name="Test User",
        email="test@example.com"
    )
    db_session.add(customer)
    
    segment = Segment(
        name="Test Segment",
        filter_rules={},
        customer_count=0,
        created_by="manual"
    )
    db_session.add(segment)
    
    campaign = Campaign(
        name="Test Campaign",
        goal="Test",
        segment_id=segment.id,
        channel="whatsapp",
        status="running"
    )
    db_session.add(campaign)
    db_session.commit()
    
    comm = Communication(
        campaign_id=campaign.id,
        customer_id=customer.id,
        variant_id="A",
        channel="whatsapp",
        status="sent"
    )
    db_session.add(comm)
    db_session.commit()
    
    payload = {
        "communication_id": str(comm.id),
        "event": "delivered",
        "timestamp": "2026-06-10T12:01:00Z"
    }
    
    response = test_client.post("/api/receipts", json=payload)
    assert response.status_code == 200


def test_receipt_status_upgrade_delivered_to_read(test_client, db_session):
    customer = Customer(
        name="Test User",
        email="test@example.com"
    )
    db_session.add(customer)
    
    segment = Segment(
        name="Test Segment",
        filter_rules={},
        customer_count=0,
        created_by="manual"
    )
    db_session.add(segment)
    
    campaign = Campaign(
        name="Test Campaign",
        goal="Test",
        segment_id=segment.id,
        channel="whatsapp",
        status="running"
    )
    db_session.add(campaign)
    db_session.commit()
    
    comm = Communication(
        campaign_id=campaign.id,
        customer_id=customer.id,
        variant_id="A",
        channel="whatsapp",
        status="delivered"
    )
    db_session.add(comm)
    db_session.commit()
    
    payload = {
        "communication_id": str(comm.id),
        "event": "read",
        "timestamp": "2026-06-10T12:02:00Z"
    }
    
    response = test_client.post("/api/receipts", json=payload)
    assert response.status_code == 200


def test_receipt_status_upgrade_read_to_clicked(test_client, db_session):
    customer = Customer(
        name="Test User",
        email="test@example.com"
    )
    db_session.add(customer)
    
    segment = Segment(
        name="Test Segment",
        filter_rules={},
        customer_count=0,
        created_by="manual"
    )
    db_session.add(segment)
    
    campaign = Campaign(
        name="Test Campaign",
        goal="Test",
        segment_id=segment.id,
        channel="whatsapp",
        status="running"
    )
    db_session.add(campaign)
    db_session.commit()
    
    comm = Communication(
        campaign_id=campaign.id,
        customer_id=customer.id,
        variant_id="A",
        channel="whatsapp",
        status="read"
    )
    db_session.add(comm)
    db_session.commit()
    
    payload = {
        "communication_id": str(comm.id),
        "event": "clicked",
        "timestamp": "2026-06-10T12:03:00Z"
    }
    
    response = test_client.post("/api/receipts", json=payload)
    assert response.status_code == 200


def test_receipt_status_upgrade_clicked_to_order_attributed(test_client, db_session):
    customer = Customer(
        name="Test User",
        email="test@example.com"
    )
    db_session.add(customer)
    
    segment = Segment(
        name="Test Segment",
        filter_rules={},
        customer_count=0,
        created_by="manual"
    )
    db_session.add(segment)
    
    campaign = Campaign(
        name="Test Campaign",
        goal="Test",
        segment_id=segment.id,
        channel="whatsapp",
        status="running"
    )
    db_session.add(campaign)
    db_session.commit()
    
    comm = Communication(
        campaign_id=campaign.id,
        customer_id=customer.id,
        variant_id="A",
        channel="whatsapp",
        status="clicked"
    )
    db_session.add(comm)
    db_session.commit()
    
    payload = {
        "communication_id": str(comm.id),
        "event": "order_attributed",
        "timestamp": "2026-06-10T12:05:00Z",
        "revenue": 2500.00
    }
    
    response = test_client.post("/api/receipts", json=payload)
    assert response.status_code == 200
    
    db_session.refresh(comm)
    assert float(comm.attributed_revenue) == 2500.00


def test_receipt_invalid_downgrade_rejected(test_client, db_session):
    customer = Customer(
        name="Test User",
        email="test@example.com"
    )
    db_session.add(customer)
    
    segment = Segment(
        name="Test Segment",
        filter_rules={},
        customer_count=0,
        created_by="manual"
    )
    db_session.add(segment)
    
    campaign = Campaign(
        name="Test Campaign",
        goal="Test",
        segment_id=segment.id,
        channel="whatsapp",
        status="running"
    )
    db_session.add(campaign)
    db_session.commit()
    
    comm = Communication(
        campaign_id=campaign.id,
        customer_id=customer.id,
        variant_id="A",
        channel="whatsapp",
        status="read"
    )
    db_session.add(comm)
    db_session.commit()
    
    payload = {
        "communication_id": str(comm.id),
        "event": "queued",
        "timestamp": "2026-06-10T12:00:00Z"
    }
    
    response = test_client.post("/api/receipts", json=payload)
    assert response.status_code == 409
    assert response.json()["error"] == "invalid_transition"


def test_receipt_idempotency_duplicate_event(test_client, db_session):
    customer = Customer(
        name="Test User",
        email="test@example.com"
    )
    db_session.add(customer)
    
    segment = Segment(
        name="Test Segment",
        filter_rules={},
        customer_count=0,
        created_by="manual"
    )
    db_session.add(segment)
    
    campaign = Campaign(
        name="Test Campaign",
        goal="Test",
        segment_id=segment.id,
        channel="whatsapp",
        status="running"
    )
    db_session.add(campaign)
    db_session.commit()
    
    comm = Communication(
        campaign_id=campaign.id,
        customer_id=customer.id,
        variant_id="A",
        channel="whatsapp",
        status="sent"
    )
    db_session.add(comm)
    db_session.commit()
    
    payload = {
        "communication_id": str(comm.id),
        "event": "sent",
        "timestamp": "2026-06-10T12:00:00Z"
    }
    
    response = test_client.post("/api/receipts", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] == True
    assert data["skipped"] == True


def test_receipt_nonexistent_communication(test_client, db_session):
    import uuid
    fake_id = str(uuid.uuid4())
    
    payload = {
        "communication_id": fake_id,
        "event": "sent",
        "timestamp": "2026-06-10T12:00:00Z"
    }
    
    response = test_client.post("/api/receipts", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] == True
    assert data["skipped"] == True


def test_receipt_invalid_status(test_client, db_session):
    customer = Customer(
        name="Test User",
        email="test@example.com"
    )
    db_session.add(customer)
    
    segment = Segment(
        name="Test Segment",
        filter_rules={},
        customer_count=0,
        created_by="manual"
    )
    db_session.add(segment)
    
    campaign = Campaign(
        name="Test Campaign",
        goal="Test",
        segment_id=segment.id,
        channel="whatsapp",
        status="running"
    )
    db_session.add(campaign)
    db_session.commit()
    
    comm = Communication(
        campaign_id=campaign.id,
        customer_id=customer.id,
        variant_id="A",
        channel="whatsapp",
        status="queued"
    )
    db_session.add(comm)
    db_session.commit()
    
    payload = {
        "communication_id": str(comm.id),
        "event": "invalid_status",
        "timestamp": "2026-06-10T12:00:00Z"
    }
    
    response = test_client.post("/api/receipts", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["skipped"] == True


def test_allowed_transitions():
    assert is_valid_transition("queued", "sent")
    assert is_valid_transition("sent", "delivered")
    assert is_valid_transition("delivered", "read")
    assert is_valid_transition("read", "clicked")
    assert is_valid_transition("clicked", "order_attributed")
    assert not is_valid_transition("read", "queued")
    assert "sent" in ALLOWED_TRANSITIONS["queued"]
    assert "failed" in ALLOWED_TRANSITIONS["queued"]


def test_receipt_failed_status(test_client, db_session):
    customer = Customer(
        name="Test User",
        email="test@example.com"
    )
    db_session.add(customer)
    
    segment = Segment(
        name="Test Segment",
        filter_rules={},
        customer_count=0,
        created_by="manual"
    )
    db_session.add(segment)
    
    campaign = Campaign(
        name="Test Campaign",
        goal="Test",
        segment_id=segment.id,
        channel="whatsapp",
        status="running"
    )
    db_session.add(campaign)
    db_session.commit()
    
    comm = Communication(
        campaign_id=campaign.id,
        customer_id=customer.id,
        variant_id="A",
        channel="whatsapp",
        status="sent"
    )
    db_session.add(comm)
    db_session.commit()
    
    payload = {
        "communication_id": str(comm.id),
        "event": "failed",
        "timestamp": "2026-06-10T12:00:00Z"
    }
    
    response = test_client.post("/api/receipts", json=payload)
    assert response.status_code == 200
