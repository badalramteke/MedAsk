# Rules

## The AI Update Cycle System (CRITICAL)
Every AI agent operating in this repository MUST follow this strict cycle for every task to ensure state is never lost:
1. **Pre-Flight (MANDATORY before any work):**
   - Read `.ai/memory/CURRENT_STATE.md`, `TODO.md`, `ACTIVE_WORK.md`, and `DECISIONS.md`.
   - **ALWAYS read `PS.md` and `docs/product/PRD.md` before starting any new phase or major task.** These are the ground truth for what MediKiosk is, who it serves, and what each module does. Missing details from these files leads to wrong architectural decisions.
   - Read the specific foundational file mapped in the "Anti-Hallucination Source of Truth Mapping" section below for the type of work being done.
2. **Execution:** Do the requested work.
3. **Post-Flight:** Before ending your turn, you MUST:
   - Update `CHANGELOG.md` if material files or features were added/changed.
   - Update `.ai/memory/CURRENT_STATE.md` to reflect what is actually built and working.
   - Update `.ai/memory/TODO.md` to check off completed items and add new blockers.
   - Update `.ai/memory/ACTIVE_WORK.md` to reflect the next immediate focus.
   - Update `.ai/memory/COMPLETED_WORK.md` with finished deliverables.
   - Update `.ai/memory/KNOWN_ISSUES.md`, `FAILED_APPROACHES.md`, and `LESSONS_LEARNED.md` if any bugs were found, paths rejected, or architectural lessons gained.
   - If a Phase was completed, generate a `docs/retrospectives/PHASE_X_RETROSPECTIVE.md`.

## Anti-Hallucination Source of Truth Mapping
Before writing any code or making implementation decisions, you MUST consult the appropriate foundational document to prevent hallucination. Use the following mapping:

- **Overall Scope & Features:** Read `ps.md` and `docs/product/PRD.md`
- **Frontend & Routes:** Read `docs/architecture/PATHS.md` and `docs/product/MODULES.md`
- **Backend Architecture & Tech Stack:** Read `docs/architecture/TECH_STACK.md` and `docs/architecture/BACKEND_ARCHITECTURE.md`
- **Data Models & Database:** Read `docs/database/PATIENT_DATA_OBJECT.md` and `docs/database/SCHEMA.md`
- **API Contracts:** Read `docs/api/API_CONTRACTS.md` and `docs/api/ERROR_CODES.md`
- **AI Prompts & Model Abstraction:** Read `docs/ai/MODEL_ABSTRACTION.md` and `docs/ai/PROMPT_LIBRARY.md`
- **Clinical Protocols & Triage:** Read files in `docs/clinical/` (e.g., `CLINICAL_SAFETY.md`, `RED_FLAG_RULES.md`) and check JSON schemas in `data/clinical/`
- **Integrations (ABDM, HIS, Bhashini):** Read the specific file in `docs/integrations/`
- **Plugin Architecture:** Read `docs/architecture/PLUGIN_INTERFACE.md`

**Rule:** If a detail is missing from the designated foundational file, DO NOT hallucinate it. Treat it as unknown and ask the user for clarification.

## Hard rules
- Never hardcode secrets, API keys, tokens, or credentials in code, config files, or notes.
- Do not perform autonomous medical diagnosis or claim clinical judgment beyond approved project documentation.
- Never bypass PatientDataObject as the source of truth for patient data and workflow state.
- No direct database access from routes, services, or handlers; keep persistence behind the planned data layer.
- Preserve the plugin architecture; do not fold plugin logic into route-level code or bypass interfaces.
- Do not invent missing APIs, endpoints, payloads, or integrations.
- Never assume ABDM or FHIR behavior without explicit documentation or human confirmation.
- If clinical terminology, medical safety, or protocol details are uncertain, ask before proceeding.
- Frontend Element Attribute Rule: Every interactive/identifiable frontend UI element must include `data-element`, `data-voice-action`, `data-testid`, `id`, and `aria-label`.
- Frontend Route Catalog Rule: All frontend routes and pages must be documented in `docs/architecture/PATHS.md`.
- Follow the .ai memory workflow at the start and end of every session.
- Keep .ai changes limited to memory and agent context; do not write project documentation here.

## Do not invent
- No fabricated endpoint behavior.
- No guessed clinical rules.
- No assumed integration contracts.
- No hidden assumptions about hospital systems, ABDM flows, or compliance behavior.
- If something is unclear, treat it as unknown and ask instead of guessing.

