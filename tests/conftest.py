import asyncio
import os
import sys
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock
from dotenv import load_dotenv

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import NullPool

root_env = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(root_env)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from models.db import Base


TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://xenion:xenion_test@localhost:5435/xenion_crm_test"
)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def db_engine():
    engine = create_engine(TEST_DATABASE_URL, poolclass=NullPool)
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture
def db_session(db_engine) -> Generator[Session, None, None]:
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        for table in reversed(Base.metadata.sorted_tables):
            session.execute(table.delete())
        session.commit()
        session.close()


@pytest.fixture
def test_client(db_session) -> TestClient:
    import httpx
    from main import app
    from db.session import get_db
    
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    if not hasattr(app.state, 'http_client'):
        app.state.http_client = httpx.AsyncClient()
    
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def async_client(db_session) -> AsyncGenerator[AsyncClient, None]:
    from httpx import ASGITransport
    from main import app
    from db.session import get_db
    
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        yield client
    
    app.dependency_overrides.clear()


@pytest.fixture
def mock_gemini():
    return {
        "segment_name": "Test segment",
        "reasoning": "Test reasoning",
        "filter_rules": {"operator": "AND", "rules": []},
    }


@pytest.fixture
def mock_gemini_variants():
    return {
        "recommended_channel": "whatsapp",
        "reasoning": "Test strategy",
        "channel_reasoning": "WhatsApp for reach",
        "message_style": "informational",
        "trend_highlights": ["Summer trends ready"],
        "predicted_open_rate": "30-35%",
        "variants": [
            {"id": "A", "targets": {"age_group": "18-25"}, "message": "Hey {name}, test message A"},
            {"id": "B", "targets": {"age_group": "26-42"}, "message": "Hi {name}, test message B"},
        ],
    }


@pytest.fixture
def mock_tavily():
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "results": [
            {"content": "Summer fashion trends: pastels, linen, flowy silhouettes"},
            {"content": "Ethnic fusion wear trending for festive season"}
        ]
    }
    return mock_response


@pytest.fixture
def sample_customer_data():
    return {
        "name": "Priya Sharma",
        "email": "priya@example.com",
        "phone": "+919876543210",
        "city": "Mumbai",
        "region": "india",
        "gender": "female",
        "age_group": "26-35",
        "total_spent": 15000.00,
        "order_count": 5,
        "preferred_categories": ["kurta", "western"]
    }


@pytest.fixture
def sample_segment_data():
    return {
        "name": "High Value Customers",
        "nl_query": "customers who spent more than 10000 in the last 90 days",
        "filter_rules": {
            "operator": "AND",
            "rules": [
                {"field": "total_spent", "op": "gt", "value": 10000},
                {"field": "last_order_date", "op": "gt_days_ago", "value": 90}
            ]
        },
        "created_by": "ai"
    }


@pytest.fixture
def sample_campaign_data():
    return {
        "name": "Summer Sale 2026",
        "goal": "Get repeat purchases from high-value customers for summer collection",
        "channel": "whatsapp",
        "message_variants": [
            {"id": "A", "targets": {"age_group": "26-35"}, "message": "Hey {name}, summer collection is here!"},
            {"id": "B", "targets": {"age_group": "18-25"}, "message": "Hi {name}, check out our summer drop!"}
        ],
        "ai_reasoning": "Targeting based on past purchase behavior"
    }
