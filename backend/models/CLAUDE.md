<!-- v1.0 | propose changes in chat before editing -->

# backend/models/CLAUDE.md

## Owns
A single file: db.py. Contains all SQLAlchemy ORM models:
Customer, Order, Segment, Campaign, Communication, CampaignLearning.
No Pydantic schemas here — those live in api/ files.

## Does not
- Define Pydantic request/response schemas
- Contain seed data — that lives in db/seed.py
- Contain migration logic — that lives in alembic/

## Contracts
Receives from: db/session.py (Session instance)
Produces for: api/, services/, agents/ (ORM model classes for queries and inserts)
Shared contract: all models imported from models.db — single import point
Must not import: api/, agents/, services/ (no circular imports)

## Decisions
- All models in one file — avoids circular import issues at this scale. Split
  only if the file exceeds ~300 lines.
- UUID primary keys using server_default=text("gen_random_uuid()") — generates
  in PostgreSQL, not Python, to avoid import dependency on uuid module in models.
- Communication.status is VARCHAR not a Python Enum — adding a new status value
  (e.g. bounced) requires no Alembic migration, only app code changes.
- Customer.preferred_categories is TEXT[] not JSONB — enables the PostgreSQL
  @> contains operator used in services/segment_engine.py per SPEC.md §4.

---
Pending: none
Changelog: v1.0 Jun 2026 initial