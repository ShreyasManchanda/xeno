<!-- v1.0 | propose changes in chat before editing -->

# channel-service/CLAUDE.md

## Owns
main.py      — FastAPI app with one route: POST /send
simulator.py — async delivery simulation logic and callback firing with retry

## Does not
- Store persistent state — stateless by design, no DB, no file writes
- Know about customers, segments, or campaigns — works only with communication_id
- Make LLM calls
- Import anything from backend/ — separate deployment

## Contracts
Receives from: backend/api/campaigns.py (POST /send per SPEC.md §7 request schema)
Produces for: backend/api/receipts.py (POST /api/receipts per SPEC.md §7 callback schema)
Shared contract: event names and payload shapes in SPEC.md §7 — both services
  must match; a mismatch here silently breaks delivery tracking
Must not import: any backend/ module, any models, any DB libraries

## Decisions
- Simulation probabilities are in simulator.py matching SPEC.md §7 — change
  them in the spec first, then update here to stay in sync.
- POST /send returns 200 immediately and runs simulation as a FastAPI
  BackgroundTask — keeps CRM launch fast; simulation delay is async.
- Callback retry uses exponential backoff with jitter, max 3 attempts, then
  appends to an in-memory dead_letter list — per SPEC.md §7. No persistence
  because the service is stateless; lost callbacks show as non-delivered comms.
- Stateless by design — multiple instances can run in parallel without
  coordination, which matters if Railway scales the service horizontally.

---
Pending: none
Changelog: v1.0 Jun 2026 initial