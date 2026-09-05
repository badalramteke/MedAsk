# Retrospective — Phase 3: MedGemma & ModelService Integration

## 1. What Was Done
- **AI Task Contracts & Models:** Created `backend/app/models/ai.py` defining `ModelCapability` (Text Narration Structuring, Medical Image Analysis, Summary Synthesis, Follow-up Proposal), `ModelTaskRequest`, `ModelTaskResponse`, `StructuredNarrationResult`, `MedicalImageFindings`, and `ClinicalSummaryDraft`.
- **Versioned Prompt Library:** Created `backend/app/services/prompt_templates.py` containing versioned templates (`NARRATION_STRUCTURING_SYSTEM_V1`, `IMAGE_ANALYSIS_SYSTEM_V1`, `SUMMARY_SYNTHESIS_SYSTEM_V1`) adhering strictly to `docs/ai/PROMPT_LIBRARY.md`.
- **Multi-Provider Adapter Layer:**
  - `BaseModelAdapter`: Abstract base class for all providers.
  - `ColabMedGemmaAdapter`: Primary provider communicating with the live Google Colab GPU instance hosting MedGemma (4B Multimodal / 27B Text) via `/api/v1/clinical-infer` and `/api/v1/multimodal-infer`.
  - `GeminiAdapter`: Cloud fallback adapter for Gemini models.
  - `MockModelAdapter`: Deterministic offline mock engine ensuring 100% automated test pass rate and safe degradation.
- **Central ModelService Orchestrator:** Implemented `backend/app/services/model_service.py` with capability routing, cascading fallback, non-diagnostic safety gating, and safe degradation.
- **API Endpoints:** Added `POST /sessions/{id}/ai/structure-narration`, `POST /sessions/{id}/ai/generate-summary`, and `GET /ai/health` to `backend/app/api/endpoints/sessions.py`.

## 2. Why It Was Done
- **Central Model Abstraction:** `TECH_STACK.md` and `MODEL_ABSTRACTION.md` mandate that route handlers and clinical engines never call LLMs directly. Isolating AI behind `ModelService` allows changing model providers (Colab GPU, vLLM, Gemini, Grok, on-prem) via configuration without touching business logic.
- **MedGemma Core Role:** MedGemma acts as the clinical reasoning and summary generator (Module C). It synthesizes both the structured patient interview data and source-attributed OCR records into a unified draft summary with explicit citations (e.g. `[Doc#1: Discharge Summary 2024-05-10]`).
- **Medical Image Analysis:** MedGemma Multimodal (4B) handles medical images (X-rays, sonography, CT scans) to extract candidate visual patterns.
- **Clinical Safety & Non-Diagnosis:** Rigorous regex filters and prompt guardrails prevent the AI from generating autonomous diagnoses or medical prescriptions.

## 3. What Technologies Were Used & Why
- **Google Colab vLLM / FastAPI:** Primary GPU host serving MedGemma (`google/medgemma-1.5-4b-it`) via an ngrok tunnel.
- **Pydantic V2:** Validates structured JSON inputs/outputs across all AI contracts.
- **httpx (Async Client):** High-performance non-blocking async HTTP client for model inference calls.

## 4. How to Prepare a Presentation (PPT) for Phase 3

**Slide 1: Central ModelService Architecture (Title)**
- **Hook:** "MediKiosk's AI is built on a resilient, multi-tiered abstraction layer that isolates medical intelligence from business logic, ensuring 100% uptime and clinical safety."

**Slide 2: Live MedGemma Serving & Cascade Fallback**
- **Talking Points:** Primary inference is powered by MedGemma running on dedicated GPU instances (Google Colab / vLLM), with automated fallback to Gemini/Groq and deterministic mock failover. If the internet drops, the kiosk seamlessly continues via the touch engine.
- **Visual:** Diagram showing `Client -> FastAPI -> ModelService -> [Colab MedGemma -> Gemini -> Mock]`.

**Slide 3: Source-Attributed Summary Synthesis (Module C)**
- **Talking Points:** How MedGemma ingests both patient-reported symptoms and OCR-extracted laboratory/prescription findings, synthesizing a physician draft where every single claim has an explicit citation tag (e.g. `[Doc#1: Lab Report]`, `[Patient-Reported]`).
- **Visual:** A side-by-side comparison of raw OCR text + interview answers resulting in a neatly formatted summary draft with green source tags.

**Slide 4: Medical Image Multimodal Understanding**
- **Talking Points:** MedGemma 4B Multimodal directly analyzes medical imaging (Chest X-rays, Ultrasound/Sonography, CT scans), providing descriptive visual observations as candidate findings for radiologist review.

**Slide 5: Clinical Safety & Guardrails**
- **Talking Points:** Strict compliance with PRD Section 11.4 — the AI strictly elicits and summarizes, with hardcoded safety gates blocking autonomous diagnoses or drug prescriptions.
