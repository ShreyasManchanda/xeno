<!-- v1.1 | agent_stream + agent_progress SSE types -->

# frontend/lib/CLAUDE.md

## Owns
api.ts   — every HTTP call to the backend, organised by resource
sse.ts   — useSSE hook (EventSource lifecycle, typed event dispatch)
types.ts — all shared TypeScript interfaces and enums

## Does not
- Render any UI
- Contain business logic beyond request shaping
- Define component-local types — those stay co-located with their component

## Contracts
Receives from: SPEC.md §5 (all endpoint definitions) and §6 (SSE schemas)
Produces for: frontend/app/ (data and event streams), frontend/components/ (types)
Shared contract: types.ts is the single source of truth for all frontend types
Must not import: React, Next.js router (pure utility layer, no framework deps)

## Decisions
- All endpoints centralised in api.ts — prevents route drift from SPEC.md §5.
- useSSE in sse.ts closes EventSource on component unmount.
- Copilot SSE types include agent_stream (token deltas) and agent_progress
  (non-LLM status updates) in addition to SPEC §6 base events.
- ProposalData mirrors backend proposal_ready flat shape (segment_name,
  segment as FilterRules, customer_count at root, trend_context).

---
Pending: none
Changelog: v1.0 Jun 2026 initial | v1.1 Jun 2026 streaming SSE types, ProposalData shape