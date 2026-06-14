<!-- AGENTS.md v1.2 | Cross-tool standard (Cursor, Claude Code, Codex, Copilot, Aider) -->
<!-- Propose changes in chat. Bump version on approval. -->

# Xenion — Agent Working Context

Three-node LangGraph pipeline (Analyst → Strategist → Executor), two FastAPI
services (CRM backend + channel-service), SSE real-time delivery tracking,
PostgreSQL. Source of truth: SPEC.md.

## Commands
Dev:      docker-compose up (starts PostgreSQL locally)
Backend:  cd backend && uvicorn main:app --reload --port 8000
Channel:  cd channel-service && uvicorn main:app --reload --port 8001
Frontend: cd frontend && npm run dev
Seed:     cd backend && python -m db.seed
Migrate:  cd backend && alembic upgrade head
New migration: alembic revision --autogenerate -m "description"

## Module map
SPEC.md            → architecture decisions, API contracts, SSE schemas
CLAUDE.md          → project context, cross-cutting conventions
IMPLEMENTATION.md  → agent execution playbook, phase-by-phase guide
backend/agents/    → LangGraph graph, state, three node files
backend/api/       → FastAPI route handlers only
backend/models/    → all SQLAlchemy models in one file (db.py)
backend/services/  → segment engine, campaign service, learnings, SSE bus
backend/db/        → session dependency, seed script
channel-service/   → delivery simulator (separate deployment, stateless)
frontend/lib/      → api.ts, sse.ts, types.ts
frontend/app/      → Next.js App Router pages
frontend/components/ → UI components only
tests/             → backend unit tests + integration tests (pytest)
evals/             → AI quality evaluation scripts (manual runs)

Each folder has its own CLAUDE.md. Read it before editing files in that folder.

## Before you write code
1. Read SPEC.md section relevant to the task
2. Read the target folder's CLAUDE.md
3. Check SPEC.md §5 for exact API route before adding or changing routes
4. Check SPEC.md §6 for exact SSE event shape before emitting or consuming events

## Invariants — do not violate without a SPEC.md update first
- Communication status upgrades only: queued→sent→delivered→read→clicked→order_attributed
- "read" is the single status covering what email calls "opened" and WhatsApp
  calls "read" (blue ticks) — do not add a separate "opened" status (SPEC.md §4)
- No per-customer Claude API calls — variants generated once by Strategist
- /api/receipts must be idempotent — check before writing
- All API routes match SPEC.md §5 exactly
- All SSE event shapes match SPEC.md §6 exactly
- No auth, no pages/ router, no localStorage, no requests library

## Living document process
To change any context file: describe the change in chat, get human approval,
then update the file, bump its version, add a changelog entry.

---
Pending: none
Changelog: v1.0 Jun 2026 initial | v1.1 Jun 2026 added tests/, evals/, IMPLEMENTATION.md | v1.2 Jun 2026 updated CORS, Postgres driver, and async DB session safety for production deployment
