# SPEC.md — Xenion (Final Locked Spec)
> Source of truth. All architectural decisions are final and researched.
> Do not override without updating this file and documenting the reason.

---

## 1. Product Overview

**Demo brand:** Tana & Co. — Indian D2C ethnic and fusion wear.

**Core problem:** A fashion brand marketer has thousands of customers, limited budget,
and one shot at a WhatsApp campaign. They need to know who to send it to, what to say,
and whether it worked.

**Core loop:**
```
Marketer enters goal (NL)
→ AI pipeline: Analyst builds segment → Strategist researches trends → Executor prepares variants
→ Marketer reviews proposal, edits if needed, approves
→ Campaign executes against channel service
→ Real-time delivery tracking via async callbacks
→ AI insight summary generated on completion
→ Learnings stored, injected into next Strategist run
```

**What this is NOT:** A sales/pipeline CRM, support ticket system, or lead management tool.

---

## 2. Stack (Locked)

| Layer            | Choice                                       |
|------------------|----------------------------------------------|
| Frontend         | Next.js 14 (App Router), Tailwind, shadcn/ui |
| Backend          | FastAPI (Python 3.11+), SQLAlchemy, Alembic  |
| Database         | PostgreSQL 15                                |
| Agent framework  | LangGraph (proper nodes, shared state)       |
| AI model         | gemini-2.5-pro (Google GenAI SDK)           |
| Trend search     | Tavily API (Strategist node only)            |
| Channel service  | Separate FastAPI app, separate Railway svc   |
| Real-time        | SSE via FastAPI StreamingResponse            |
| Async HTTP       | httpx.AsyncClient (never requests)           |
| Deployment       | Vercel (frontend) + Railway (2x backend)     |

---

## 3. Folder Structure

```
xenion/
├── SPEC.md                        # This file
├── CLAUDE.md                      # Root AI context
├── AGENTS.md                      # LangGraph agent detail
├── .cursorrules
├── .env.example
├── docker-compose.yml             # Local dev: PostgreSQL
│
├── frontend/
│   ├── CLAUDE.md
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx               # Dashboard (audience-first home)
│   │   ├── customers/
│   │   │   ├── page.tsx           # Customer table + search
│   │   │   └── [id]/page.tsx      # Customer 360
│   │   ├── segments/
│   │   │   ├── page.tsx           # Segment list
│   │   │   ├── new/page.tsx       # NL creator + filter chips
│   │   │   └── [id]/page.tsx      # Segment detail + performance
│   │   └── campaigns/
│   │       ├── page.tsx           # Campaign list
│   │       ├── new/page.tsx       # Copilot flow (SSE stepper)
│   │       └── [id]/page.tsx      # Live tracking + analytics
│   ├── components/
│   │   ├── ui/                    # shadcn components only
│   │   ├── dashboard/
│   │   │   ├── NudgeCard.tsx
│   │   │   └── KPICards.tsx
│   │   ├── segments/
│   │   │   ├── FilterChips.tsx    # Editable rule chips
│   │   │   └── NLCreator.tsx
│   │   └── campaigns/
│   │       ├── AgentStepper.tsx   # Live agent progress
│   │       ├── ProposalCard.tsx   # Review/edit before approve
│   │       ├── DeliveryFunnel.tsx
│   │       ├── VariantBreakdown.tsx
│   │       └── EventFeed.tsx      # Live callback stream
│   └── lib/
│       ├── api.ts                 # All API calls (no direct fetch in components)
│       ├── sse.ts                 # useSSE hook
│       └── types.ts               # Shared TypeScript types
│
├── backend/
│   ├── CLAUDE.md
│   ├── main.py
│   ├── alembic.ini
│   ├── alembic/versions/
│   ├── agents/
│   │   ├── graph.py               # LangGraph graph definition
│   │   ├── state.py               # CampaignState TypedDict
│   │   ├── analyst.py             # AudienceAnalyst node
│   │   ├── strategist.py          # CampaignStrategist node
│   │   └── executor.py            # CampaignExecutor node (pure Python)
│   ├── api/
│   │   ├── dashboard.py
│   │   ├── customers.py
│   │   ├── segments.py
│   │   ├── campaigns.py           # Includes SSE endpoints
│   │   ├── receipts.py            # Channel service callbacks
│   │   └── ingest.py              # Data ingestion endpoint
│   ├── models/db.py               # All SQLAlchemy models
│   ├── services/
│   │   ├── segment_engine.py      # filter_rules JSONB → SQLAlchemy query
│   │   ├── campaign_service.py    # Launch, fire to channel, complete
│   │   └── learnings.py           # Write + read campaign_learnings
│   └── db/
│       ├── session.py             # get_db dependency
│       └── seed.py                # Full Tana & Co. seed script
│
└── channel-service/
    ├── CLAUDE.md
    ├── main.py
    └── simulator.py               # Async delivery sim + retry logic
```

