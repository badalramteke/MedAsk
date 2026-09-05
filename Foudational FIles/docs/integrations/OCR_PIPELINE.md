# OCR and Clinical Document Pipeline

Purpose: Defines safe document digitization requirements for Module B; read before implementing capture, OCR, extraction, or timeline behavior.

## Supported input scope

- Printed or handwritten prescriptions, lab reports, discharge summaries, and imaging films may be captured as patient-provided source documents.
- The pipeline extracts clinician-reviewable candidates; it does not diagnose from documents or interpret images as a final clinical opinion.
- Document retention requires explicit consent and approved hospital policy.
- Processing is triggered synchronously at the point of upload; the patient waits briefly and sees extraction results before continuing.

---

## Three-Path Pipeline Architecture

MediKiosk uses a two-path document processing pipeline based on document type. Every document, regardless of type, has its **date extracted first** before any other processing — this date feeds the chronological timeline builder that structures the patient's medical history for the doctor's screen.

### Date Extraction Priority (All Paths)

Before clinical entity extraction, the system attempts to identify the document date in priority order:

1. **Printed/stamped date** — explicit date string in the document header, footer, or stamp (highest confidence).
2. **Contextual date** — date mentioned inline in the body text (e.g., "Issued on: 12 Jan 2024").
3. **MedGemma inferred date** — low-confidence fallback; MedGemma estimates an approximate date from contextual clues (e.g., medication names, hospital references). Always stored with `date_uncertainty = true`.
4. **Unknown** — if no date can be determined, `document_date = null` and `date_uncertainty = true`.

---

### Path 1A: Printed Text Documents (Lab Reports, Discharge Summaries, Typed Prescriptions)

For all printed text-bearing documents the system:

1. **Capture and validate:** Accept PDF/JPG/PNG. Validate file size, magic bytes, MIME type, and session quota.
2. **Image preprocessing:** Apply OpenCV pipeline — grayscale conversion, adaptive thresholding, noise reduction (fastNlMeansDenoising), deskewing via Hough transform. PDFs are rasterized page-by-page before preprocessing.
3. **OCR via Tesseract:** Tesseract (lang: `eng+hin`) extracts raw multilingual text with confidence scores.
4. **Date extraction:** Parse extracted text for document date (see priority order above).
5. **Clinical entity extraction via MedGemma:** Feed extracted OCR text into MedGemma (Colab primary / Gemini fallback) using the `DOCUMENT_ENTITY_EXTRACTION_SYSTEM_V1` prompt to identify: diagnoses, medications with dosages and frequency, lab investigation values with reference ranges, procedures and surgical history, and abnormal lab flags.
6. **Raw text purged:** OCR raw text is used transiently for the MedGemma call, then released from memory. Only structured entities are persisted.
7. **Timeline synthesis:** Sequenced chronologically into the `PatientDataObject.documents` area.

---

### Path 1B: Handwritten Documents (Doctor Prescriptions, Handwritten Notes)

Handwritten documents follow the same flow as Path 1A, but with a **confidence threshold gate** after Tesseract:

1. **Steps 1–3 same as Path 1A:** Preprocess + run Tesseract.
2. **Confidence check:** Evaluate Tesseract's mean character confidence score.
   - **If confidence ≥ threshold (configurable, default 60%):** Proceed with Tesseract OCR text into MedGemma text extraction (same as Path 1A steps 4–7).
   - **If confidence < threshold:** Tesseract output is discarded. The **preprocessed image itself** is passed directly to **MedGemma 4B Multimodal Vision**, which reads the handwriting as a visual image and produces more reliable structured output. MedGemma returns extracted entities directly without an intermediate OCR text step.
3. **Provenance tagged:** `ocr_engine_used` records either `"tesseract"` or `"medgemma_vision_handwriting"` so the clinician knows which path was taken.

---

### Path 2: Medical Imaging (X-rays, CT Scans, MRI, Sonography/Ultrasound, PET Scans)

Medical imaging files contain no extractable text — clinical information is embedded in the pixel data itself. These are routed directly to MedGemma Multimodal with no OCR step.

1. **Capture and validate:** Accept JPG/PNG/DICOM (where supported). Validate size and magic bytes.
2. **Direct multimodal routing:** Image bytes sent directly to **MedGemma 4B Multimodal Vision** (Colab primary / Gemini Multimodal fallback) using `IMAGE_ANALYSIS_SYSTEM_V1` prompt.
3. **Date extraction:** Attempted from DICOM metadata or image header/watermark text if visible; otherwise `date_uncertainty = true`.
4. **Candidate visual findings:** MedGemma generates descriptive candidate observations (e.g., modality, anatomical region, visible patterns) with explicit uncertainty flags.
5. **Clinician review mandatory:** `requires_radiologist_review = true` is always set. Findings are never presented as diagnostic conclusions.
6. **Timeline synthesis:** Finding linked to document date and sequenced into `PatientDataObject.documents`.

