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
- **Phase 7:** Voice Intake Engine & Module E Navigation (`backend/app/services/speech/`, `backend/app/api/endpoints/voice_router.py`, `backend/tests/test_voice_suite.py`):
  - Built modular `SpeechService` package with 3-tier cascade (`BhashiniSpeechAdapter` -> `GeminiAudioAdapter` -> `MockSpeechAdapter`) across 6 Indian languages (en, hi, mr, bn, ta, te).
  - Implemented Module E `VoiceActionMatcher` recognizing allow-listed semantic UI commands (`NAV_NEXT`, `NAV_PREVIOUS`, `LANG_HINDI`, `SELECT_OPTION_1`, `CONFIRM_AGREE`, `EMERGENCY_HELP`).
  - Added hybrid in-memory `TTSAudioCache` providing 0ms audio retrieval for static questions.
  - Mounted modular `/api/v1/voice/transcribe`, `/api/v1/voice/synthesize`, `/api/v1/voice/actions`, and `/api/v1/voice/health`.
  - Built unified sub-second voice answer endpoint (`POST /api/v1/sessions/{id}/voice/answer`) advancing LangGraph and generating next-question TTS audio in a single round-trip.
  - Enforced DPDP Act ephemeral audio memory purge with zero raw audio stored on disk.
  - Authored 10-test automated pytest voice suite (`backend/tests/test_voice_suite.py`), bringing total backend test count to 23/23 tests passing with 100% pass rate.
- **Phase 8:** Medical Document Digitization Module (Module B) (`backend/app/services/ocr/`, `backend/app/services/document/`, `backend/app/models/document.py`, `backend/app/api/endpoints/documents_router.py`, `backend/tests/test_document_suite.py`):
  - Implemented modular `OCRService` package with three-path document processing:
    - Path 1A: Printed text -> Tesseract OCR (`eng+hin`) -> MedGemma clinical entity extraction.
    - Path 1B: Handwritten -> Tesseract confidence gate (<60%) -> direct MedGemma 4B Multimodal Vision fallback.
    - Path 2: Medical imaging (X-rays, CT, Ultrasound) -> direct MedGemma Multimodal (no OCR text step).
  - Built OpenCV image preprocessing pipeline (`ImagePreprocessor`) with denoising, deskewing, adaptive binarization, and multi-page PDF rasterization.
  - Created versioned prompt contract `DOCUMENT_ENTITY_EXTRACTION_SYSTEM_V1` strictly treating OCR output as untrusted data block per OWASP LLM safety rules.
  - Implemented `DocumentEntityExtractor` with date-first priority parsing (Printed -> Contextual -> MedGemma inferred).
  - Implemented `LabValueNormalizer` with comprehensive gender-adjusted reference ranges (`lab_reference_ranges.json`, 35+ tests) and three-tier severity flagging (`LOW`, `MODERATE`, `HIGH`).
  - Implemented `TimelineOrganizer` sorting patient medical history chronologically with explicit date uncertainty flags.
  - Extended `DocumentRepository` with DPDP-compliant ephemeral raw file byte buffer (purged immediately after processing) and extraction result CRUD.
  - Extended `documents_router.py` with synchronous-at-upload OCR processing (`POST /{id}/documents/upload`), timeline endpoint (`GET /{id}/documents/timeline`), extraction retrieval (`GET /{id}/documents/{doc_id}/extraction`), and clinician review endpoint (`POST /{id}/documents/{doc_id}/review`).
  - Authored 13-test automated pytest suite (`backend/tests/test_document_suite.py`), bringing total backend test suite to 36/36 tests passing with 100% pass rate.
- **Architecture Updates:** Formally established dual-path OCR (Tesseract/PaddleOCR/EasyOCR for document text extraction + source attribution) and MedGemma's role as the primary clinical summary synthesizer (Module C) + medical image interpreter (X-rays, sonography, CT).

### Changed

- Documentation now defines the four-module scope, PatientDataObject/plugin boundaries, and ModelService requirement.

## Open Questions

- First release version, release cadence, and release owner are pending.
