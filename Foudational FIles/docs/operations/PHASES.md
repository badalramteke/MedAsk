# Delivery Phases

Purpose: Defines MediKiosk’s backend-first delivery plan from the approved solution overview; read before planning, implementing, or accepting work.

## Solution coverage requirement

Every phase contributes to the approved patient journey:

```text
Identify + consent -> voice/touch history -> red-flag staff alert -> document scan
-> structured editable summary -> physician review -> consented FHIR/HIS/ABDM hand-off
```

The delivery plan must cover all four current modules:

| Module | Required delivered capability |
| --- | --- |
| A — Conversational History Engine | Voice/touch interview, adaptive HPI/ROS, SOCRATES where applicable, AYUSH/Dashavidha and Ahara-Vihara capture, red-flag staff alert |
| B — Document Digitization | Permitted prescription/lab/discharge-summary capture, multilingual printed/handwritten extraction, medications/dosages, investigations/ranges, procedures, chronology, clinician-review flags |
| C — Summary Generator | Standard structured history, bilingual patient confirmation, editable physician draft, accept/amend/reject boundary |
| D — Consent + Integration | ABHA/new-registration entry boundary, granular audio-guided consent, secure session lifecycle, FHIR preparation, truthful HIS/ABDM delivery state |

## Phase 0 — Foundation setup

- Review and lock this foundation documentation baseline.
- Install approved project dependencies and development tooling.
- Create the project structure with separate backend, frontend, plugins, data, integrations, tests, and configuration areas.
- Configure Docker/Docker Compose, PostgreSQL/Supabase development path, Redis, encrypted-artifact storage boundary, `.env` from `.env.example`, synthetic test data, linting, and test scaffolding.
- Run basic MedGemma connectivity/capability checks in the selected development/hackathon environment; do not treat connectivity as clinical validation.

**Exit:** reproducible local setup, dependency lockfiles, documented project structure, baseline checks, and no committed secrets.

## Phase 1 — Core data contract and session foundation

- Implement PatientDataObject core schema, versioned patches, provenance, uncertainty, and namespaced plugin outputs.
- Implement repository/data-service boundaries, basic CRUD required for synthetic sessions, PostgreSQL persistence, and Redis-backed short-lived session state.
- Implement intake session lifecycle, consent-state skeleton, secure temporary-data lifecycle, and audit-safe events.
- Implement mock integration delivery states: prepared, queued, accepted, rejected, and failed.

**Exit:** backend can create, resume, validate, and safely clear synthetic intake sessions without a frontend.

## Phase 2 — Question engine skeleton (rule-based, no AI)

- Implement a static, deterministic question flow for chief complaint, HPI, past history, medication/allergy, family, personal history, ROS, and applicable reproductive history.
- Implement touch-compatible answer options and explicit unknown/refusal/clarification states.
- Implement deterministic branching and completion validation; no LLM-generated questions in this phase.
- Add approved-placeholder AYUSH routing and field capture boundaries without automated AYUSH interpretation.

**Exit:** an API-tested, rule-based synthetic interview produces valid PatientDataObject history updates and proves the workflow skeleton works.

## Phase 3 — MedGemma and ModelService integration

- Implement ModelService and primary MedGemma provider adapters: MedGemma 27B for text tasks where supported and MedGemma 4B for multimodal tasks.
- Connect the text-model path to the question engine for constrained AI follow-up candidates and patient-narration structuring.
- Apply typed output validation, prompt versioning, provenance, uncertainty, consent checks, and no-diagnosis controls.
- Add Gemini/Grok only as configured ModelService fallbacks with identical policy/validation; never as direct business-logic calls.

**Exit:** AI-assisted outputs are validated candidate data, not clinical conclusions, and safe failures preserve the rule-based/touch workflow.

## Phase 4 — LangGraph clinical workflow and safety rules

- Convert stable question flow into LangGraph stateful/cyclic branching without changing PatientDataObject contract.
- Add symptom-specific SOCRATES routing where applicable and configured AYUSH-mode routing for Dashavidha Pariksha and Ahara-Vihara.
- Implement the separate deterministic clinical validator for required-field checks, data quality, uncertainty, and contradictions.
- Implement red-flag evidence extraction plus a versioned deterministic rule engine that sends staff alerts without diagnosing or stopping the interview.

**Exit:** backend workflow supports adaptive questioning, AYUSH routing, validated state checkpoints, and traceable staff-alert lifecycle.

## Phase 5 — Summary generator

- Build Module C from validated PatientDataObject data.
- Generate the standard draft: chief complaint, HPI, past medical/surgical, drug/allergy, family, personal, applicable reproductive history, ROS, and prior-investigations summary.
- Generate patient-facing local-language audio confirmation and physician-facing English/Hindi structured draft.
- Preserve source/provenance/uncertainty and clinician actions: accept, amend, or reject.

**Exit:** backend produces a clinician-editable draft and never commits an autonomous final clinical record.

## Phase 6 — API layer completion

