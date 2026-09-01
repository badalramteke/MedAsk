# Current State

## Project Phase
- **Phase 0 (Foundation Setup):** COMPLETED. Directory structure, docker-compose (Redis + Postgres), MedGemma connectivity check, and requirements locked.
- **Phase 1 (Core Data Contract & Session Foundation):** COMPLETED. Full `PatientDataObject` Pydantic models (identity, consent, history, ayush, provenance, patch) and session repository.
- **Phase 2 (Question Engine Skeleton — Rule-based, No AI):** COMPLETED. Dynamic branching engine with `QuestionBank`, `FlowController`, `AnswerValidator`, `RedFlagScanner`, general intake dataset with female menstrual routing (31 total questions), and `/next-question`, `/answer`, `/alerts` endpoints.
- **Phase 3 (MedGemma & ModelService Integration):** COMPLETED. Implemented `ModelService`, `ColabMedGemmaAdapter` (verified LIVE on Google Colab GPU with `google/medgemma-1.5-4b-it`), `GeminiAdapter`, `MockModelAdapter`, prompt templates, safety gating, and session AI endpoints (`/ai/structure-narration`, `/ai/generate-summary`, `/ai/health`).
- **Phase 4 (LangGraph Clinical Workflow & Safety Rules):** NEXT UP.


## Built and working right now
- **Project Documentation:** Foundational documentation under `docs/` fully updated and synchronized.
- **AI Memory System:** Initialized in `.ai/memory/` with approved decisions, rules, completed work, and retrospectives for Phase 0, 1, and 2.
- **Data Contract:** Type-safe Pydantic models implementing `PatientDataObject` with RFC 6902 JSON-Patch support.
- **Question Engine Skeleton (`backend/app/engine/`):**
  - `question_bank.py`: Loads and indexes 31 questions (17 SOCRATES across 2 domains + 14 General Intake across 7 sections, with female-specific menstrual history gating).
  - `flow_controller.py`: Dynamic branching state machine (Chief Complaint → SOCRATES Deep-Dive → General History → Menstrual History if Female → Complete) using JSON `followup_triggers`.
  - `answer_validator.py`: Strict validation of submitted `value_code` against JSON options.
  - `red_flag_scanner.py`: Real-time scan of 13 deterministic emergency rules via `structured_fact_pattern` matching after every answer.
- **Clinical Datasets (`data/clinical/`):**
  - `questions_socrates.json` (17 questions, 6 languages)
  - `questions_general_intake.json` (14 questions, 7 sections, 6 languages, branching triggers + gender gating)
  - `red_flags_rules.json` (13 rules, 4 emergency categories, 6 languages)
  - `ayush_dashavidha_pariksha.json` (10 parameters, 6 languages — reserved for AYUSH hospital deployments)
  - `lab_reference_ranges.json` (Reserved for Phase 8 doc digitization)
- **API Endpoints (`backend/app/api/endpoints/sessions.py`):**
  - `POST /sessions/` (Create intake session)
  - `GET /sessions/{id}` (Retrieve session PDO)
  - `GET /sessions/{id}/next-question` (Get localized next question)
  - `POST /sessions/{id}/answer` (Submit answer, patch PDO, scan red flags, advance state)
  - `GET /sessions/{id}/alerts` (Get active red-flag alerts)

## Locked-in tech stack & decisions
- Frontend: Next.js (with mandatory element attribute schema and `PATHS.md` registry)
- Backend: FastAPI
- AI orchestration: LangGraph with LangChain integration layer
- Model layer: MedGemma served on Google Colab (vLLM/FastAPI) as primary, with Gemini/Grok API fallback via ModelService
- Vision & OCR: Dual-path (Tesseract/PaddleOCR for text docs → MedGemma summary; direct multimodal MedGemma for medical images)
- Speech stack: Bhashini ASR/TTS primary with `.env` key, cascading to Gemini audio and local speech engines; push-to-talk persistent listening until session end
- Languages: English, Hindi, Marathi, Bengali, Tamil, Telugu
- Clinical: Allopathic SOCRATES + Full Dashavidha Pariksha & AYUSH parameters (separate AYUSH deployment config)
- Data and interoperability: Cloud Supabase + local Docker, PatientDataObject, FHIR R4, ABDM sandbox model, ephemeral audio termination with persistent history
- Demonstration: Separate dedicated portal for Clinician review (`/doctor`)

## Notes
- Update this file at the end of every session with the actual state, not planned state
- Do not mark features as working unless they are verified in code or runtime
