# OCR and Clinical Document Pipeline

Purpose: Defines safe document digitization requirements for Module B; read before implementing capture, OCR, extraction, or timeline behavior.

## Supported input scope

- Printed or handwritten prescriptions, lab reports, discharge summaries, and imaging films may be captured as patient-provided source documents.
- The pipeline extracts clinician-reviewable candidates; it does not diagnose from documents or interpret images as a final clinical opinion.
- Document retention requires explicit consent and approved hospital policy.

## Pipeline

1. **Capture and validate:** accept permitted file/image formats, apply size/type limits, and create source metadata.
2. **Preprocess:** improve legibility where configured while preserving the original/source reference.
3. **Extract:** use the configured OCR/vision provider through ModelService.
4. **Structure:** identify candidate diagnoses, medications/dosages, investigations/values/reference ranges, procedures/surgery history, document type, and possible date.
5. **Validate:** attach confidence/uncertainty and source location; never silently invent unreadable content.
6. **Timeline:** order records by supported dates; retain unknown/ambiguous dates for review rather than guessing.
7. **Review and summary:** write validated candidates to PatientDataObject for clinician-editable summary generation.

## Model/provider boundary

- MedGemma 4B is the primary multimodal document/image-understanding model selected in the technology stack.
- Provider/model calls pass through ModelService.
- Gemini/Grok fallback is permitted only if configured and must meet identical schema, safety, privacy, and provenance controls.
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
