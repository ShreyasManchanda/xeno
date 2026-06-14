<!-- v1.0 | propose changes in chat before editing -->

# frontend/components/CLAUDE.md

## Owns
All reusable UI components, organised by feature:
dashboard/  → NudgeCard, KPICards
segments/   → FilterChips, NLCreator
campaigns/  → AgentStepper, ProposalCard, DeliveryFunnel, VariantBreakdown, EventFeed
shared/     → Sidebar, StatusBadge
ui/         → shadcn/ui installed components only

## Does not
- Make API calls — receives data as props from app/ pages
- Manage SSE connections — receives events as props or via hook passed down
- Make routing decisions — uses Next.js Link or router passed as prop
- Define TypeScript types — consumes from lib/types.ts

## Contracts
Receives from: app/ pages (props — data and event callbacks)
Receives from: lib/types.ts (type definitions)
Produces for: app/ pages (rendered JSX)
Shared contract: all prop types reference lib/types.ts interfaces
Must not import: lib/api.ts, lib/sse.ts (those belong in app/ pages)

## Decisions
- FilterChips edits AI-generated segment filter_rules in-place — this is the
  manual fallback per SPEC.md §5 PUT /api/segments/:id. Each chip maps to one
  rule object in the filter_rules.rules array.
- AgentStepper maps agent_start, agent_stream, agent_progress, agent_complete
  SSE events to three visual states with live token preview during LLM calls.
- EventFeed shows last 20 comm_event SSE events — keeps DOM bounded, no
  virtualisation needed at demo scale per SPEC.md §14.
- ProposalCard is the human review gate per SPEC.md §10 step 4 — it must
  allow editing of segment rules, message text, and channel before approve.

---
Pending: none
Changelog: v1.0 Jun 2026 initial