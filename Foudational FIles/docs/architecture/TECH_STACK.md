# 1. File Header

**Project Name:** MediKiosk

**Document Version:** 1.0.0

**Date:** August 30, 2026

**Status:** Approved for MVP & Production Implementation

**Authors:** [Badal, and other asurs ]

## What This File Covers
- This file gives a readable, self-contained overview of the chosen technology, the reasons for each choice, and what each component is responsible for.
- For step‑by‑step implementation, configuration examples, and code-level detail see the referenced files at the end of each section.

→ For detailed implementation, see docs/architecture/TECH_STACK.md (this file) and the linked deep-dive pages at each section end.


# 2. Frontend & Audio Pipeline — Overview

- Frontend stack: `Next.js` + `React` + `TypeScript` for the kiosk UI, `Tailwind CSS` for styling, and `Zustand` for lightweight client state.
- Audio capture: browser `MediaRecorder` / Web Audio API → local WASM processing (VAD / denoise) → chunked WebSocket streaming to the backend for ASR.
- Responsibility: the frontend captures audio, optionally preprocesses it, shows UI, handles language selection, and streams binary audio frames to the FastAPI gateway.

Why: web standards give cross-platform kiosk compatibility and fast iteration during demos.

→ For detailed implementation, see docs/integrations/BHASHINI_ASR.md


# 3. API Layer — Overview

- Core framework: `FastAPI` (async-first) served with `uvicorn[standard]`.
- Responsibilities: accept WebSocket audio streams, receive document uploads, orchestrate ASR/TTS calls, manage session lifecycle, and hand off structured state to the AI orchestration layer.
- Data validation: use `pydantic` models (the `PatientDataObject`) as the canonical input/output schema across the API boundary.

Why: FastAPI provides async handling, good developer ergonomics, and tight Pydantic integration for clinical schemas.

→ For detailed implementation, see docs/operations/DEPLOYMENT.md


# 4. Logic / Dialogue Engine — Overview (LangGraph + LangChain)

This file retains the full reasoning for using LangGraph and LangChain. The summary below is sufficient to understand the choice:

- Orchestration: `LangGraph` — cyclic state machine for multi-turn clinical interviews that must loop and probe until structured data is complete.
- Component layer: `LangChain` — provider-agnostic model wrappers and prompt templating for model calls.
- Relationship: LangGraph controls flow (when/where to ask), LangChain handles the model interaction (how to ask).

Why: medical interviews require branching, loop-back, and structured state; LangGraph models this directly while LangChain standardizes model calls.

The LangGraph vs LangChain comparison and reasoning remains unchanged and is preserved in this document.

→ For detailed implementation, see docs/ai/MODEL_ABSTRACTION.md


# 5. Local LLM — Overview & Clarifications

- Primary clinical models: `MedGemma 4B (multimodal)` for vision+text tasks and `MedGemma 27B (text)` for higher-capacity text-only synthesis where hardware allows.
- Model serving options: `Ollama` for local development and `vLLM` for production-scale serving when a GPU is available.
- Performance figures in this document are targets/estimates only and must be validated by benchmarking in each environment.

Hardware notes (clarified):
- Our Actual Dev Hardware: 4GB VRAM / 16GB RAM laptop (current developer machines).
- Future Production Target: NVIDIA-class GPUs (e.g., 12–24GB VRAM devices) — recommended for high-throughput, low-latency deployments.

Why: using MedGemma family models lets the product combine vision and clinical reasoning in a unified stack while allowing a smaller 4B variant for constrained hosts.

→ For detailed implementation, model comparison, and serving examples, see docs/ai/MODEL_ABSTRACTION.md


# 6. Model Abstraction & Split-Brain — Summary

- Principle: all model interactions must go through a `ModelService` abstraction; no provider SDK calls inside business logic or route handlers.
- Split-Brain reason: separate low-latency live dialogue (short-turn generation) from heavy clinical summarization (longer, higher-throughput generation).
- Providers by environment: dev → Ollama/local models; demo → cloud-hosted demo models; prod → local vLLM or approved on-prem models.

Why: this keeps the application provider-agnostic and makes it possible to swap model backends without touching business code.

→ For detailed implementation, engine comparison, split‑brain diagrams, and latency targets (marked as target/estimated), see docs/ai/MODEL_ABSTRACTION.md


# 7. Voice & Language — Overview

- Primary ASR/TTS engine: `Bhashini` (ULCA streaming APIs) — chosen for managed high-coverage Indian language support.
- Fallback/local engine: `AI4Bharat` (IndicConformer, Indic-TTS) — for air-gapped / on-premise deployments.
- Responsibilities: ASR converts speech to transcripts; TTS renders questions; VAD manages barge-in and session flow.
- Supported languages: Hindi, Marathi, Indian English, and additional Indian languages via the configured provider models.

Why: Bhashini gives production-grade language coverage for the target Indian languages; AI4Bharat provides an open-source fallback for offline deployments.

