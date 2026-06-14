<!-- v1.1 | Gemini service, streaming SSE, AsyncTavily -->

# backend/agents/CLAUDE.md

## Owns
graph.py  — LangGraph StateGraph definition and compile
state.py  — CampaignState TypedDict (shared across all nodes and calling code)
analyst.py    — AudienceAnalyst node (Gemini via services/gemini.py)
strategist.py — CampaignStrategist node (AsyncTavily then Gemini)
executor.py   — CampaignExecutor node (pure Python, no LLM call)

## Does not
- Handle HTTP routing — graph is invoked from api/campaigns.py
- Manage SSE stream lifecycle — publishes events via services/sse_bus.py
- Call Gemini directly — uses services/gemini.py
- Access DB directly with its own session — receives db session from caller

## Contracts
Receives from: api/campaigns.py (initial CampaignState: goal, session_id, seasons)
Receives from: services/learnings.py (learnings_context string before Strategist)
Produces for: api/campaigns.py (completed CampaignState with assignments)
Produces for: services/sse_bus.py (SSE events during execution)
Shared contract: CampaignState in state.py — imported by api/campaigns.py too
Must not import: api/, models/ directly — DB access via passed db session only

## Decisions
- CampaignExecutor makes no LLM call — variant assignment is deterministic Python per SPEC.md §9.
- Strategist calls AsyncTavilyClient before Gemini — trend context enriches the prompt.
- Analyst skips SSE publish when session_id is "preview" (segments preview API).
- Gemini calls stream tokens via agent_stream SSE when session_id is set (copilot only).
- Executor publishes agent_progress during batch personalization for live UI feedback.
- System prompt templates live in analyst.py and strategist.py node files.

---
Pending: none
Changelog: v1.0 Jun 2026 initial | v1.1 Jun 2026 Gemini service, streaming SSE, richer proposal_ready