# Clinical Protocols

Purpose: Sets the evidence-based boundaries for MediKiosk clinical-intake workflows; read before changing interview content, triage behavior, or summaries.

## Clinical role

- MediKiosk elicits and structures patient-reported information before consultation.
- It creates an editable draft for a clinician; it does not diagnose, prescribe, recommend treatment, or replace examination.
- Red-flag detection creates a staff alert without interrupting the interview. Triage staff decide the clinical response and may acknowledge or clear the alert.
- All patient-facing content must support voice and touch, use approved local-language wording, and be tested with the target population.

## Required intake domains

| Domain | Required outcome |
| --- | --- |
| Presenting concern | Patient’s words plus structured chief complaint |
| HPI | Chronological symptom narrative and relevant follow-up answers |
| History | Past medical/surgical, medication/allergy, family, personal, and review-of-systems information |
| Reproductive history | Ask only when the patient identifies as female and the clinician-approved flow applies |
| AYUSH mode | Trividha, Ashtavidha, Dashavidha, and Ahara-Vihara fields for the configured AYUSH workflow |
| Documents | Structured extraction from prescriptions, lab reports, discharge summaries, and imaging films where supported |
| Summary | Draft in the standard format for clinician edit, accept, amend, or reject |

## Clinical workflow rules

1. Obtain required consent before collecting or processing health data.
2. Start with an open patient narrative, then use focused, adaptive questions.
3. Record source and confidence/provenance; distinguish patient-reported, document-extracted, and clinician-edited information.
4. Use SOCRATES only as a structured symptom/pain history aid, not as a diagnostic engine.
5. Run approved red-flag screening throughout the interview and publish alerts to authorized staff.
6. Preserve uncertainty and contradictions for clinician review; never silently infer a diagnosis.
7. Present the summary as a draft and capture clinician edits/decision where the hospital workflow permits.

## Governance gates

- Clinician approval is required before deploying question wording, translations, scoring, clinical ontology mappings, alert thresholds, or protocol changes.
- Evidence sources support this foundation but do not substitute for hospital-specific clinical governance.
- Emergency-alert configuration must be tested with the hospital’s triage workflow before patient use.

## Sources

- [NCBI Clinical Methods: The Medical Interview](https://www.ncbi.nlm.nih.gov/books/NBK349/) for structured history components and patient-centred interview principles.
- [WHO Interagency Integrated Triage Tool](https://www.who.int/tools/triage) for facility-based acuity prioritization principles.

→ For question-flow requirements, see `docs/clinical/QUESTION_ENGINE_SPEC.md`.
→ For alert boundaries, see `docs/clinical/RED_FLAG_RULES.md`.
→ For safety requirements, see `docs/clinical/CLINICAL_SAFETY.md`.

## Open Questions

- Hospital-approved question wording, local-language translations, clinician sign-off process, and triage escalation contacts are pending.