→ For detailed implementation (WebSocket chunk format, sample rate, bit depth, RNNoise or Silero VAD pipeline steps, audio capture code), see docs/integrations/BHASHINI_ASR.md


# 8. Document OCR & Clinical Vision — Overview

- Chosen engine: `MedGemma 4B (multimodal)` for document understanding and structured extraction (preferred over legacy OCR for clinical reasoning and handwriting interpretation).
- Why chosen: multimodal models can reason about document context, map abbreviations, and extract structured entities more robustly than plain OCR.
- Base document types supported: `PRESCRIPTION`, `LAB_REPORT`, `DISCHARGE_SUMMARY` (extraction schemas enforced via Pydantic).

Why: clinical documents require contextual interpretation (handwriting, abbreviations, semantics) that multimodal engines handle better than Tesseract-style OCR.

→ For detailed implementation (WebRTC capture flow, OpenCV preprocessing steps, schema registry, and vision prompt templates), see docs/integrations/OCR_PIPELINE.md


# 9. Database & Storage — Overview (kept as primary reference)

This section retains the primary storage design and retention policy (left intentionally comprehensive in this file):

- Primary relational store: `PostgreSQL` (self-hosted via `Supabase` for edge/hospital deployments; managed Supabase for demos where appropriate).
- Session cache: `Redis` for ephemeral LangGraph dialogue states (10-minute TTL) and pub/sub signals.
- Artifact storage: encrypted local volume for production, Supabase Cloud Storage for demo artifacts.

What’s stored where (high level):
- Patient demographics & ABHA: `PostgreSQL` (persistent, audited)
- Active dialogue state: `Redis` (ephemeral, auto-purge)
- Microphone audio chunks & camera frames: zero retention in memory / RAM buffers
- Final summaries & FHIR bundles: encrypted persistent artifact storage

Data retention table (kept in full):

| Data Category | Target Storage Layer | Retention Period | Purge Trigger |
| :--- | :--- | :--- | :--- |
| Microphone Audio Chunks | Web Audio `AudioWorklet` RAM | Zero Retention (<200ms) | Discarded immediately upon network transmission |
| Document Camera Frames | Volatile RAM Buffer | Zero Retention (<10s) | Flushed immediately after entity extraction completes |
| Active Dialogue State | `Redis` In-Memory Cache | Ephemeral (10 min `TTL`) | Session completion, timeout, or cancellation |
| Final Clinical Summaries | `Supabase Storage` | Persistent (Audit Trail) | Hospital archival policy / manual administrative purge |
| Patient Demographics & ABHA | `PostgreSQL` (`Supabase`) | Persistent | Governed by hospital health record rules |

→ For detailed implementation (failover matrix, Upstash fallback routing, hybrid local-cloud switching logic, and failover triggers), see docs/operations/DEPLOYMENT.md


# 10. ABDM / FHIR Integration — Overview

- Standard: `FHIR R4` using `fhir.resources` for validation and mapping.
- Flow: `PatientDataObject → FHIR Mapping → Validation → FHIR JSON → ABDM/HIS`.
- Main resource mapping is preserved: Patient→Patient, Encounter→OPD visit, Condition/Observation→clinical findings, Medication-related resources→meds, Composition→clinical summary, DocumentReference→documents, Bundle→complete submission.

→ For detailed ABDM submission flows and sandbox usage see docs/operations/DEPLOYMENT.md


# 11. Security — Overview

- Authentication: ABHA ID primary; alternative entry flows documented in product requirements.
- Consent: explicit, revocable, audio-guided where needed.
- Data protection: encrypted transport, storage, and strict session isolation.

Security structure and principles are preserved in full in this file.

→ For deployment-specific security controls and environment isolation, see docs/operations/DEPLOYMENT.md


# 12. DevOps & Deployment — Overview

- Environments: `development`, `SIH demo`, `production` (hospital edge). The codebase is shared; environment configuration selects services and providers.
- Containerization: `Docker` + `docker-compose` for local and edge deployments.
- What remains consistent across environments: `PatientDataObject`, clinical workflow, voice + touch interactions, consent flows, and core mapping logic.

→ For detailed implementation (Cloudflare Tunnel setup, Colab hosting walkthrough, exact deployment diagrams, and runbooks), see docs/operations/DEPLOYMENT.md


# 13. Monitoring & Health Checks — Overview

- Monitor AI availability, API health, storage connectivity, and ABDM / HIS integration status.
- Health-check endpoints and alerting are required; logs must not contain patient PII.

→ For operational runbooks and monitoring dashboards, see docs/operations/DEPLOYMENT.md


# 14. Dev vs Production Mode — Overview (preserved)

The document's environment table and the Dev/Demo/Production guidance are preserved in full.

→ For environment-specific run steps and environment variable examples, see docs/operations/DEPLOYMENT.md


# Notes and next steps

- All deep, code-level, and pipeline-level details were moved into focused target documents (see referenced files).
- The high-level reasoning, design choices, and resource mappings remain in this file so a reader who opens only TECH_STACK.md has a complete, decision-grounded view of the stack.
