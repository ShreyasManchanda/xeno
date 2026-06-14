<!-- v1.0 | propose changes in chat before editing -->

# backend/db/CLAUDE.md

## Owns
session.py — get_db FastAPI dependency (yields SQLAlchemy Session)
seed.py    — full Tana & Co. dataset generation and insertion

## Does not
- Define ORM models — imports them from models/db.py
- Run migrations — Alembic owns that (alembic/)
- Contain business logic

## Contracts
Receives from: models/db.py (model classes used in seed inserts)
Produces for: all api/ route handlers via get_db dependency injection
Shared contract: get_db is the only way to access the DB across the app;
  every route handler that needs DB access declares db: Session = Depends(get_db)
Must not import: api/, agents/, services/

## Decisions
- get_db uses try/finally yield pattern — guarantees session.close() even if
  the route handler raises an exception.
- seed.py is idempotent — checks for existing records before inserting so it
  is safe to run multiple times during development.
- seed.py inserts pre-seeded CampaignLearning rows so the Strategist agent has
  historical context from the first demo run — see SPEC.md §12 for structure.

---
Pending: none
Changelog: v1.0 Jun 2026 initial