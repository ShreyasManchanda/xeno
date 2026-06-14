<!-- v1.0 | propose changes in chat before editing -->

# tests/CLAUDE.md

## Owns
Backend unit tests and integration tests for the Xeno CRM API.
Uses pytest + pytest-asyncio with Docker PostgreSQL for integration tests.

## Does not
- Test frontend code
- Test channel-service (stateless, no logic worth unit testing)
- Make real Gemini or Tavily API calls (use mocks)
- Use SQLite (PostgreSQL-specific features required)

## Structure
```
tests/
├── conftest.py           # Shared fixtures, test client, DB setup
├── test_api/
│   ├── test_dashboard.py
│   ├── test_customers.py
│   ├── test_segments.py
│   ├── test_campaigns.py
│   └── test_receipts.py
├── test_services/
│   ├── test_segment_engine.py
│   ├── test_campaign_service.py
│   └── test_sse_bus.py
└── test_agents/
    ├── test_analyst.py
    ├── test_strategist.py
    └── test_executor.py
```

## Contracts
Receives from: backend/ (imports models, services, api)
Produces for: CI pipeline (exit codes)
Shared contract: Each test file tests one module; conftest provides DB fixtures

## Fixtures (conftest.py)
- `test_db`: PostgreSQL test database session (Docker)
- `test_client`: FastAPI TestClient with test DB
- `mock_gemini`: Mock google.genai.Client responses
- `mock_tavily`: Mock Tavily API responses

## Decisions
- Docker Compose required for tests. CI must run `docker-compose up` before pytest.
- Database tests use a separate test database, not the dev database.
- Each test rolls back transactions or truncates tables for isolation.
- Mock external APIs (Gemini, Tavily) to avoid rate limits and flakiness.
- Integration tests hit real endpoints; unit tests mock dependencies.

## Running Tests
```bash
docker-compose up -d
cd backend && pytest ../tests -v
```

---
Pending: none
Changelog: v1.0 Jun 2026 initial
