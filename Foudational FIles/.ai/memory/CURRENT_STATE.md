# Current State

## Project Phase
- Phase 0: foundation documentation and requirement alignment
- No production code has been implemented yet

## Built and working right now
- The workspace contains project documentation under docs/
- The .ai memory system has been initialized for session continuity
- The project context and operational rules are documented in .ai/CONTEXT.md and .ai/memory/
- No application modules, routes, database layer, or AI workflow code are running yet

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
- All 10 architecture specifications and prerequisites have been confirmed and integrated into `PRD.md`, `PATHS.md`, `RULES.md`, and `DECISIONS.md`.
- Implementation is explicitly on hold waiting for user command ("dont start impletaion until i say and all the files are okay").

## Notes
- Update this file at the end of every session with the actual state, not planned state
- Do not mark features as working unless they are verified in code or runtime
