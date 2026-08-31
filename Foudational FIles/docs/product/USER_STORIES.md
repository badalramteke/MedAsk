# User Stories

Purpose: Defines current-scope user outcomes for MediKiosk; read before planning or accepting product work.

## Patient

- As a first-time, low-literacy patient, I want to use simple voice or touch prompts in my chosen language so that I can provide my history without prior digital training.
- As a patient with a current health concern, I want to describe it naturally and answer relevant follow-up questions so that the clinician receives a structured history draft.
- As a patient with paper records, I want to scan prescriptions, lab reports, discharge summaries, and permitted imaging records so that my clinician can review an ordered timeline.
- As a patient, I want a clear audio/touch consent experience and the ability to decline or withdraw permitted data sharing so that I remain in control of my information.

## Allopathic physician

- As an OPD physician, I want a concise, structured, editable draft before consultation so that I spend the visit on examination, reasoning, and counselling rather than repeated data entry.
- As a physician, I want to see source/provenance and uncertainty for extracted data so that I can verify, amend, accept, or reject it safely.

## AYUSH practitioner

- As an AYUSH practitioner, I want the configured intake to capture Dashavidha Pariksha and related AYUSH history fields so that I can review a fuller pre-consultation history.
- As an AYUSH practitioner, I want patient-reported AYUSH data kept separate from automated interpretation so that clinical judgement remains mine.

## Triage/nursing staff

- As triage staff, I want a timely, visible alert when configured potential emergency evidence appears so that I can prioritize patient assessment under hospital protocol.
- As triage staff, I want to acknowledge, clear, or escalate the alert so that the system accurately records the alert lifecycle without making an autonomous decision.

## Hospital/IT support

- As hospital operations/IT support, I want configured HIS/ABDM delivery states to be truthful and auditable so that failed or queued submissions are not mistaken for completed records.

## Acceptance boundaries

- All clinical outputs remain drafts for clinician review.
- No story authorizes autonomous diagnosis, treatment advice, prescription generation, EMR replacement, hardware manufacturing, or a future idea from `FUTURE.md`.

→ For module responsibilities, see `docs/product/MODULES.md`.

## Open Questions

- Story acceptance criteria, localization, accessibility validation, clinical wording, and hospital workflow timing require stakeholder review.