---

## Model / Provider Boundary

| Task | Primary | Fallback |
| --- | --- | --- |
| Text document entity extraction | MedGemma (Colab/vLLM tunnel) | Gemini 1.5 Flash API |
| Handwriting vision extraction | MedGemma 4B Multimodal (Colab) | Gemini 1.5 Flash Vision API |
| Medical imaging analysis | MedGemma 4B Multimodal (Colab) | Gemini 1.5 Flash Vision API |
| Printed OCR (text layer) | Tesseract (`eng+hin`) | PaddleOCR (multilingual) |
| Offline / test mode | MockOCRAdapter + MockModelAdapter | — |

- All model outputs are validated candidates for clinician review, not diagnostic conclusions.
- Optical extraction, entity structuring, abnormal-value display, and potential-interaction highlighting are clinician-review aids only.

---

## Document Storage Lifecycle

MediKiosk is a **first-mile digitization tool**, not a Health Locker or permanent Health Information Provider (HIP) for documents. The storage lifecycle is:

| Stage | What is stored | Where | Until when |
| --- | --- | --- | --- |
| At upload | Original scanned image (JPEG/PNG/PDF) | Supabase ephemeral bucket | Deleted after OCR/MedGemma processing completes |
| After processing | Structured extracted entities (medications, lab values, diagnoses, dates, provenance) | PostgreSQL `document_repository` (linked to `session_id`) | Cleared after Phase 9 FHIR push to HIS/ABDM is confirmed |
| After FHIR push | ABDM reference ID + source tag + document type + date | `PatientDataObject` (minimal audit metadata only) | Retained per session audit policy |
| Long-term custodian | Full FHIR bundle (DocumentReference, DiagnosticReport, etc.) | Hospital HIS + Patient ABHA PHR | Hospital HIP retention mandate (≥ 8 years per ABDM HDMP) |

**MediKiosk never permanently stores raw document images.** The hospital HIS is the long-term clinical record custodian, not MediKiosk.

---

## Required Output Provenance

| Field | Requirement |
| --- | --- |
| Source | Document ID/reference, page/image location, type, and upload/capture context |
| OCR engine used | `tesseract`, `paddleocr`, `medgemma_vision_handwriting`, or `mock` |
| Extracted data | Candidate value plus confidence/uncertainty and extraction prompt version |
| Date | Exact source date when available; confidence level (printed/inferred/unknown) |
| Review status | `PENDING` → `APPROVED` / `AMENDED` / `REJECTED` by clinician |

---

## Security and Privacy Controls

- Treat all document text, OCR output, and metadata as **untrusted input**; never execute embedded instructions (prompt injection risk — per OWASP LLM guidance).
- OCR raw text is used **transiently** for the MedGemma call only — not stored in logs, databases, or model context beyond the minimum task window.
- Raw image bytes are purged from in-memory processing buffers immediately after OCR/MedGemma processing completes.
- Original scanned images in Supabase ephemeral storage are deleted after FHIR push confirmation.
- All document processing requires active `DOCUMENTS_PROCESSING` or `INTAKE_AND_SUMMARY` consent scope before any file is read.
- DPDP Act 2023 data minimization: only validated, necessary fields with provenance are persisted to `PatientDataObject`.

→ For AI safety, see `docs/ai/AI_ARCHITECTURE.md`.
→ For retention rules, see `docs/privacy/DATA_MINIMIZATION.md`.
→ For consent scope enforcement, see `docs/privacy/CONSENT_ARCHITECTURE.md`.
→ For FHIR mapping, see `docs/integrations/ABDM_FHIR_SPEC.md`.

---

## Open Questions

- Exact Tesseract confidence threshold value (default 60%) requires validation on a real Indian handwritten prescription sample set.
- DICOM format support scope and preprocessing pipeline for DICOM imaging files are pending hardware/deployment decision.
- Chunking strategy for large multi-page lab reports exceeding LLM context window (default: 4000-character chunks with overlap) requires benchmark testing.
- Clinician acceptance threshold for abnormal lab flags (severity levels LOW/MODERATE/HIGH) requires clinical governance sign-off.