- Complete typed REST and required streaming/WebSocket contracts for session, consent, history, document, summary, alert, and integration workflows.
- Implement safe errors, authorization/consent boundaries, upload validation, idempotency/correlation handling, and health/readiness endpoints.
- Make the complete backend testable through API clients using synthetic/de-identified data.

**Exit:** every implemented backend workflow is API-testable without patient or clinician frontend screens.

## Phase 7 — Voice module: Bhashini ASR/TTS

- Integrate Bhashini through the speech-provider abstraction; configure AI4Bharat fallback only where approved.
- Test voice capture, transcription confirmation, audio prompts, and selected language paths independently.
- Connect voice input to the existing question engine while preserving equivalent touch answers for every question.

**Exit:** voice failure never blocks intake; the touch path remains fully functional and tested.

## Phase 8 — Document digitization module

- Implement permitted document upload/capture, input validation, preprocessing boundary, and source metadata.
- Use MedGemma 4B through ModelService to create source-linked extraction candidates for printed/handwritten prescriptions, lab reports, and discharge summaries.
- Structure diagnoses, medication/dosage, investigation values/reference ranges, and procedure/surgery history; generate chronology with explicit date uncertainty.
- Flag abnormal values and potential drug-interaction candidates only for clinician attention; do not diagnose or provide treatment advice.

**Exit:** document extraction is independently tested, source-attributed, clinician-reviewable, and connected to the summary contract.

## Phase 9 — Consent, FHIR, ABDM, and HIS integration

- Complete granular, revocable, audio-guided consent flow for capture, document processing, draft generation, and permitted sharing.
- Implement approved ABHA/new-registration entry boundary; do not invent identity or ABDM authentication behavior.
- Implement validated FHIR R4 mapping from PatientDataObject and mock delivery adapters first.
- Use ABDM/HIS sandbox only after credentials, target specifications, and permitted test data are available.
- Present truthful delivery state; clear temporary session data after confirmed successful submission, while retaining only minimal encrypted resumable state after a recoverable failure/queue.

**Exit:** consented mock or approved sandbox hand-off is traceable, validated, and never falsely reported as complete.

## Phase 10 — Backend integration testing

- Exercise the complete backend journey through API calls only: identify/consent, voice/touch-compatible history, red-flag alert, document extraction, summary draft, clinician decision state, and FHIR/HIS/ABDM delivery state.
- Test module failure, low-network interruption/resume, idempotent retry, provider fallback, alert-recipient outage, and unsafe AI output.
- Run unit, integration, clinical-safety, security, AI evaluation, and red-team tests using synthetic/de-identified data.

**Exit:** all modules work together without a UI and have documented test evidence, failures, limitations, and release blockers.

## Phase 11 — Frontend patient flow

- Build only the patient interface needed to operate the tested backend APIs: language, consent, voice/touch questions, document capture, confirmation, and truthful status.
- Keep clinical logic, provider calls, consent enforcement, and FHIR construction in the backend.

**Exit:** patient UI drives tested backend contracts and supports the complete non-clinician journey.

## Phase 12 — Frontend clinician and triage flow

- Build physician summary screen with source/uncertainty visibility and accept/edit/reject actions.
- Build triage alert visibility with acknowledgement/clear/escalation state for authorized staff.
- Enforce role/purpose boundaries and audit-safe user actions.

**Exit:** clinician and triage screens preserve human authority and use existing backend contracts.

## Phase 13 — UI accessibility and polish

- Validate icon-driven design, large controls, audio guidance, language support, voice/touch parity, low-literacy usability, and elderly-user accessibility.
- Improve UI clarity and responsive behavior without moving clinical/business/provider logic into the frontend.

**Exit:** documented usability/accessibility evidence and resolved critical UI issues.

## Phase 14 — Hackathon demonstration and MVP validation

- Package a reproducible demonstration using configured local/Colab and/or approved online model paths.
- Clearly label mock HIS/ABDM integrations when sandbox/production credentials are absent.
- Demonstrate all four modules, clinician draft control, triage-staff alert authority, low-network resilience, and truthful delivery state.

**Exit:** reproducible demo, documented limitations, and stakeholder-review evidence.

## Phase 15 — Hospital pilot and production readiness

- Replace mock boundaries only with approved clinical rules, provider accounts, hospital access, retention/access policy, ABDM/HIS sandbox validation, monitoring, backups, recovery, and named operational ownership.
- Complete security, privacy, AI, clinical, accessibility, integration, and operational release gates.
- Scale only after hospital pilot evidence supports readiness.

**Exit:** hospital-approved pilot or production go-live decision.

## Future features

- No `FUTURE.md` idea is an automatic delivery phase.
- A future feature may be planned only after explicit approval and movement into `PRD.md`; it must be implemented as a new plugin without changing the core modules.

→ For detailed scope, see `docs/product/SCOPE.md`.
→ For module boundaries, see `docs/product/MODULES.md`.
→ For testing layers, see `docs/operations/TESTING_STRATEGY.md`.

## Open Questions

- Exact dependency versions, project folder layout, clinical rule approval, target hardware, provider credentials, ABHA/ABDM identity flow, HIS contract, named owners, dates, and phase acceptance thresholds remain pending.
