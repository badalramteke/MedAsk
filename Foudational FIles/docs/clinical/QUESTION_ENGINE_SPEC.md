# Question Engine Specification

Purpose: Defines safe requirements for the adaptive history-question engine; read before implementing or reviewing Module A dialogue logic.

## Objective

- Convert patient narration and touch answers into a complete, clinician-reviewable history draft.
- Keep every spoken question answerable by touch.
- Ask follow-ups based on the presenting concern and prior validated answers without generating diagnostic claims.

## Required flow

| Stage | Engine responsibility |
| --- | --- |
| Consent and language | Confirm valid consent state and configured language before collection |
| Open narrative | Invite the patient to describe the reason for visit in their own words |
| Structured HPI | Ask relevant chronology/symptom questions; use SOCRATES where applicable |
| History domains | Cover configured past, medication/allergy, family, personal, ROS, and reproductive fields |
| AYUSH branch | Enable only for the selected AYUSH workflow; capture approved Trividha, Ashtavidha, Dashavidha, and Ahara-Vihara fields |
| Safety monitor | Evaluate approved red-flag rules and emit a staff alert without stopping the interview |
| Confirmation | Read back/visually present captured information and route it to the editable clinician draft |

## Interaction requirements

- Use concise, respectful, non-leading questions; maintain the patient’s original wording alongside structured fields where possible.
- Explain transitions between sections and allow “don’t know,” “prefer not to answer,” “repeat,” and back navigation.
- Do not pressure a patient to disclose sensitive information.
- Ask menstrual/reproductive history only when the patient identifies as female and the approved workflow applies.
- A low-confidence ASR result must be confirmed through replay, clarification, or touch—not silently accepted.
- The engine may identify missing data but must not fabricate a value to complete a form.

## AI constraints

- The model may propose the next approved question only within the configured clinical ontology and policy.
- Deterministic policy controls consent checks, question eligibility, red-flag event emission, and output validation.
- The model must not provide medical advice, diagnoses, treatment instructions, reassurance that an alert is harmless, or final record decisions.
- Prompt and model versions must be recorded as provenance for generated content.

## Completion conditions

- Required consent remains valid.
- The engine records either an answer, an explicit refusal/unknown response, or a clinician-review-required gap for each applicable field.
- A summary draft is generated only after validation; it remains editable by the clinician.

## Sources

- [NCBI Clinical Methods: The Medical Interview](https://www.ncbi.nlm.nih.gov/books/NBK349/) for structured history and review-of-systems principles.
- [Medical History, StatPearls](https://www.ncbi.nlm.nih.gov/books/NBK534249/) for structured history domains and reproductive-history context.

→ For the symptom framework, see `docs/clinical/SOCRATES_FRAMEWORK.md`.
→ For prompt controls, see `docs/ai/PROMPT_LIBRARY.md`.

## Open Questions

- The exact approved ontology, question bank, translations, and completion rules await clinical review.
