# Lessons Learned

## Engineering & Architecture
- **Pydantic Validation is AI Armor:** Generating Pydantic schemas directly from clinical JSON standards (like `SOCRATES` or `Dashavidha Pariksha`) forces the AI into a structured path. If the AI hallucinates, Pydantic immediately catches it at the API boundary before it reaches the database.
- **Mock Repositories Speed Up Iteration:** Building a `SessionRepository` interface with an in-memory dictionary backing allowed us to test the FastAPI routes immediately in Phase 1 without having to wait for the Postgres schema migrations in Phase 3.
- **followup_triggers are the branching backbone:** The `followup_triggers` mechanism in the clinical JSON datasets (e.g., VALUE_MATCH, ALWAYS) is the single source of branching truth for the question engine. The Python FlowController never hardcodes question ordering — it delegates entirely to the JSON data. This means adding new question sequences only requires editing JSON, not Python.

## Phase 4: LangGraph Clinical Workflow & Safety Rules

### 1. LangGraph Cyclic Edge Evaluation
**Context:** The `StateGraph` requires explicit conditional logic to pause execution and wait for user input without causing an infinite loop.
**Lesson Learned:** Returning `END` from conditional edges effectively halts execution. However, injecting `update_state` directly using the dictionary (without `as_node`) forces LangGraph to re-evaluate the conditional edge of the node that last executed rather than re-running the node itself.
**Best Practice:** When bridging a REST API with LangGraph, perform input-dependent domain logic (like chief complaint domain mapping) in the API endpoint *before* `update_state`, or explicitly pass `as_node` if you want the node to re-run from the top.

### 2. TypedDict Default Reducers
**Context:** Returning a partial dictionary from a node update.
**Lesson Learned:** Without an explicit `Annotated` reducer (like `operator.add`), LangGraph's default behavior for a standard `TypedDict` is to *replace* the key's value entirely. This cleanly works for state updates but requires care not to overwrite nested fields inadvertently.

## Phase 6: API Layer Completion & Multi-Router Architecture
- **Substring Chief Complaint Matching:** Exact dictionary key lookup (`CHIEF_COMPLAINT_TO_DOMAIN.get(text)`) failed on real user inputs such as `"Chest pain for 2 hours"` or `"Severe chest pain"`. Switching to a case-insensitive substring search across canonical domain triggers made the conversational routing robust and clinician-like.
- **FastAPI python-multipart Requirement:** Using `UploadFile` in FastAPI endpoints requires explicit installation of `python-multipart`. Adding this to `requirements.txt` is essential for containerized environments.
- **Global Triage Alert Synchronicity:** When a red flag is triggered in the LangGraph state machine, it must be mapped immediately to the global `alert_repo` with proper field names (`rule_id` -> `flag_id`, `urgency_level` -> `severity`). Any field mismatches inside an unhandled exception block can cause alerts to silently disappear from the staff dashboard.
- **SSE Stream Ingress Keep-Alive:** Streaming LLM tokens/events via `text/event-stream` completely bypasses edge proxy timeouts and provides instant visual progress feedback to users on slow mobile networks.

## Workflow & Memory
- **Rigid Documentation Pays Off:** The Phase 0 file-by-file audit caught minor mismatches between `ROADMAP.md` and `PHASES.md` early. Fixing these before writing code prevented future scope drift.
- **Automated Memory Cycling:** The AI update cycle (Pre-Flight/Post-Flight) ensures that context is never lost across sessions, which is vital for long-running agentic tasks.
- **Always read PS.md + PRD.md first:** In Phase 2 planning, we initially missed that the problem statement is FROM the Ministry of AYUSH/AIIA, which fundamentally changes the architectural understanding of AYUSH deployment. This was caught only after explicitly re-reading PS.md. The lesson: never start a phase without re-reading the original problem statement and PRD.

