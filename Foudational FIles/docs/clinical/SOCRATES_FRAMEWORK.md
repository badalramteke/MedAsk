# SOCRATES Framework

Purpose: Defines the SOCRATES history structure used for applicable symptoms; read before authoring symptom follow-up questions.

## Scope

- SOCRATES is a mnemonic for structuring symptom/pain history, not a diagnosis, triage decision, or treatment pathway.
- The engine uses it only when it is relevant to the patient’s concern and an approved question is available.
- Patient-facing wording must be clinician-approved and localized before deployment.

## Structured fields

| Element | Capture objective |
| --- | --- |
| Site | Where the symptom is experienced |
| Onset | When and how it began |
| Character | How the patient describes it |
| Radiation | Whether it spreads elsewhere |
| Associated factors | Other symptoms or relevant circumstances reported with it |
| Timing | Pattern, duration, frequency, or progression |
| Exacerbating/relieving factors | What appears to worsen or improve it |
| Severity | Patient-reported impact or severity using an approved scale/description |

## Safe use rules

- Preserve the original patient narrative; structured answers are an aid to clinician review.
- Do not require every element when it is irrelevant, refused, unknown, or unsafe to pursue in the kiosk.
- A response that matches an approved alert rule emits a staff alert; SOCRATES itself never determines urgency.
- Do not translate symptom answers into a disease label.

## Source

- [BMJ Supportive & Palliative Care abstract on SOCRATES](https://pubmed.ncbi.nlm.nih.gov/25960483/) identifies the eight commonly used framework elements.

→ For alert handling, see `docs/clinical/RED_FLAG_RULES.md`.

## Open Questions

- Approved patient wording, severity scale, language translations, and symptom-specific branches remain pending clinical review.
