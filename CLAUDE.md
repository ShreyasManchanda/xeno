<!-- CLAUDE.md v1.1 | propose changes in chat before editing -->

# Xenion — Claude Project Context

## What this is
AI-native CRM. Three-node LangGraph pipeline (Analyst → Strategist →
Executor) proposes segments + message variants. Marketers review and approve.
Real-time delivery tracking feeds a performance feedback loop.

Read SPEC.md before generating code. Read the folder's CLAUDE.md before
editing files in that folder. Read AGENTS.md for commands and invariants.

## Stack
Frontend:  Next.js 14 App Router · Tailwind · shadcn/ui → Vercel
Backend:   FastAPI · SQLAlchemy · PostgreSQL · LangGraph → Railway
Channel:   Separate FastAPI service (delivery simulator) → Railway
AI:        gemini-2.5-pro (Google GenAI SDK) · Tavily API
Real-time: SSE via FastAPI StreamingResponse

## Cross-cutting rules
Python: async/await always. httpx.AsyncClient for HTTP. get_db dependency for
DB. Pydantic v2 for schemas. UUIDs as strings in responses. os.getenv() for env.

TypeScript: App Router only. lib/api.ts for all HTTP. lib/sse.ts for SSE.
lib/types.ts for types. 'use client' only for state/events. No localStorage.

Data: Status upgrades only (queued→sent→delivered→read→clicked→order_attributed).
Derive campaign stats from communications table — no separate stats table.
SSE event shapes match SPEC.md §6. API routes match SPEC.md §5.

## Folder map
SPEC.md / AGENTS.md    → source of truth and commands
backend/agents/        → LangGraph graph, state, three node files
backend/api/           → route handlers only
backend/models/        → all SQLAlchemy models (db.py)
backend/services/      → segment engine, campaign service, learnings, SSE bus
backend/db/            → session dependency, seed script
channel-service/       → stateless delivery simulator
frontend/lib/          → api.ts, sse.ts, types.ts
frontend/app/          → pages and route segments
frontend/components/   → UI components only

## Living document process
Propose changes in chat. Get human approval. Bump version. Add changelog entry.

---
Pending: none
Changelog: v1.0 Jun 2026 initial | v1.1 trimmed to under 75 lines
