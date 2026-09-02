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

## Phase 8 Tasks (Next Up: Medical Document Digitization — Module B)
- `[ ]` Review `docs/integrations/OCR_PIPELINE.md` and lab reference range bounds.
- `[ ]` Implement dual-path OCR extraction engine for printed/handwritten prescriptions, lab reports, and discharge summaries.
- `[ ]` Implement entity extractors for medications, dosages, lab tests, reference ranges, and abnormal value flagging.
- `[ ]` Implement MedGemma Multimodal (4B) medical image finding extraction for Chest X-rays, Sonography, and CT scans.
- `[ ]` Implement chronological timelining linking digitized documents to `PatientDataObject.documents`.
- `[ ]` Add automated pytest suite for document parsing and entity extraction.

## Future Phases
- `[ ]` Phase 8: Document digitization module (Dual-path OCR + MedGemma medical image reasoning)
- `[ ]` Phase 9: Consent, FHIR, ABDM, and HIS integration (FHIR R4 Bundle `Composition` generator)
- `[ ]` Phase 10: Backend integration testing
- `[ ]` Phase 11: Frontend patient flow (Next.js Kiosk UI)
- `[ ]` Phase 12: Frontend clinician and triage flow (`/doctor` portal)
- `[ ]` Phase 13: UI accessibility and polish
- `[ ]` Phase 14: Hackathon demonstration and MVP validation
- `[ ]` Phase 15: Hospital pilot and production readiness.

## Notes
- Update this file immediately when a task is completed or a new blocker is found.
