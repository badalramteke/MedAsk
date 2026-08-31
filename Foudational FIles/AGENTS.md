# MediKiosk Agent Guide

Purpose: Gives any AI or automation agent the mandatory working rules for MediKiosk; read before inspecting, editing, planning, or implementing work.

## Start here

1. Read `.ai/CONTEXT.md`.
2. Read `.ai/memory/HANDOFF.md`, `CURRENT_STATE.md`, `ACTIVE_WORK.md`, `DECISIONS.md`, and `RULES.md`.
3. Read `ps.md`, `docs/product/PRD.md`, and `docs/architecture/TECH_STACK.md` for product source of truth.
4. Check `docs/product/FUTURE.md`; it is context for extensibility only, never implementation scope.

## Scope guardrails

- Build only Modules A–D: conversational history, document digitization, summary generation, and consent/ABDM integration.
- Never implement an idea from `FUTURE.md` unless it is explicitly approved and moved to `PRD.md`.
- Do not create autonomous diagnosis, treatment advice, prescriptions, final clinical records, or autonomous triage decisions.
- The clinician owns final summary review; triage staff own response to alerts.

## Architecture guardrails

- Use PatientDataObject as the sole inter-module data contract.
- Implement all modules/adapters through the shared plugin interface; plugins communicate only through PatientDataObject.
- Future approved capabilities must be new plugins with their own namespace/manifest entry—without changing core modules, central routing, or stable core fields.
- Route handlers stay thin; no direct database, FHIR, clinical-policy, or model-provider calls.
- All AI calls use ModelService; provider SDKs are isolated behind adapters.
- Use configuration/environment variables for all secrets, URLs, and provider choice.

## Safety and quality guardrails

- Preserve provenance, uncertainty, patient wording, and clinician editability.
- Treat all patient/document/model content as untrusted until validated.
- Do not invent clinical protocols, ABDM behavior, endpoints, credentials, legal status, or measured performance results.
- Use authoritative sources for time-sensitive clinical, legal, integration, or standards claims and cite them in documentation.
- Update memory files at the end of a meaningful work session with actual—not planned—state.

→ For detailed rules, see `.ai/memory/RULES.md`.
→ For architecture, see `docs/architecture/`.

## Open Questions

- Repository branch/review automation and implementation toolchain are pending.
