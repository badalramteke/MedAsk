# Decisions

## 2026-08-30 — AI memory system lives under .ai and is the project continuity layer
- Decision: Keep all session state, memory, workflow notes, and handoff information inside .ai/memory/ and .ai/CONTEXT.md.
- Why: The project is complex, multi-session, and requires durable context without polluting the project documentation in docs/.
- Status: Approved and active

## 2026-08-30 — Phase 0 is a planning-only foundation state
- Decision: The project is currently in Phase 0, with no active implementation work yet.
- Why: The repo contains architecture and product foundation material, but no verified application code or runtime state exists.
- Status: Approved and active

## 2026-08-30 — The project stack is locked at the architecture level
- Decision: Use Next.js for frontend, FastAPI for backend, LangGraph/LangChain for AI orchestration, MedGemma as the clinical reasoning model, and Bhashini/AI4Bharat for speech and translation support.
- Why: These choices are already reflected in the architecture documentation and establish the baseline for implementation decisions.
- Status: Approved and active

## 2026-08-30 — PatientDataObject remains the source of truth for patient state
- Decision: Do not bypass PatientDataObject or spread state across ad hoc structures.
- Why: This prevents inconsistent patient data handling and keeps clinical workflow state centralized and auditable.
- Status: Approved and active

## 2026-08-30 — No direct DB calls from route handlers
- Decision: Route-level logic must not talk to persistence directly.
- Why: This protects architecture boundaries and keeps the app consistent with the documented service/data-layer design.
- Status: Approved and active

## 2026-08-30 — No invented API or clinical assumptions
- Decision: If an external behavior is uncertain, ask instead of assuming.
- Why: Medical and integration accuracy is critical, and undocumented ABDM or clinical behavior must not be guessed.
- Status: Approved and active

## 2026-08-30 — Foundation documentation is generated and reviewed in groups
- Decision: Generate documentation group by group, beginning with architecture, and obtain user review before moving to the next group.
- Why: This prevents unreviewed assumptions from spreading through the foundation set.
- Status: Approved and active

## 2026-08-30 — Extension boundaries use an approved plugin manifest and PatientDataObject namespaces
- Decision: Use a controlled plugin manifest at startup, plugin-owned optional routes, and namespaced `plugin_outputs` for future approved extensions.
- Why: A new feature must be added without modifying the core history engine, existing modules, central route wiring, or core PatientDataObject schema.
- Status: Approved by user direction; implementation details remain pending.

## 2026-08-31 — Use a backend-first, module-by-module delivery sequence
- Decision: Start implementation with dependencies/project structure, then backend/data contracts, question logic and MedGemma validation, and backend modules. Build the frontend only after backend contracts work, then validate each module independently before full end-to-end flow.
- Why: The user prioritizes reliable backend, clinical workflow, model behavior, and phase-by-phase testing over frontend-first development.
- Status: Approved and active.

## 2026-08-31 — Delivery phases must cover the full approved solution journey
- Decision: Phase planning explicitly covers all four modules and the journey from consented identification through voice/touch history, red-flag alerting, document digitization, editable summary, clinician review, and permitted FHIR/HIS/ABDM hand-off.
- Why: The user confirmed that the solution overview is the required completeness baseline for foundational planning.
- Status: Approved and active.

## 2026-08-31 — Voice UI navigation is promoted to PRD.md (Module E)
- Decision: Promoted voice-driven kiosk navigation from FUTURE.md to PRD.md (Module E) as an accessibility engine using allow-listed semantic UI actions (`data-voice-action`), preserving continuous touch fallback.
- Why: Hands-free navigation directly advances zero-training accessibility for low-literacy and elderly patients.
- Status: Approved and incorporated into PRD.md v1.1.

## 2026-08-31 — Frontend mandatory element attributes and PATHS.md catalog
- Decision: Every interactive/identifiable frontend element must include `data-element`, `data-voice-action`, `data-testid`, `id`, and `aria-label`. All screen paths, routes, and mapped elements must be tracked in `docs/architecture/PATHS.md`.
- Why: Enables deterministic automated testing, accessibility compliance, and safe voice command mapping without DOM query vulnerabilities.
- Status: Approved and active.

## 2026-08-31 — 10 Approved Implementation Architecture Specifications
1. **Model Deployment**: Primary deployment on Google Colab (FastAPI / vLLM / tunnel serving MedGemma) with Gemini / Grok API keys as runtime fallback when Colab is offline.
2. **Document & Image Processing**: Dual pipeline:
   - Text documents (Prescriptions, Lab reports, discharge summaries): Text OCR via Tesseract / PaddleOCR / EasyOCR → extracted text fed to MedGemma for structured clinical extraction & summarization.
   - Medical Images (X-rays, CT scans, Sonography, PET scans): Direct multimodal reasoning via MedGemma (multimodal) into clinical history.
3. **Speech & Audio Cascade**: Bhashini API configured as primary ASR/TTS with `.env` key, cascading to Gemini API audio transcription as first fallback, and local Web Speech / speech engine as secondary fallback.
4. **Voice Navigation Activation**: Push-to-talk initiation; once triggered by patient, continuous voice listening stays active until session termination with 100% touch fallback parity.
5. **Supported Languages**: Full 6-language support: English, Hindi, Marathi, Bengali, Tamil, and Telugu.
6. **AYUSH History Scope**: Full Dashavidha Pariksha (10 parameters: Prakriti, Vikriti, Sara, Samhanana, Pramana, Satmya, Sattva, Ahara Shakti, Vyayama Shakti, Vaya) + Ahara-Vihara, Agni, Koshtha.
7. **Database Infrastructure**: Cloud Supabase + Docker for local development.
8. **DPDP Data Lifecycle**: Ephemeral temporary audio recordings and temp buffers purged immediately upon session completion; structured history, clinical draft, and digitized documents linked to ABHA / HIS record.
9. **Clinician Portal**: Separate dedicated portal for demo (`/doctor/portal`).
10. **ABDM Interoperability**: Standard FHIR R4 JSON bundle for health data exchange.
- Status: Confirmed and approved by user.


