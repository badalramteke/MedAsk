# Lessons Learned

## Engineering & Architecture
- **Pydantic Validation is AI Armor:** Generating Pydantic schemas directly from clinical JSON standards (like `SOCRATES` or `Dashavidha Pariksha`) forces the AI into a structured path. If the AI hallucinates, Pydantic immediately catches it at the API boundary before it reaches the database.
- **Mock Repositories Speed Up Iteration:** Building a `SessionRepository` interface with an in-memory dictionary backing allowed us to test the FastAPI routes immediately in Phase 1 without having to wait for the Postgres schema migrations in Phase 3.
- **followup_triggers are the branching backbone:** The `followup_triggers` mechanism in the clinical JSON datasets (e.g., VALUE_MATCH, ALWAYS) is the single source of branching truth for the question engine. The Python FlowController never hardcodes question ordering — it delegates entirely to the JSON data. This means adding new question sequences only requires editing JSON, not Python.

## Workflow & Memory
- **Rigid Documentation Pays Off:** The Phase 0 file-by-file audit caught minor mismatches between `ROADMAP.md` and `PHASES.md` early. Fixing these before writing code prevented future scope drift.
- **Automated Memory Cycling:** The AI update cycle (Pre-Flight/Post-Flight) ensures that context is never lost across sessions, which is vital for long-running agentic tasks.
- **Always read PS.md + PRD.md first:** In Phase 2 planning, we initially missed that the problem statement is FROM the Ministry of AYUSH/AIIA, which fundamentally changes the architectural understanding of AYUSH deployment. This was caught only after explicitly re-reading PS.md. The lesson: never start a phase without re-reading the original problem statement and PRD.
