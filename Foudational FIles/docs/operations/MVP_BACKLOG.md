# MVP Backlog

Purpose: Prioritizes the current-scope work required for a MediKiosk prototype/MVP; read before selecting implementation work.

## Must-have foundation implementation

- Patient kiosk flow with consent, language selection, and voice/touch parity.
- Module A: structured history intake, approved question-flow boundary, and red-flag staff-alert lifecycle.
- Module B: permitted document capture, extraction candidates, provenance, and timeline.
- Module C: clinician-editable structured draft and patient-facing local-language confirmation path.
- Module D: consent-state enforcement, mock/approved FHIR-HIS/ABDM hand-off, and truthful delivery states.
- PatientDataObject, plugin manifest/interface, ModelService, model/provider adapters, and validation.
- Security/privacy controls: no hardcoded secrets, minimum-data handling, safe logging, session lifecycle, access controls.
- Tests using synthetic/de-identified data for core workflow, failure conditions, safety boundaries, and accessibility.

## Required demonstration evidence

- A patient can complete a representative intake via touch if voice fails.
- A clinician can inspect and edit/reject a generated draft.
- A triage alert reaches the configured demo recipient and records acknowledgement state.
- A document is extracted into source-linked candidates without unsupported inference.
- A mock external delivery visibly reports simulated/queued/failed/accepted state truthfully.

## Not in this backlog

- Autonomous clinical decisions, physical hardware, HIS replacement, production ABDM certification, and all `FUTURE.md` ideas.

→ For scope, see `docs/product/SCOPE.md`.

## Open Questions

- Prioritized tickets, owner assignment, estimates, exact demo scenarios, and hackathon judging criteria are pending.