---

## 4. Data Model

### customers
```sql
id                   UUID PRIMARY KEY DEFAULT gen_random_uuid()
name                 VARCHAR(100) NOT NULL
email                VARCHAR(150) UNIQUE
phone                VARCHAR(20)
city                 VARCHAR(50)
region               VARCHAR(20)      -- 'india' | 'international'
gender               VARCHAR(10)
age_group            VARCHAR(10)      -- '18-25' | '26-35' | '36-45' | '45+'
signup_date          DATE
total_spent          NUMERIC(10,2)    DEFAULT 0
order_count          INT              DEFAULT 0
last_order_date      DATE
preferred_channel    VARCHAR(20)      DEFAULT 'whatsapp'
preferred_categories TEXT[]           -- {'kurta','western','bridal','saree','accessories'}
created_at           TIMESTAMPTZ      DEFAULT NOW()
```

### orders
```sql
id             UUID PRIMARY KEY DEFAULT gen_random_uuid()
customer_id    UUID REFERENCES customers(id) ON DELETE CASCADE
amount         NUMERIC(10,2)
items          JSONB            -- [{name, category, price, qty}]
order_date     DATE
season         VARCHAR(20)      -- 'summer' | 'winter' | 'festive'
category_tags  TEXT[]
created_at     TIMESTAMPTZ DEFAULT NOW()
```

### segments
```sql
id             UUID PRIMARY KEY DEFAULT gen_random_uuid()
name           VARCHAR(100)
nl_query       TEXT             -- original NL input
filter_rules   JSONB            -- see schema below
customer_count INT
created_by     VARCHAR(10)      -- 'ai' | 'manual'
created_at     TIMESTAMPTZ DEFAULT NOW()
```

**filter_rules schema:**
```json
{
  "operator": "AND",
  "rules": [
    { "field": "total_spent",     "op": "gt",          "value": 10000 },
    { "field": "last_order_date", "op": "lt_days_ago", "value": 90   },
    { "field": "preferred_categories", "op": "contains", "value": ["kurta"] }
  ]
}
```

Supported ops: `gt` `lt` `gte` `lte` `eq` `neq` `in` `lt_days_ago` `gt_days_ago` `contains`
- `contains` on TEXT[] uses PostgreSQL `@>` operator
- `in` on scalar fields uses SQL `IN`

### campaigns
```sql
id               UUID PRIMARY KEY DEFAULT gen_random_uuid()
name             VARCHAR(150)
goal             TEXT             -- plain language marketer input
segment_id       UUID REFERENCES segments(id)
channel          VARCHAR(20)      -- 'whatsapp' | 'sms' | 'email'
status           VARCHAR(20)      DEFAULT 'draft'
                                  -- 'draft'|'running'|'completed'|'failed'
message_variants JSONB            -- [{id, targets, message}] — see Section 9
ai_reasoning     TEXT
trend_context    TEXT             -- raw Tavily output used by Strategist
launched_at      TIMESTAMPTZ
completed_at     TIMESTAMPTZ
created_at       TIMESTAMPTZ DEFAULT NOW()
```

### communications
```sql
id                   UUID PRIMARY KEY DEFAULT gen_random_uuid()
campaign_id          UUID REFERENCES campaigns(id)
customer_id          UUID REFERENCES customers(id)
variant_id           VARCHAR(5)       -- 'A' | 'B' | 'C' | 'D'
personalized_message TEXT
channel              VARCHAR(20)
status               VARCHAR(30)      DEFAULT 'queued'
sent_at              TIMESTAMPTZ
delivered_at         TIMESTAMPTZ
read_at              TIMESTAMPTZ
clicked_at           TIMESTAMPTZ
order_attributed_at  TIMESTAMPTZ
attributed_revenue   NUMERIC(10,2)
created_at           TIMESTAMPTZ DEFAULT NOW()
```

