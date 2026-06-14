import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

from models.db import Customer, Segment


def test_list_segments_empty(test_client, db_session):
    response = test_client.get("/api/segments")
    assert response.status_code == 200
    assert response.json() == []


def test_create_segment(test_client, db_session):
    customer = Customer(
        name="Test User",
        email="test@example.com",
        total_spent=15000
    )
    db_session.add(customer)
    db_session.commit()
    
    segment_data = {
        "name": "High Value",
        "nl_query": "customers with high spend",
        "filter_rules": {
            "operator": "AND",
            "rules": [{"field": "total_spent", "op": "gt", "value": 10000}]
        },
        "created_by": "manual"
    }
    
    response = test_client.post("/api/segments", json=segment_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "High Value"
    assert data["customer_count"] == 1


def test_get_segment_not_found(test_client, db_session):
    import uuid
    fake_id = str(uuid.uuid4())
    response = test_client.get(f"/api/segments/{fake_id}")
    assert response.status_code == 404


def test_get_segment_detail(test_client, db_session):
    customer = Customer(
        name="Test User",
        email="test@example.com",
        total_spent=15000
    )
    db_session.add(customer)
    db_session.commit()
    
    segment = Segment(
        name="Test Segment",
        nl_query="test",
        filter_rules={"operator": "AND", "rules": []},
        customer_count=1,
        created_by="manual"
    )
    db_session.add(segment)
    db_session.commit()
    
    response = test_client.get(f"/api/segments/{segment.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["segment"]["name"] == "Test Segment"


def test_update_segment(test_client, db_session):
    customer1 = Customer(
        name="High Value",
        email="high@example.com",
        total_spent=20000
    )
    customer2 = Customer(
        name="Low Value",
        email="low@example.com",
        total_spent=5000
    )
    db_session.add(customer1)
    db_session.add(customer2)
    db_session.commit()
    
    segment = Segment(
        name="Test Segment",
        filter_rules={"operator": "AND", "rules": []},
        customer_count=2,
        created_by="manual"
    )
    db_session.add(segment)
    db_session.commit()
    
    update_data = {
        "filter_rules": {
            "operator": "AND",
            "rules": [{"field": "total_spent", "op": "gt", "value": 10000}]
        }
    }
    
    response = test_client.put(f"/api/segments/{segment.id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["customer_count"] == 1


def test_delete_segment(test_client, db_session):
    segment = Segment(
        name="To Delete",
        filter_rules={},
        customer_count=0,
        created_by="manual"
    )
    db_session.add(segment)
    db_session.commit()
    
    response = test_client.delete(f"/api/segments/{segment.id}")
    assert response.status_code == 200
    assert response.json()["deleted"] == True
    
    response = test_client.get(f"/api/segments/{segment.id}")
    assert response.status_code == 404
