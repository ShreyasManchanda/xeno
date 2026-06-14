# IMPLEMENTATION.md v1.0

> Agent execution playbook. Follow phases in order.
> Each phase builds on previous. Do not skip ahead.

---

## Prerequisites

Before Phase 1:
1. Install Docker Desktop
2. Install Python 3.11+
3. Install Node.js 20+
4. Get API keys: Google AI Studio (Gemini), Tavily

---

## Phase 1: Foundation (Day 1)

### 1.1 docker-compose.yml
PostgreSQL 15 service. Port 5432. Named volume for persistence.

```bash
docker-compose up -d
docker-compose ps  # Verify running
```

### 1.2 backend/requirements.txt
Core: fastapi, uvicorn, sqlalchemy, alembic, asyncpg, pydantic, httpx, google-genai, tavily-python

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 1.3 backend/models/db.py
All 6 SQLAlchemy models per SPEC.md §4:
- Customer (preferred_categories as ARRAY(Text))
- Order (items as JSONB)
- Segment (filter_rules as JSONB)
- Campaign (message_variants as JSONB)
- Communication
- CampaignLearning

### 1.4 backend/db/session.py
get_db dependency. try/finally yield pattern. DATABASE_URL from env.

### 1.5 Alembic Setup
```bash
cd backend
alembic init alembic
# Edit alembic/env.py: import models, set target_metadata
alembic revision --autogenerate -m "initial"
alembic upgrade head
```

### 1.6 backend/db/seed.py
Deterministic faker (seed=42). Generate:
- 200 customers (70% India, 30% international)
- 1-12 orders per customer
- 5 pre-seeded CampaignLearning rows

```bash
cd backend && python -m db.seed
```

---

## Phase 2: Backend API - Read Layer (Day 2)

### 2.1 backend/main.py
FastAPI app. CORS middleware. Lifespan for httpx.AsyncClient. Mount routers.

### 2.2 backend/api/dashboard.py
GET /api/dashboard/stats. Aggregate queries on customers/segments/campaigns.

### 2.3 backend/api/customers.py
GET /api/customers (paginated, searchable). GET /api/customers/:id (with orders).

### 2.4 backend/services/segment_engine.py
build_query() converts filter_rules to SQLAlchemy query. Support all ops in SPEC.md §4.

### 2.5 backend/api/segments.py
GET /api/segments. POST /api/segments. GET /api/segments/:id. PUT /api/segments/:id. DELETE /api/segments/:id.

### 2.6 backend/services/sse_bus.py
Module-level dict of asyncio.Queue. create_queue, publish, cleanup functions.

---

## Phase 3: Agent Pipeline (Day 3)

### 3.1 backend/agents/state.py
CampaignState TypedDict with all fields from SPEC.md §10:
- goal, session_id, season_india, season_intl
- filter_rules, customer_count, reasoning, sample_customers
- trend_highlights, channel, message_variants
- variant_assignments

### 3.2 backend/agents/analyst.py
AudienceAnalyst node. Gemini call with structured prompt.
System prompt: role definition, filter_rules schema, examples.
Returns: filter_rules, customer_count, reasoning, sample_customers.

### 3.3 backend/agents/strategist.py
CampaignStrategist node. Two-step process:
1. Tavily API search for trends
2. Gemini call with trend context + learnings
Returns: trend_highlights, channel, message_variants, reasoning.

### 3.4 backend/agents/executor.py
CampaignExecutor node. Pure Python, no LLM.
assign_variant() function per SPEC.md §9.
personalize() replaces {name}, {city}.
Returns: variant_assignments dict.

### 3.5 backend/agents/graph.py
LangGraph StateGraph. Nodes: analyst → strategist → executor.
Edges: analyst → strategist, strategist → executor.
Compile to runnable graph.

### 3.6 backend/api/campaigns.py
- GET /api/campaigns
- GET /api/campaigns/:id
- POST /api/campaigns (save draft)
- POST /api/campaigns/:id/launch
- POST /api/campaigns/copilot (fire-and-forget async)
- GET /api/campaigns/copilot/stream/:session_id (SSE)
- GET /api/campaigns/:id/stream (SSE)

---

## Phase 4: Delivery Layer (Day 4)

### 4.1 channel-service/main.py
FastAPI app. POST /send endpoint. Returns 200 immediately, BackgroundTask runs simulation.

### 4.2 channel-service/simulator.py
simulate_delivery() async function. Probabilities per SPEC.md §7.
Exponential backoff retry for callbacks. Dead letter list.

### 4.3 backend/services/campaign_service.py
launch_campaign() function:
1. Create Communication records (queued)
2. Batch dispatch to channel-service (20 concurrent)
3. Background task: poll for completion every 30s

### 4.4 backend/api/receipts.py
POST /api/receipts. Idempotent. Validate status upgrade. Update Communication. Push SSE event.

### 4.5 backend/services/learnings.py
write_learning() after campaign completion. get_recent_learnings() for Strategist context.

---

## Phase 5: Frontend (Day 5)

### 5.1 Setup
```bash
cd frontend
npx create-next-app@14 . --typescript --tailwind --app
npx shadcn@latest init
npx shadcn@latest add button card input label badge table tabs
```

### 5.2 frontend/lib/types.ts
TypeScript interfaces matching SPEC.md §4 data model.
SSE event union types per SPEC.md §6.

### 5.3 frontend/lib/api.ts
HTTP functions for each endpoint. No direct fetch.

### 5.4 frontend/lib/sse.ts
useSSE hook. EventSource lifecycle. Typed event dispatch.

### 5.5 frontend/components/
Implement per frontend/components/CLAUDE.md:
- shared/Sidebar.tsx, StatusBadge.tsx
- dashboard/NudgeCard.tsx, KPICards.tsx
- segments/FilterChips.tsx, NLCreator.tsx
- campaigns/AgentStepper.tsx, ProposalCard.tsx, DeliveryFunnel.tsx, VariantBreakdown.tsx, EventFeed.tsx

### 5.6 frontend/app/
All pages per frontend/app/CLAUDE.md:
- layout.tsx (with Sidebar)
- page.tsx (dashboard)
- customers/page.tsx, customers/[id]/page.tsx
- segments/page.tsx, segments/new/page.tsx, segments/[id]/page.tsx
- campaigns/page.tsx, campaigns/new/page.tsx, campaigns/[id]/page.tsx

---

## Phase 6: Tests & Evals

### 6.1 Test Structure
Create test files per tests/CLAUDE.md structure.

### 6.2 Key Test Cases
- receipts.py: status transitions, idempotency, invalid downgrade rejection
- segment_engine.py: all filter operators
- executor.py: variant assignment logic per SPEC.md §9
- campaigns.py: SSE stream lifecycle

### 6.3 Run Tests
```bash
docker-compose up -d
cd backend && pytest ../tests -v
```

### 6.4 Evals (Optional)
Create golden_examples.json. Run evals manually for quality assessment.

---

## Deployment

### Railway Setup
1. Create two services: crm-backend, channel-service
2. Add PostgreSQL addon to crm-backend
3. Set environment variables per SPEC.md §19

### Vercel Setup
1. Import frontend from GitHub
2. Set NEXT_PUBLIC_API_URL

---

## Verification Checklist

Before considering complete:
- [ ] docker-compose up works
- [ ] Seed script creates data
- [ ] All API endpoints return 200
- [ ] Agent pipeline produces valid proposal
- [ ] Campaign launch queues communications
- [ ] SSE streams deliver events
- [ ] Frontend renders all pages
- [ ] Tests pass

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| v1.0 | Jun 2026 | Initial implementation guide |
