<!-- v1.1 | propose changes in chat before editing -->

# backend/CLAUDE.md

## Owns
FastAPI application deployed to Railway or Render. main.py mounts all routers and
configures CORS and lifespan. Routes in api/, models in models/db.py, business
logic in services/, agent pipeline in agents/, DB utilities in db/.

## Does not
- Contain simulation logic — that belongs in channel-service/
- Call the Anthropic or Tavily APIs directly — delegated to agents/
- Define Pydantic schemas inside model files — schemas live in api/ files

## Contracts
Receives from: frontend (HTTP requests), channel-service (POST /api/receipts)
Produces for: frontend (JSON + SSE streams), channel-service (POST /send)
Shared contract: SPEC.md §5 (all routes), §6 (SSE shapes), §7 (channel contract)
Must not import: channel-service/ modules (separate deployment, separate process)

## Decisions
- Two SSE endpoints with different lifecycles: /copilot/stream/:session_id
  (short, ends when proposal_ready fires) and /campaigns/:id/stream (longer,
  ends on campaign_complete). Keeping them separate avoids mixed state.
- In-memory asyncio.Queue for SSE sessions (services/sse_bus.py) — intentional
  demo-scale choice documented in SPEC.md §18. Scale path is Redis pub/sub.
- main.py registers a lifespan handler to create the httpx.AsyncClient used by
  campaign_service.py — one shared client, not one per request.

---
Pending: none
Changelog: v1.0 Jun 2026 initial | v1.1 Jun 2026 added dynamic CORS support, psycopg2-binary driver, and refactored async dispatcher for production safety