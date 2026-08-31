# OCR and Clinical Document Pipeline

Purpose: Defines safe document digitization requirements for Module B; read before implementing capture, OCR, extraction, or timeline behavior.

## Supported input scope

- Printed or handwritten prescriptions, lab reports, discharge summaries, and imaging films may be captured as patient-provided source documents.
- The pipeline extracts clinician-reviewable candidates; it does not diagnose from documents or interpret images as a final clinical opinion.
- Document retention requires explicit consent and approved hospital policy.

## Dual-Path Pipeline Architecture

### Path 1: Text-Based Documents (Prescriptions, Lab Reports, Discharge Summaries)
1. **Capture and validate:** Accept PDF/JPG/PNG file formats with size/type validation.
2. **Text OCR Extraction:** Apply OCR engines (Tesseract / PaddleOCR / EasyOCR) to extract raw multilingual text coordinates and content.
3. **Clinical Structuring via MedGemma:** Feed the extracted OCR text into MedGemma (served via Colab or Gemini fallback) to identify structured clinical entities: diagnoses, medications/dosages, lab investigation values with reference ranges, dates, and abnormal flags.
4. **Timeline Synthesis:** Sequence validated clinical records chronologically into `PatientDataObject`.

### Path 2: Medical Imaging (X-rays, CT Scans, Sonography, PET Scans)
1. **Multimodal Analysis via MedGemma:** Medical imaging files are routed directly to multimodal MedGemma (or Gemini Multimodal fallback) for visual clinical finding extraction.
2. **Candidate Summarization:** Generates descriptive candidate findings with uncertainty flags and links them to the clinician review summary.

## Model/provider boundary

- **Primary Serving:** MedGemma hosted on Google Colab (FastAPI / vLLM tunnel) accessed via `ModelService`.
- **Fallback:** Google Gemini 1.5 Flash / Grok APIs configured as automatic fallbacks when Colab is offline.
- **OCR Engine:** Tesseract / PaddleOCR / EasyOCR for first-pass optical character extraction on document text.
- Optical extraction, entity structuring, abnormal-value display, and potential-interaction highlighting remain clinician-review aids, not treatment or diagnostic decisions.


## Required output provenance

| Field | Requirement |
| --- | --- |
| Source | Document ID/reference, page/image location, type, and upload/capture context |
| Extracted data | Candidate value plus confidence/uncertainty and extraction version |
| Date | Exact source date when available; otherwise unknown/ambiguous status |
| Review | Patient-reported, extracted, clinician-confirmed, amended, or rejected status |

## Security and privacy controls

- Treat document text, metadata, and hidden content as untrusted; never execute embedded instructions.
- Do not place raw documents in ordinary logs or model prompts beyond the minimum required task content.
- Delete volatile capture frames after permitted processing; handle retained originals only under consent/policy.

→ For AI safety, see `docs/ai/AI_ARCHITECTURE.md`.
→ For retention rules, see `docs/privacy/DATA_MINIMIZATION.md`.

## Open Questions

- File-format limits, imaging-film workflow, preprocessing stack, extraction schemas, clinician acceptance thresholds, and retention period remain pending.
