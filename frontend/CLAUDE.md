<!-- v2.0 | Complete redesign - dark mode, new palette, motion library -->

# frontend/CLAUDE.md

## Owns
Next.js 14 App Router application deployed to Vercel.
app/ — all route segments and pages
components/ — all reusable UI components
lib/ — api.ts, sse.ts, types.ts

## Design Contract
READ frontend/DESIGN.md before implementing any UI component.
- **Dark mode default**: `bg-dark-bg (#0A0A0B)` with glassmorphic cards
- **Typography**: Geist Display for wordmark, Inter for UI, Fraunces for serif moments
- **Accent colors**: Crimson/Red (`#DC2626`) on dark mode, Blue (`#3B82F6`) on light mode
- **One accent per theme**: No mixed temperature colors
- **Motion**: `motion` library for spring physics, `prefers-reduced-motion` honored
- **Cards**: Glassmorphic with top highlight (`inset 0 1px 0 rgba(255,255,255,0.04)`), NO outer glows

## Does not
- Contain business logic or data transformation beyond display formatting
- Call fetch() directly — all HTTP goes through lib/api.ts
- Manage SSE connections outside lib/sse.ts useSSE hook
- Know about backend internals, agent architecture, or DB schema
- Use localStorage, sessionStorage, or any browser storage

## Contracts
Receives from: backend/api/ via HTTP (shapes in SPEC.md §5)
Receives from: backend/api/ via SSE stream (shapes in SPEC.md §6)
Produces for: end user (browser)
Shared contract: lib/types.ts — all frontend types live here
Must not import: anything from backend/, channel-service/, or models/

## Decisions
- **Dark mode first**: Layout sets `className="dark"` on `<html>`, all pages designed for dark
- **Motion library**: `npm install motion` — use spring physics, not CSS transitions for hover states
- **Sidebar**: Glassmorphic (`backdrop-blur-xl`, `bg-white/[0.03]`) with spring hover on nav items
- **Broken grids**: KPI cards use unequal layout — one hero metric (col-span-2, row-span-2), others subordinate
- **Typography hierarchy**: "Good evening" smaller (16px), brand name larger serif italic moment (40px+)
- **Grain overlay**: `z-index: 1` (NOT 9999), `pointer-events: none`, sits below modals
- Server components by default; 'use client' only when state or browser events needed

---
Pending: none
Changelog: v1.0 Jun 2026 initial | v1.1 Jun 2026 added DESIGN.md integration | v2.0 Jun 2026 complete redesign (dark mode, motion, new palette)
