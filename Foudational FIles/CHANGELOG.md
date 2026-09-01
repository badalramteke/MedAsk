# Changelog

Purpose: Records user-visible and foundation-level changes to MediKiosk; read before preparing a release or recording a material change.

This project follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) style and uses semantic-version intent where releases are defined.

## [Unreleased]

### Added

- Foundation documentation for architecture, clinical safety, AI, security/privacy, integrations, API/database, product, and operations.
- Empty `docs/product/FUTURE.md` template for explicitly out-of-scope future ideas.
- AI project context and durable memory workflow.
- **Phase 0:** Project directory structure (`backend/`, `frontend/`, etc.), `docker-compose.yml` for Redis/Postgres, `requirements.txt`, and basic MedGemma connectivity checks.
- **Phase 1:** `PatientDataObject` Pydantic schemas (identity, consent, history, ayush, provenance, patch) and basic FastAPI session routing with a mock repository.
- **Retrospectives:** Added auto-generating retrospective files for Phase 0 and Phase 1.
- **Phase 2:** Dynamic rule-based question engine (`backend/app/engine/`), interview state machine with SOCRATES branching, red-flag scanner (13 rules), `questions_general_intake.json` (now 14 questions including female gender-gated Menstrual & Reproductive History in 6 languages), and session API endpoints (`/next-question`, `/answer`, `/alerts`).
- **Phase 3:** Centralized `ModelService` orchestrator (`backend/app/services/model_service.py`), `ColabMedGemmaAdapter` verified LIVE with `google/medgemma-1.5-4b-it` on GPU, `GeminiAdapter`, `MockModelAdapter` fallback cascade, prompt versioning library (`PROMPT_LIBRARY.md`), non-diagnostic safety gating, and session AI endpoints (`/ai/structure-narration`, `/ai/generate-summary`, `/ai/health`).
- **Phase 4:** Migrated clinical intake engine to LangGraph stateful interview graph (`StateGraph`), implemented `ClinicalInterviewState` with nodes for Chief Complaint, SOCRATES, General Intake, Menstrual/Reproductive, and AYUSH Dashavidha Pariksha, and wrapped nodes with automated `RedFlagScanner` triage rules.
- **Phase 5:** Module C Summary Generator (`backend/app/services/prompt_templates.py`, `backend/app/models/ai.py`, `backend/app/api/endpoints/sessions.py`):
  - Built physician-ready draft synthesis with 9 distinct clinical sections matching FHIR R4 `Composition` requirements.
  - Added bilingual audio confirmation script generation (`patient_audio_script_local_lang`) and AYUSH `ayush_summary` support.
  - Implemented Clinician Review actions (`POST /{session_id}/summary/review` supporting `ACCEPTED`, `AMENDED` with section-level patching, and `REJECTED`).
  - Attached automated provenance tracking (`source_type`, `confidence`, `review_status`).
  - Verified LIVE inference with `google/medgemma-1.5-4b-it` on Google Colab GPU for both structured clinical summary synthesis and multimodal Chest X-ray image analysis (`/api/v1/multimodal-infer`).
- **Phase 6:** API Layer Completion (`backend/app/api/`, `backend/app/middleware/`, `backend/tests/`):
  - Standardized all 23 API endpoints across 5 modular routers (`sessions`, `consent_router`, `documents_router`, `alerts_router`, `ops_router`).
  - Implemented `CorrelationIdMiddleware` for end-to-end `X-Correlation-ID` tracing.
  - Implemented `IdempotencyMiddleware` with replay cache for safe retries over `X-Idempotency-Key`.
  - Built centralized error handling mapping domain exceptions strictly to `docs/api/ERROR_CODES.md` with zero secret/stack-trace leakage.
  - Added ABDM M1 ABHA Authentication endpoints (`/abha/initiate`, `/abha/confirm`) with sandbox simulation and profile linking.
  - Added Server-Sent Events (SSE) streaming endpoint (`/summary/stream`) for long-running LLM summary delivery.
  - Added Global Triage Emergency Queue (`/alerts`) with nurse acknowledgement lifecycle.
  - Added Document upload security (magic-byte validation, 10MB limit, quota enforcement).
  - Built 13-test automated pytest integration suite (`backend/tests/test_api_suite.py`) with 100% pass rate.
- **Architecture Updates:** Formally established dual-path OCR (Tesseract/PaddleOCR/EasyOCR for document text extraction + source attribution) and MedGemma's role as the primary clinical summary synthesizer (Module C) + medical image interpreter (X-rays, sonography, CT).


### Changed

- Documentation now defines the four-module scope, PatientDataObject/plugin boundaries, and ModelService requirement.

## Open Questions

- First release version, release cadence, and release owner are pending.