**Status state machine (upgrades only — never downgrade):**
```
queued → sent → delivered → read → clicked → order_attributed
                          ↘ failed
```

Note: "read" covers what email platforms call "opened" (pixel tracking) and what
WhatsApp calls "read" (blue ticks). We use "read" throughout — it matches the
WhatsApp Business API terminology and the assignment's explicit language.

### campaign_learnings
```sql
id                   UUID PRIMARY KEY DEFAULT gen_random_uuid()
campaign_id          UUID REFERENCES campaigns(id)
segment_description  TEXT
channel              VARCHAR(20)
message_style        VARCHAR(30)  -- 'festive'|'urgent'|'emotional'|'informational'
open_rate            NUMERIC(5,4) -- using "open" here for readability (= read_rate)
click_rate           NUMERIC(5,4)
order_rate           NUMERIC(5,4)
customer_count       INT
created_at           TIMESTAMPTZ DEFAULT NOW()
```

---

## 5. API Endpoints

### Dashboard
```
GET /api/dashboard/stats
Response: {
  kpis: { total_customers, active_segments, campaigns_run, avg_read_rate },
  nudges: [{ title, body, cta, segment_id? }]   ← one Claude call, 3 nudges
}
```

### Customers
```
GET  /api/customers?search=&city=&age_group=&page=1&limit=20
GET  /api/customers/:id
     Response: { customer, orders: [...], campaign_history: [...] }
```

### Segments
```
GET    /api/segments
POST   /api/segments/preview
       Body: { nl_query: string }
       → Runs AudienceAnalyst node only (no save)
       → { filter_rules, customer_count, reasoning, sample_customers: [...5] }
POST   /api/segments
       Body: { name, nl_query, filter_rules, created_by }
GET    /api/segments/:id
       Response: { segment, customers: [...paginated],
                   performance: { campaigns_run, avg_read_rate, avg_click_rate, avg_order_rate } }
PUT    /api/segments/:id
       Body: { filter_rules }   ← marketer edits filter chips
DELETE /api/segments/:id
```

### Campaigns
```
GET    /api/campaigns?status=
GET    /api/campaigns/:id
       Response: { campaign, stats, variant_breakdown: [...], recent_events: [...20] }
POST   /api/campaigns
       Body: { name, goal, segment_id, channel, message_variants, ai_reasoning, trend_context }
       → Saves as status='draft'
POST   /api/campaigns/:id/launch
       → Sets status='running', queues all comms, fires to channel service in batches of 20
       → { launched: true, total_queued: int }
DELETE /api/campaigns/:id    ← draft only
```

### Agent Pipeline (SSE)
```
POST /api/campaigns/copilot
     Body: { goal: string, session_id: string }
     → Kicks off LangGraph pipeline async (fire and forget)
     → { session_id }   ← returns immediately

GET  /api/campaigns/copilot/stream/:session_id
     → SSE stream (see Section 6)
     → Client must open this BEFORE calling POST /copilot
```

### Delivery Tracking (SSE)
```
GET /api/campaigns/:id/stream
    → SSE stream of live delivery events for a running campaign
```

### Receipts (called by channel service only)
```
POST /api/receipts
     Body: { communication_id, event, timestamp, revenue? }
     → Idempotent. Validates status upgrade. Updates communication.
     → Triggers SSE push to any active /stream/:id listeners.
     → 200 { ok: true }
     → 409 { error: "invalid_transition" } if downgrade attempted
     → 200 { ok: true, skipped: true } if duplicate event
```

### Ingest (covers the assignment's "take in customers and orders" requirement)
```
POST /api/ingest
     Body: {
       customers: [{ name, email, phone, city, ... }],
       orders:    [{ customer_email, amount, items, order_date, ... }]
     }
     → Upserts on email for customers, inserts orders
     → { customers_upserted: int, orders_inserted: int, errors: [...] }
```

Note: The seed script calls this internally. In production this endpoint would
receive webhooks from Shopify/WooCommerce. State this in your walkthrough video.

---

## 6. SSE Event Schemas

