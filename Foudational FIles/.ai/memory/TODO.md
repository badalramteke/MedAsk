# TODO

## Current phase focus
- `[x]` Phase 0: Foundation setup and audit
- `[x]` Phase 1: Core data contract and session foundation
- `[x]` Phase 2: Question Engine Skeleton (rule-based, no AI)
- `[x]` Phase 3: MedGemma and ModelService integration
- `[x]` Phase 4: LangGraph clinical workflow and safety rules
- `[x]` Phase 5: Summary Generator
- `[x]` Phase 6: API layer completion

## Phase 7 Tasks (Next Up: Voice Intake Engine — Module E)
- `[ ]` Read `docs/integrations/BHASHINI_ASR.md` and review Bhashini ULCA API specifications.
- `[ ]` Implement Bhashini ASR client (Hindi, English, Marathi, Bengali, Tamil, Telugu) with `.env` credentials.
- `[ ]` Implement local/browser speech recognition & Gemini Audio fallback for speech-to-text.
- `[ ]` Implement Bhashini TTS client for localized patient audio guidance.
- `[ ]` Build `/api/v1/voice/transcribe` and `/api/v1/voice/synthesize` endpoints.
- `[ ]` Implement dual-mode voice + touch continuous fallback.

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
