<!-- v1.1 | useSSE on copilot page, streaming agent UI -->

# frontend/app/CLAUDE.md

## Owns
All Next.js route segments. layout.tsx with Sidebar. Pages:
/ (dashboard), /customers, /customers/[id], /segments, /segments/new,
/segments/[id], /campaigns, /campaigns/new, /campaigns/[id].
Each segment should have loading.tsx and error.tsx.

## Does not
- Implement data fetching logic — delegates to lib/api.ts
- Implement component logic — delegates to components/
- Manage SSE connections directly — delegates to lib/sse.ts via useSSE

## Contracts
Receives from: lib/api.ts (fetched data), lib/sse.ts (streamed events)
Receives from: components/ (rendered JSX)
Produces for: browser (rendered pages)
Shared contract: route structure matches SPEC.md §3 folder structure exactly
Must not import: fetch() directly, EventSource directly, anything from backend/

## Decisions
- /campaigns/new is fully 'use client' — uses useSSE for copilot stream.
- SSE stream must open before POST /api/campaigns/copilot fires (SPEC §10 step 2).
- proposal_ready payload is normalized in page before passing to ProposalCard.
- Marketer goal is stored in component state and passed on campaign create.

---
Pending: none
Changelog: v1.0 Jun 2026 initial | v1.1 Jun 2026 useSSE copilot, goal/trend_context on approve