### Agent pipeline stream (/api/campaigns/copilot/stream/:session_id)
```jsonc
{ "type": "agent_start",    "agent": "analyst",    "message": "Analyzing your customer base..." }
{ "type": "agent_stream",   "agent": "analyst",    "delta": "..." }   ← token chunk while Gemini streams JSON
{ "type": "agent_progress", "agent": "strategist", "message": "Found 5 trend signals from the web" }
{ "type": "agent_complete", "agent": "analyst",    "data": { "segment": {}, "segment_name": "...", "customer_count": 187, "reasoning": "..." } }
{ "type": "agent_start",    "agent": "strategist", "message": "Searching Indian summer fashion trends..." }
{ "type": "agent_stream",   "agent": "strategist", "delta": "..." }
{ "type": "agent_complete", "agent": "strategist", "data": { "trend_highlights": [], "channel": "whatsapp" } }
{ "type": "agent_start",    "agent": "executor",   "message": "Preparing message variants..." }
{ "type": "agent_progress", "agent": "executor",   "message": "Personalizing messages… 45/187", "data": { "current": 45, "total": 187 } }
{ "type": "agent_complete", "agent": "executor",   "data": { "variants": [], "variant_count": 3 } }
{ "type": "proposal_ready", "data": { "segment_name": "...", "segment": {}, "customer_count": 187, "channel": "whatsapp", "message_variants": [], "reasoning": "...", "trend_highlights": [], "trend_context": "..." } }
{ "type": "error",          "agent": "strategist", "message": "Retrying (attempt 2/3)..." }
{ "type": "fatal_error",    "message": "Pipeline failed after 3 attempts." }
```

### Delivery tracking stream (/api/campaigns/:id/stream)
```jsonc
{ "type": "stats_update",      "data": { "sent": 84, "delivered": 67, "failed": 5, "read": 12, "clicked": 3, "orders": 0, "revenue": 0 } }
{ "type": "comm_event",        "data": { "customer_name": "Priya Sharma", "event": "delivered",        "variant_id": "B", "timestamp": "..." } }
{ "type": "comm_event",        "data": { "customer_name": "Kavya Nair",   "event": "order_attributed", "variant_id": "A", "revenue": 2400 } }
{ "type": "campaign_complete", "data": { "final_stats": {}, "insight_summary": "..." } }
```

---

## 7. Channel Service Contract

**Separate Railway deployment. CRM and channel service are independent.**

### CRM → Channel: POST /send
```json
{
  "communication_id": "uuid",
  "recipient": { "email": "priya@...", "phone": "+919..." },
  "message": "Hey Priya, summer's here...",
  "channel": "whatsapp"
}
```
CRM sends in async batches of 20 using asyncio.gather + semaphore.

### Channel → CRM: POST /api/receipts (callback)
```json
{
  "communication_id": "uuid",
  "event": "delivered",
  "timestamp": "2026-06-10T14:32:00Z",
  "revenue": 2400.00
}
```

### Simulation probabilities
```
sent             → always, ~0.1s after receiving /send
delivered        → 80% of sent,  0.5–2s after sent
failed           → 20% of sent  (fires instead of delivered)
read             → 55% of delivered, 2–8s after delivered
clicked          → 30% of read,  3–10s after read
order_attributed → 30% of clicked, 30–180s after clicked
                   revenue = random(800, 8000) INR
```

Rationale: 80% delivery, 44% overall read rate, 13% click rate, 4% order rate.
These match published D2C WhatsApp campaign benchmarks (MoEngage, Klaviyo data).

### Channel service retry logic
If CRM /api/receipts returns non-200 or times out:
```python
# Exponential backoff with jitter (industry standard)
for attempt in range(3):
    delay = min(1 * (2 ** attempt), 10) + random.uniform(0, 0.5)
    await asyncio.sleep(delay)
    response = await call_receipts(payload)
    if response.status_code == 200:
        break
else:
    # After 3 failures: log to in-memory dead_letter list
    dead_letter.append({ "payload": payload, "failed_at": now() })
```
State in video: "At scale this would be a Redis queue or SQS with a monitored DLQ."

---

## 8. CRM → Channel Retry Logic

