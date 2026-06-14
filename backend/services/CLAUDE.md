<!-- v1.1 | Added gemini.py shared client -->

# backend/services/CLAUDE.md

## Owns
segment_engine.py  — converts filter_rules JSONB to a SQLAlchemy query
campaign_service.py — campaign launch: queue comms, dispatch to channel-service,
                      background task polling every 30s for completion trigger
learnings.py       — write CampaignLearning after completion; read context for Strategist
sse_bus.py         — in-memory asyncio.Queue per session_id; publish and cleanup
gemini.py          — shared Gemini client (JSON mode + optional token streaming to SSE)

## Does not
- Handle HTTP routing — called from api/ and agents/
- Define the LangGraph graph or nodes — that belongs in agents/
- Define ORM models — imports from models/db.py

## Contracts
Receives from: api/ (calls into services), agents/ (calls sse_bus, learnings, gemini)
Produces for: api/ (query results, launch confirmations)
Produces for: agents/ (learnings context string, SSE event publishing, LLM responses)
Shared contract: sse_bus.py is the single event bus — agents/, api/receipts.py publish here
Must not import: api/ modules (would create circular dependency)

## Decisions
- gemini.py uses httpx + responseMimeType application/json — agents pass session_id
  to stream token deltas as agent_stream SSE events during copilot runs.
- sse_bus.py uses a module-level dict — intentional demo-scale tradeoff (SPEC §13).
- segment_engine.py uses PostgreSQL @> for preferred_categories contains rules.
- campaign_service.py batches channel-service calls at 20 concurrent (SPEC §7).

---
Pending: none
Changelog: v1.0 Jun 2026 initial | v1.1 Jun 2026 added gemini.py