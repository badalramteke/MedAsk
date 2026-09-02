# TODO

## Current phase focus
- `[x]` Phase 0: Foundation setup and audit
- `[x]` Phase 1: Core data contract and session foundation
- `[x]` Phase 2: Question Engine Skeleton (rule-based, no AI)
- `[x]` Phase 3: MedGemma and ModelService integration
- `[x]` Phase 4: LangGraph clinical workflow and safety rules
- `[x]` Phase 5: Summary Generator
- `[x]` Phase 6: API layer completion
- `[x]` Phase 7: Voice Intake Engine (Module E)
- `[x]` Phase 8: Medical Document Digitization (Module B)

## Phase 9 Tasks (Next Up: Consent, FHIR, ABDM, and HIS Integration — Module D)
- `[ ]` Review `docs/integrations/ABDM_FHIR_SPEC.md` and NRCeS FHIR R4 profile specifications.
- `[ ]` Implement validated FHIR R4 mapping from `PatientDataObject` (Composition, Patient, Encounter, Condition, MedicationStatement, Observation, DiagnosticReport, DocumentReference, Procedure).
- `[ ]` Implement granular, revocable, audio-guided consent state machine and evidence capture.
- `[ ]` Build mock ABDM / HIS delivery adapters (prepared, queued, accepted, rejected, failed states).
- `[ ]` Implement secure session termination with automatic clearing of temporary data upon confirmed submission.
- `[ ]` Add automated pytest suite for FHIR serialization and ABDM delivery lifecycle.

## Future Phases
- `[ ]` Phase 9: Consent, FHIR, ABDM, and HIS integration (Module D)
- `[ ]` Phase 9: Consent, FHIR, ABDM, and HIS integration (FHIR R4 Bundle `Composition` generator)
- `[ ]` Phase 10: Backend integration testing
- `[ ]` Phase 11: Frontend patient flow (Next.js Kiosk UI)
- `[ ]` Phase 12: Frontend clinician and triage flow (`/doctor` portal)
- `[ ]` Phase 13: UI accessibility and polish
- `[ ]` Phase 14: Hackathon demonstration and MVP validation
- `[ ]` Phase 15: Hospital pilot and production readiness.

## Notes
- Update this file immediately when a task is completed or a new blocker is found.
