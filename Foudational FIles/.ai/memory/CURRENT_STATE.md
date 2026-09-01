# Current State

## Project Phase
- Phase 1: Core data contract and session foundation.
- Phase 0 foundation setup is completed. Project directories exist and initial configurations are in place.

## Built and working right now
- Project documentation under docs/ fully updated and synchronized
- .ai memory system initialized with approved decisions, rules, and architecture specs
- MedGemma 4B server verified LIVE on GPU (Colab ngrok gateway)
- Cloud Supabase (PostgreSQL, GoTrue, Storage, PostgREST) verified LIVE and working
- Local Docker Redis (`medikiosk-redis`) verified LIVE responding `+PONG` on `localhost:6379`
- Project scaffolding complete (`backend`, `frontend`, `plugins`, `integrations`, `configuration`).
- `docker-compose.yml` created for local data persistence.
- `backend/requirements.txt` configured with core dependencies.
- `backend/check_medgemma.py` script created for basic model health checks.

## Locked-in tech stack & decisions
- Frontend: Next.js (with mandatory element attribute schema and `PATHS.md` registry)
- Backend: FastAPI
- AI orchestration: LangGraph with LangChain integration layer
- Model layer: MedGemma served on Google Colab (vLLM/FastAPI) as primary, with Gemini/Grok API fallback via ModelService
- Vision & OCR: Dual-path (Tesseract/PaddleOCR for text docs → MedGemma summary; direct multimodal MedGemma for medical images)
- Speech stack: Bhashini ASR/TTS primary with `.env` key, cascading to Gemini audio and local speech engines; push-to-talk persistent listening until session end
- Languages: English, Hindi, Marathi, Bengali, Tamil, Telugu
- Clinical: Allopathic SOCRATES + Full Dashavidha Pariksha & AYUSH parameters
- Data and interoperability: Cloud Supabase + local Docker, PatientDataObject, FHIR R4, ABDM sandbox model, ephemeral audio termination with persistent history
- Demonstration: Separate dedicated portal for Clinician review (`/doctor`)

## Current status summary
- All Phase 0 requirements have been met.
- Ready to begin Phase 1 backend implementation.

## Notes
- Update this file at the end of every session with the actual state, not planned state
- Do not mark features as working unless they are verified in code or runtime
