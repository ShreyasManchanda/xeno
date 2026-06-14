<!-- v1.0 | propose changes in chat before editing -->

# backend/api/CLAUDE.md

## Owns
One FastAPI router per resource file:
dashboard.py  — GET /api/dashboard/stats
customers.py  — GET /api/customers, GET /api/customers/:id
segments.py   — CRUD + POST /api/segments/preview
campaigns.py  — CRUD, POST /api/campaigns/copilot, SSE stream endpoints
receipts.py   — POST /api/receipts (channel-service callbacks only)
ingest.py     — POST /api/ingest

## Does not
- Contain business logic beyond request validation and response shaping
- Invoke LangGraph graph directly except in campaigns.py
- Define SQLAlchemy models — imports from models/db.py
- Own SSE bus — uses services/sse_bus.py

## Contracts
Receives from: frontend (HTTP), channel-service (POST /api/receipts)
Produces for: frontend (JSON responses, SSE streams)
Shared contract: all routes and response shapes defined in SPEC.md §5
Must not import: agents/ from any file except campaigns.py

## Decisions
- receipts.py validates status upgrade before writing — prevents downgrades and
  double-counting per SPEC.md §5 idempotency requirement.
- campaigns.py starts LangGraph graph as asyncio background task and returns
  session_id immediately — frontend must open SSE before this call per SPEC.md §10.
- segments.py POST /preview runs AudienceAnalyst node in isolation and returns
  without saving — lets marketer see customer count before committing.
- ingest.py upserts on customer email — safe to run seed script multiple times.

---
Pending: none
Changelog: v1.0 Jun 2026 initial