If channel service /send returns non-200 or times out:
```python
for attempt in range(3):
    delay = min(1 * (2 ** attempt), 10) + random.uniform(0, 0.5)
    try:
        await httpx_client.post(CHANNEL_SERVICE_URL + "/send", json=payload, timeout=5)
        break
    except Exception:
        if attempt == 2:
            # Mark communication as failed after 3 attempts
            await update_comm_status(comm_id, "failed")
```

---

## 9. Personalization — Variant Assignment

### Strategist outputs 3–4 variants with targeting metadata:
```json
{
  "variants": [
    {
      "id": "A",
      "targets": { "age_group": "18-25", "region": "india", "season": "summer" },
      "message": "Hey {name}, summer is here — our linen edit just dropped 🌿"
    },
    {
      "id": "B",
      "targets": { "age_group": "26-42", "region": "india", "season": "summer" },
      "message": "Hi {name}, the summer kurta collection is live. Curated for the season →"
    },
    {
      "id": "C",
      "targets": { "region": "international" },
      "message": "Hi {name}, we ship globally. New arrivals from our summer collection →"
    }
  ]
}
```

### Executor assignment (pure Python, no LLM call):
```python
def assign_variant(customer: Customer, variants: list) -> dict:
    # 1. International customers get their specific variant if it exists
    if customer.region == "international":
        for v in variants:
            if v["targets"].get("region") == "international":
                return v
    # 2. Match on age_group for india customers
    for v in variants:
        ag = v["targets"].get("age_group", "")
        if ag and _age_in_range(customer.age_group, ag):
            return v
    # 3. Fallback to variant A
    return variants[0]

def personalize(variant: dict, customer: Customer) -> str:
    return (variant["message"]
            .replace("{name}", customer.name.split()[0])
            .replace("{city}", customer.city))
```

Season context for Strategist prompt: derived from hemisphere + current month.
India = summer June–Sep, winter Nov–Feb, festive Oct + Mar–May.
International (Sydney/London/Dubai) = opposite or neutral.

---

## 10. Campaign Copilot — Exact UX Flow

This is the step-by-step sequence for the new campaign page (/campaigns/new).

```
Step 1: Marketer is on /campaigns/new
        → Page generates a session_id (uuid) on load

Step 2: Marketer types goal and clicks "Generate"
        → Frontend opens SSE connection to GET /api/campaigns/copilot/stream/:session_id
        → Frontend sends POST /api/campaigns/copilot { goal, session_id }
        → Backend starts LangGraph pipeline async and returns immediately

Step 3: AgentStepper component updates live as SSE events arrive:
        ✓  Audience Analyst    "Found N matching customers"
        ⟳  Campaign Strategist "Searching fashion trends..."
        ○  Preparing variants

Step 4: proposal_ready SSE event fires
        → ProposalCard renders with:
           - Segment: name, count, filter chips (editable)
           - Channel: recommended (selectable)
           - Message variants A/B/C with targeting info (editable text)
           - AI reasoning text
           - Trend highlights from Tavily

Step 5: Marketer reviews, optionally edits filter chips / message text / channel
        → PUT /api/segments/:id fires if rules change (recalculates count live)

Step 6: Marketer clicks "Approve and Launch"
        → POST /api/campaigns (saves draft with all proposal data)
        → POST /api/campaigns/:id/launch (executes)
        → Redirect to /campaigns/:id

Step 7: /campaigns/:id page opens SSE to GET /api/campaigns/:id/stream
        → EventFeed and KPI cards update live as callbacks arrive
        → campaign_complete event fires → insight summary renders
```

---

## 11. Campaign Analytics Coverage

This covers the assignment's "surface communication performance insights" requirement.

### Campaign detail page (/campaigns/:id)
```
KPI row:    Sent | Delivered | Failed | Read (%) | Clicked (%) | Orders | Revenue
Funnel:     Visual bars showing sent → delivered → read → clicked → orders
Variants:   Per-variant breakdown (see below)
Event feed: Last 20 delivery events, live
AI summary: Plain-English paragraph generated on campaign completion
```

### Variant breakdown (per-variant stats on campaign detail):
```
Variant A  ({targeting})   sent: N   read: X%   clicked: Y%   orders: Z
Variant B  ({targeting})   sent: N   read: X%   clicked: Y%   orders: Z
Variant C  ({targeting})   sent: N   read: X%   clicked: Y%   orders: Z
```
Query: GROUP BY variant_id on communications table. No new tables needed.

