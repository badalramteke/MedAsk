# Clinical Safety

Purpose: Defines non-negotiable safety constraints for all MediKiosk clinical functionality; read before deploying, testing, or changing any clinical AI behavior.

## Mandatory rules

- MediKiosk is an intake and documentation tool, not a diagnostic, prescribing, or treatment system.
- The system must never state or imply that a patient has or does not have a disease.
- Every generated summary is an editable draft; only the clinician may accept, amend, reject, or save it as part of the clinical record.
- A model output is never a clinical fact until a clinician reviews it.
- Red-flag detection is a staff-notification aid, not an autonomous triage decision; the interview continues unless authorized staff intervene.

## Data-quality protections

- Preserve patient wording and distinguish it from extracted, inferred, and clinician-edited data.
- Display uncertainty, low-confidence extraction, contradictory information, and missing fields for review.
- Require confirmation/fallback for unreliable ASR or OCR results.
- Do not invent, normalize away, or silently remove a patient-reported symptom.
- Attribute document-derived claims to their source document and extraction status.

## Human oversight

- Authorized clinicians own final review of the summary.
- Authorized triage staff own acknowledgement/escalation of alerts.
- Clinical owners approve protocol versions, question banks, translations, red-flag policies, and evaluation acceptance criteria.
- The system must maintain an auditable record of draft generation, clinical changes, and alert lifecycle subject to approved retention policy.

## Release gates

- Clinical owner approval of configured workflows and languages.
- Evaluation against clinician-reviewed cases, including unsafe-output and alert-failure tests.
- Accessibility testing with intended low-literacy and elderly users.
- Validated integration behavior; no simulated success for failed HIS/ABDM delivery.

## Sources

- [WHO Basic Emergency Care](https://www.who.int/publications/i/item/9789241513081) for the need for systematic recognition of time-sensitive conditions.
- [National Academies: Improving Diagnosis in Health Care](https://www.ncbi.nlm.nih.gov/books/NBK338593/) for clinical history as part of the diagnostic process, which remains under clinician responsibility.

→ For adversarial and failure testing, see `docs/ai/RED_TEAM_PLAN.md`.

## Open Questions

- Named clinical owners, approval workflow, audit retention, and deployment acceptance thresholds are pending.
