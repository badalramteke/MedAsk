# Dashavidha Pariksha

Purpose: Defines the AYUSH-mode data boundary for Dashavidha Pariksha; read before building AYUSH question flows or data mappings.

## Scope and safety boundary

- Dashavidha Pariksha is an AYUSH assessment framework included in the MediKiosk AYUSH workflow.
- This document defines data-capture fields only. It does not define treatment, diagnosis, scoring, interpretation, or automated recommendations.
- An AYUSH clinician must approve all questions, translations, permitted values, and any future interpretation logic.

## Ten fields to capture

| Field | Capture rule |
| --- | --- |
| Prakriti | Store patient/clinician-approved assessment without inferring it from unrelated data |
| Vikriti | Store current assessment as a clinician-reviewable field |
| Sara | Store approved assessment response |
| Samhanana | Store approved assessment response |
| Pramana | Store approved assessment response |
| Satmya | Store approved assessment response |
| Sattva | Store approved assessment response |
| Ahara Shakti | Store approved assessment response |
| Vyayama Shakti | Store approved assessment response |
| Vaya | Store approved age-related assessment response |

## Related AYUSH fields in scope

- Trividha Pariksha and Ashtavidha Pariksha are included as named AYUSH-history frameworks in the PS/PRD.
- Ahara-Vihara, Agni, Koshtha, Nidana, and Samprapti are named supporting AYUSH history fields.
- Their exact definitions, question sequences, value sets, and mappings must be clinician-approved before implementation.

## Data rules

- Keep AYUSH data in a clearly labelled namespace with source, language, and review status.
- Separate patient-reported answers from clinician-entered/validated assessment.
- Do not convert AYUSH fields into a biomedical diagnosis or use them to generate treatment advice.

## Sources

- [Dashavidha Pariksha review by CCRAS-affiliated authors](https://ijapr.in/index.php/ijapr/article/view/4164) for the ten named parameters.
- [Peer-reviewed overview of Dashavidha Pariksha](https://pmc.ncbi.nlm.nih.gov/articles/PMC4492017/) for its placement within Ayurvedic examination literature.

→ For engine behavior, see `docs/clinical/QUESTION_ENGINE_SPEC.md`.

## Open Questions

- AYUSH clinician-approved question bank, terminology translations, input options, scoring, and review workflow are not yet available.