This is also what populates campaign_learnings per-variant — the foundation of the
feedback loop and the "A/B testing" narrative.

### Segment detail page (/segments/:id)
Covers the assignment's "audience level" performance requirement.
```
Customers:    Paginated list of customers in this segment (current count)
Performance:  Aggregate stats across all campaigns ever sent to this segment:
              avg read rate | avg click rate | avg order rate | total campaigns
```
One derived query, no new table:
```sql
SELECT COUNT(*) as total_sent,
  AVG(CASE WHEN c.status IN ('read','clicked','order_attributed') THEN 1.0 ELSE 0 END) as avg_read,
  AVG(CASE WHEN c.status IN ('clicked','order_attributed') THEN 1.0 ELSE 0 END) as avg_click,
  AVG(CASE WHEN c.status = 'order_attributed' THEN 1.0 ELSE 0 END) as avg_order,
  COUNT(DISTINCT c.campaign_id) as campaigns_run
FROM communications c
JOIN campaigns camp ON c.campaign_id = camp.id
WHERE camp.segment_id = :segment_id
```

---

## 12. Campaign Learnings — Feedback Loop

Written after every campaign completion. One row per campaign.

```python
await write_learning({
    "campaign_id":          campaign.id,
    "segment_description":  campaign.goal,
    "channel":              campaign.channel,
    "message_style":        infer_style(campaign.message_variants),
    "open_rate":            reads / delivered  if delivered > 0 else 0,
    "click_rate":           clicks / reads     if reads > 0 else 0,
    "order_rate":           orders / clicks    if clicks > 0 else 0,
    "customer_count":       total_sent
})
```

`infer_style()` does simple keyword matching on variant messages:
festive ← diwali/festival/celebrate/occasion
urgent  ← limited/hours/ends/last chance
emotional ← miss/back/thinking/personal
informational ← (default)

### Injected into Strategist system prompt (top 5 most recent):
```
Past campaign performance for reference:
- "{segment_description}" → {channel} → {style} → {read_rate}% read, {order_rate}% orders (n={count})
...
Use this to inform your channel and message tone recommendation.
If no past data is relevant, proceed without it.
```

### Pre-seeded learnings
Seed a set of synthetic campaign_learnings rows in seed.py so the
Strategist has historical context from the very first demo run.
Specific values to be defined in the seed data document.

---

## 13. In-Memory SSE Queue Design

```python
# backend/services/sse_bus.py
import asyncio
from typing import Dict

# Module-level dict: session_id → asyncio.Queue
_queues: Dict[str, asyncio.Queue] = {}

def create_queue(session_id: str) -> asyncio.Queue:
    q = asyncio.Queue()
    _queues[session_id] = q
    return q

async def publish(session_id: str, event: dict):
    if session_id in _queues:
        await _queues[session_id].put(event)

def cleanup(session_id: str):
    _queues.pop(session_id, None)
```

SSE endpoint reads from queue and formats as text/event-stream.
Scale note: at production scale, replace with Redis pub/sub so multiple
backend instances can all push to the same session.

---

## 14. Segment Engine

```python
# backend/services/segment_engine.py
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import cast
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy import String

def build_query(filter_rules: dict, db: Session):
    from models.db import Customer
    q = db.query(Customer)
    for rule in filter_rules.get("rules", []):
        col = getattr(Customer, rule["field"], None)
        if col is None:
            continue
        op, val = rule["op"], rule["value"]
        if   op == "gt":          q = q.filter(col >  val)
        elif op == "lt":          q = q.filter(col <  val)
        elif op == "gte":         q = q.filter(col >= val)
        elif op == "lte":         q = q.filter(col <= val)
        elif op == "eq":          q = q.filter(col == val)
        elif op == "neq":         q = q.filter(col != val)
        elif op == "in":          q = q.filter(col.in_(val))
        elif op == "lt_days_ago": q = q.filter(col < datetime.now() - timedelta(days=val))
        elif op == "gt_days_ago": q = q.filter(col > datetime.now() - timedelta(days=val))
        elif op == "contains":    q = q.filter(col.contains(val))  # TEXT[] @> operator
    return q
```

---

## 15. Seed Data

