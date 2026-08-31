# MediKiosk Modules

Purpose: Defines the four current MediKiosk modules and their boundaries; read before assigning product or architecture work.

| Module | Responsibility | Inputs | Outputs | Must not do |
| --- | --- | --- | --- | --- |
| A — Conversational History Engine | Adaptive voice/touch history, applicable SOCRATES/HPI/ROS, AYUSH capture, red-flag evidence/alert | Consent-valid patient input | Validated PatientDataObject history updates and staff-alert events | Diagnose, treat, or stop the interview autonomously |
| B — Document Digitization | Scan/upload, extract, structure, and chronologically organize permitted records | Consented source documents | Source-linked candidate entities/timeline updates | Invent unreadable content or make final document interpretation |
| C — Summary Generator | Synthesize validated history/document data into bilingual outputs | Validated PatientDataObject | Patient audio confirmation and clinician-editable summary draft | Commit a final record or issue clinical advice |
| D — Consent + ABDM Integration | Enforce consent lifecycle; prepare permitted FHIR/HIS/ABDM hand-off | Consent context and validated data | Consent state and truthful delivery status | Share without permission or invent external integration success |

## Module rules

- All modules use the common plugin interface and communicate only via PatientDataObject.
- All AI calls traverse ModelService.
- Each module owns one data/output namespace and focused documentation/tests.
- A future feature is a new plugin, not an extra responsibility added to a current module, unless the PRD is formally changed.

## End-to-end flow

```text
Identify + consent (D) -> history/alerting (A) -> optional document processing (B)
-> editable summary (C) -> permitted FHIR/HIS/ABDM hand-off (D) -> clinician consult
```

→ For detailed data exchange, see `docs/database/PATIENT_DATA_OBJECT.md`.
→ For extension contract, see `docs/architecture/PLUGIN_INTERFACE.md`.

## Open Questions

- Exact module plugin IDs, completion criteria, configuration ownership, and release sequencing are pending implementation planning.
