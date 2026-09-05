# MediKiosk AI Context

Purpose: Is the primary AI-session entry point for MediKiosk; read it and the referenced memory files before making any change.

## Project

- MediKiosk (SIH26047, Ministry of Ayush / AIIA) is a patient-facing digital clinical-intake platform for hospital OPDs.
- It structures voice/touch history, digitizes patient-provided records, generates a clinician-editable summary, and supports consented HIS/ABDM hand-off.
- Source of truth: `ps.md`, `docs/product/PRD.md`, and `docs/architecture/TECH_STACK.md`.

## Current scope

- Module A: conversational history, AYUSH mode, and red-flag staff alerts.
- Module B: document digitization and chronology.
- Module C: bilingual confirmation and clinician-editable summary draft.
- Module D: consent plus permitted ABHA/ABDM/FHIR/HIS integration.
- `docs/product/FUTURE.md` is out of scope until an idea is explicitly moved to the PRD and approved.

## Hard rules

- Never generate autonomous diagnosis, treatment advice, prescriptions, final records, or autonomous triage decisions.
- Preserve the clinician-editable draft and triage-staff authority boundaries.
- Use PatientDataObject for all module communication, plugin interface/manifest for extensions, and ModelService for all model calls.
- Do not invent clinical rules, ABDM/HIS/Bhashini API behavior, legal conclusions, credentials, or performance results.
- Keep secrets/configuration outside source code and do not expose PHI in routine logs, fixtures, or prompts beyond minimum need.

## Memory workflow

- Begin by reading `memory/HANDOFF.md`, `CURRENT_STATE.md`, `ACTIVE_WORK.md`, `DECISIONS.md`, and `RULES.md`.
- Preserve approved decisions and update memory with actual completed work, active work, blockers, and handoff context at the end of meaningful sessions.

## Memory files

- `CURRENT_STATE.md`: current phase and verified status.
- `DECISIONS.md`: approved decisions and rationale.
- `ACTIVE_WORK.md`: active task/state.
- `COMPLETED_WORK.md`: verified completed work.
- `KNOWN_ISSUES.md`: active bugs/blockers.
- `FAILED_APPROACHES.md`: rejected/failed approaches.
- `LESSONS_LEARNED.md`: reusable learnings.
- `TODO.md`: prioritized next actions.
- `HANDOFF.md`: latest transition note.
