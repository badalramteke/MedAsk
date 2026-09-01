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

## 2026-09-01 — AYUSH hospitals are entirely separate deployments (sourced from PS.md + PRD.md)
- Decision: AYUSH hospitals (e.g., AIIA New Delhi, NIS Chennai, NIUM Bengaluru, NIH Kolkata) are **completely separate institutions** under the Ministry of AYUSH. MediKiosk deployed at an AYUSH hospital is a separate deployment configuration — there is NO in-app toggle or switch. A general hospital deployment runs allopathic-only intake. An AYUSH hospital deployment runs AYUSH intake (Dashavidha Pariksha etc.). The deployment configuration determines this at setup time, not at runtime.
- Critical context: The problem statement (SIH26047) is itself from the **Ministry of Ayush / All India Institute of Ayurveda (AIIA)** (PRD.md lines 9-10). AYUSH is not a secondary feature — it is the **primary deployment context** for the organization that issued the problem statement. PS.md line 91 explicitly says "for Ayurvedic OPDs, an extended interview". PRD.md Section 8.1 says "an extended interview setting for Ayurvedic OPDs". PRD.md Section 5.3 says "Doctors practicing traditional Indian medicine in AYUSH institutions" need "specialized software modes".
- Why: AYUSH and allopathic are entirely different treatment systems run by different institutions with fundamentally different clinical workflows, question banks, and assessment frameworks.
- Status: Approved and active.

## 2026-09-01 — Question flow is dynamically sequenced based on previous answers
- Decision: The question engine must be **conditional and branching**, not a flat sequential list. The next question shown to the patient depends on what they answered in the previous question. For example, if the patient selects "chest pain" as chief complaint, the engine routes into the chest_pain SOCRATES sequence; if they answer "pain radiates to left arm", the engine may trigger a red-flag scan AND adjust follow-up questions accordingly.
- Why: A static flat questionnaire misses critical clinical details and wastes patient time with irrelevant questions. Dynamic branching mirrors how a real clinician conducts an interview.
- Status: Approved and active.

## 2026-09-01 — MedGemma vs OCR Pipeline Roles & Source-Attributed Summary Synthesis
- Decision: 
  1. **Text Documents (Prescriptions, Lab Reports, Discharge Summaries):** Raw text extraction, lab reference bounds, and handwritten prescription text are extracted using dedicated OCR/text-extraction engines (Tesseract / PaddleOCR / EasyOCR). 
  2. **Structured & Sourced Feeding:** The extracted text and structured items (ranges, values, drugs, dosages) are annotated with exact source document references (e.g. `[Doc#1: Discharge Summary, 2024-05-10]`, `[Doc#2: CBC Lab Report]`).
  3. **MedGemma Core Role:** MedGemma is used as the **primary synthesis and clinical summary generator (Module C)**, taking the structured patient interview data and the source-attributed OCR extracts, and synthesizing them into a cohesive clinical draft where every finding/investigation explicitly cites its source.
  4. **Medical Image Analysis:** MedGemma Multimodal (4B) is used directly for **medical image descriptions & visual findings** (e.g., Chest X-rays, Sonography / Ultrasound, CT scans).
- Why: Preserves high-precision deterministic OCR extraction for numbers/ranges while leveraging MedGemma's medical reasoning for clinical synthesis, source-provenance summaries, and image understanding.
- Status: Approved and active.

## 2026-09-01 — Gender-Gated Reproductive & Menstrual History Routing
- Decision: When the patient gender is female (`gender == "FEMALE"`), the intake flow conditionally prompts applicable **Menstrual & Reproductive History** questions (LMP - Last Menstrual Period, cycle regularity, pregnancy status, obstetric history if applicable). If male or unspecified, this entire section is cleanly skipped.
- Why: Standard clinical intake protocol mandates reproductive history for female patients while omitting irrelevant questions for male patients to maximize throughput and privacy.
- Status: Approved and active.

## 2026-09-02 — Explicit FHIR-Aligned Section Decomposition for ClinicalSummaryDraft
- Decision: Decompose `ClinicalSummaryDraft` into distinct typed fields matching the 9 required sections of ABDM OPConsultRecord / FHIR R4 `Composition` (`patient_chief_complaint`, `hpi_summary`, `past_medical_surgical_summary`, `medications_and_allergies`, `family_history_summary`, `personal_social_history_summary`, `review_of_systems_summary`, `investigations_and_lab_summary`, `imaging_findings_summary`, `menstrual_reproductive_summary`), rather than collapsing family/personal/ROS into a single generic string.
- Why: Prevents data loss during downstream FHIR serialization (Phase 9) and allows the physician UI (Phase 12) to render and edit each clinical section independently.
- Status: Approved and active.

## 2026-09-02 — Non-Autonomous Clinical Draft Governance (Accept/Amend/Reject Boundary)
- Decision: The backend summary generator strictly produces a preliminary draft (`is_draft_for_clinician_review: true`, `draft_status: "PENDING"`) and NEVER commits an autonomous final record. The draft only transitions to `APPROVED` when an authorized clinician explicitly calls `POST /{session_id}/summary/review` with `action: ACCEPTED` or `action: AMENDED`.
- Why: Satisfies national clinical AI safety regulations (PRD Section 11.4) and ensures complete medico-legal clinician authority over generated health records.
- Status: Approved and active.

## 2026-09-02 — Standardized Error Envelopes & Zero Information Leakage
- Decision: All FastAPI exceptions are intercepted by global handlers and transformed into standard `ERROR_CODES.md` envelopes with stable machine-readable codes, correlation IDs, and safe messages. No SQL queries, stack traces, or internal model prompts are ever returned to HTTP clients.
- Why: Mandated by `docs/api/ERROR_CODES.md` and cybersecurity zero-trust principles for hospital-grade deployments.
- Status: Approved and active.

## 2026-09-02 — Server-Sent Events (SSE) for Long-Running Clinical Synthesis
- Decision: Provide `GET /api/v1/sessions/{id}/summary/stream` alongside synchronous REST calls to stream LLM synthesis status and tokens in real-time.
- Why: MedGemma inference takes 15-35s on GPU; SSE streaming prevents reverse proxy 504 timeouts and provides live feedback to the patient/doctor.
- Status: Approved and active.

## 2026-09-02 — Binary Magic-Byte File Validation for Document Staging
- Decision: Document uploads are validated against actual file header signatures (magic bytes for JPEG `\xff\xd8\xff`, PNG `\x89PNG`, PDF `%PDF-`) rather than trusting client-provided Content-Type headers or file extensions.
- Why: Prevents malicious executable uploads (e.g. polyglot binaries disguised as `.jpg`) from entering the OCR pipeline.
- Status: Approved and active.