TODO — to be defined separately.

Seed data must cover: customers, orders, pre-built segments, and
pre-seeded campaign_learnings rows (so the Strategist has historical
context from the first demo run).

The seed script lives at backend/db/seed.py and is the only place
sample data is defined.

---

## 16. Attribution Model

**Decision: last-click attribution, 24-hour window.**

Rationale: Industry standard for WhatsApp/SMS D2C campaigns. MoEngage (Xeno's
direct competitor) uses an 18-hour window for WhatsApp. We use 24-hour for
conservatism. WhatsApp messages are read within 5 minutes 80% of the time —
conversions happen fast.

Implementation: channel service fires `order_attributed` event for 30% of
`clicked` communications after 30–180s simulated delay. Revenue stored on
the communication row as `attributed_revenue`.

State explicitly in walkthrough video.

---

## 17. Campaign "Completed" Trigger

A campaign transitions `running → completed` when EITHER:
- All communications have reached a terminal status (delivered/failed + any
  post-delivery events have had enough time to fire)
- 5 minutes have elapsed since `launched_at` (catch-all for stragglers)

Implemented as a background task that polls every 30s for running campaigns.

On completion:
1. Write row to `campaign_learnings`
2. Generate AI insight summary (one Claude call with final stats)
3. Push `campaign_complete` SSE event
4. Set `campaign.completed_at` and `campaign.status = 'completed'`

---

## 18. Scale Assumptions (for walkthrough video)

This system is designed for demo scale: ~200 customers, single-digit concurrent campaigns.

**Explicitly state these tradeoffs in the video:**

| Current (demo) | At scale |
|---|---|
| In-memory asyncio.Queue for SSE | Redis pub/sub |
| Direct HTTP from channel → CRM | SQS/Kafka queue + consumer |
| Derive stats from communications table | Materialized view or stats table |
| Single FastAPI process | Worker pool (Celery/ARQ) |
| No rate limiting on dispatch | Per-campaign dispatch throttle |
| In-memory dead letter list | Monitored SQS DLQ + alerting |

---

## 19. Environment Variables

### backend/.env
```
DATABASE_URL=postgresql://user:pass@host:5432/xenion_crm
GOOGLE_API_KEY=your-google-api-key-here
TAVILY_API_KEY=tvly-...
CHANNEL_SERVICE_URL=https://channel-service.up.railway.app
RECEIPTS_CALLBACK_URL=https://crm-backend.up.railway.app/api/receipts
```

### channel-service/.env
```
CRM_RECEIPTS_URL=https://crm-backend.up.railway.app/api/receipts
PORT=8001
```

### frontend/.env.local
```
NEXT_PUBLIC_API_URL=https://crm-backend.up.railway.app
```

---

## 20. What Is Explicitly Out of Scope

State all of this in your walkthrough video as conscious decisions:

- Authentication / user accounts
- Real messaging provider integration (WhatsApp Business API, Twilio, etc.)
- Campaign scheduling / recurring campaigns
- A/B test infrastructure (variant performance data IS tracked and fed to learnings)
- Multi-tenant / workspace support
- CSV import UI (ingestion via POST /api/ingest + seed script)
- Campaign throttling / send-time optimisation
- Unsubscribe handling
- Rich HTML email templates


## 21. Model Routing

The following modules have subtle correctness requirements where a wrong
implementation produces no error but broken behaviour. Use Sonnet or above.
GLM-5 handles everything else.

### Sonnet-required files

**agents/**
- `graph.py` — LangGraph node wiring and state transitions. Wrong edge
  connections fail silently or produce incomplete proposals with no exception.

**api/**
- `receipts.py` — status state machine (queued → sent → delivered → ...).
  Must reject downgrades with 409, must be idempotent on duplicate events.
  GLM will likely implement a simple setter instead of a validated transition.

**services/**
- `sse_bus.py` — asyncio.Queue lifecycle. Queue must exist before POST /copilot
  fires or events are lost silently. Cleanup timing matters.
- `campaign_service.py` — completion trigger logic (all-terminal check + 5-min
  catch-all). Wrong condition leaves campaigns stuck in 'running' permanently.

### GLM-5 handles everything else
All models, migrations, dashboard/customers/segments API, segment engine,
channel service, frontend, seed data, deployment config.