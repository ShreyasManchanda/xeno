import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

from models.db import Customer, Order, Campaign, Communication


def test_list_customers_empty(test_client, db_session):
    response = test_client.get("/api/customers")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["customers"] == []


def test_list_customers_with_data(test_client, db_session):
    customer1 = Customer(
        name="Priya Sharma",
        email="priya@example.com",
        city="Mumbai",
        region="india",
        age_group="26-35"
    )
    customer2 = Customer(
        name="Amit Patel",
        email="amit@example.com",
        city="Delhi",
        region="india",
        age_group="18-25"
    )
    db_session.add(customer1)
    db_session.add(customer2)
    db_session.commit()
    
    response = test_client.get("/api/customers")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["customers"]) == 2


def test_list_customers_search(test_client, db_session):
    customer1 = Customer(
        name="Priya Sharma",
        email="priya@example.com",
        city="Mumbai"
    )
    customer2 = Customer(
        name="Amit Patel",
        email="amit@example.com",
        city="Delhi"
    )
    db_session.add(customer1)
    db_session.add(customer2)
    db_session.commit()
    
    response = test_client.get("/api/customers?search=priya")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["customers"][0]["name"] == "Priya Sharma"


def test_list_customers_filter_city(test_client, db_session):
    customer1 = Customer(
        name="Priya Sharma",
        email="priya@example.com",
        city="Mumbai"
    )
    customer2 = Customer(
        name="Amit Patel",
        email="amit@example.com",
        city="Delhi"
    )
    db_session.add(customer1)
    db_session.add(customer2)
    db_session.commit()
    
    response = test_client.get("/api/customers?city=Mumbai")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["customers"][0]["city"] == "Mumbai"


def test_list_customers_pagination(test_client, db_session):
    for i in range(25):
        customer = Customer(
            name=f"Customer {i}",
            email=f"customer{i}@example.com"
        )
        db_session.add(customer)
    db_session.commit()
    
    response = test_client.get("/api/customers?page=1&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert len(data["customers"]) == 10
    assert data["total"] == 25
    assert data["page"] == 1


def test_get_customer_not_found(test_client, db_session):
    import uuid
    fake_id = str(uuid.uuid4())
    response = test_client.get(f"/api/customers/{fake_id}")
    assert response.status_code == 404


def test_get_customer_detail(test_client, db_session):
    customer = Customer(
        name="Priya Sharma",
        email="priya@example.com",
        city="Mumbai",
        region="india",
        age_group="26-35",
        total_spent=15000,
        preferred_categories=["kurta", "western"]
    )
    db_session.add(customer)
    db_session.commit()
    
    order = Order(
        customer_id=customer.id,
        amount=5000,
        items=[{"name": "Kurta Set", "category": "ethnic", "price": 5000, "qty": 1}]
    )
    db_session.add(order)
    db_session.commit()
    
    response = test_client.get(f"/api/customers/{customer.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["customer"]["name"] == "Priya Sharma"
    assert data["customer"]["city"] == "Mumbai"
    assert len(data["orders"]) == 1
