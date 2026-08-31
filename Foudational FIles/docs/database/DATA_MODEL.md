# Data Model

Purpose: Defines MediKiosk data domains and ownership boundaries; read before designing persistent entities or relationships.

## Design principles

- PatientDataObject is the canonical operational patient-state contract, not a substitute for every durable database entity.
- Separate durable, short-lived, volatile, and external-reference data.
- Store only minimum necessary data, with consent/purpose/provenance and access controls.
- Do not couple module tables directly; module interaction occurs through validated PatientDataObject updates.

## Conceptual entities

| Entity | Purpose | Lifecycle |
| --- | --- | --- |
| Patient identity reference | Approved demographic/ABHA/HIS identifier linkage | Durable under hospital policy |
| Intake session | Isolates one patient intake workflow and resumable status | Short-lived; retained only as policy requires |
| Consent record | Evidence of scope, purpose, event, withdrawal/expiry | Durable as required for proof/policy |
| PatientDataObject snapshot | Versioned canonical intake state/draft | Session/draft lifecycle |
| Source document reference | Metadata and permitted storage reference for uploaded/scanned record | Per consent/retention policy |
| Extracted clinical candidate | Structured data with source/provenance/review status | Draft/record lifecycle |
| Clinical summary draft | Generated/edited clinician-reviewable summary | Draft until clinician decision |
| Triage alert | Candidate alert, recipient, acknowledgement/escalation state | Hospital policy |
| Integration delivery | HIS/ABDM hand-off request/correlation/outcome | Audit/operational policy |
| Audit event | Security/governance record without unnecessary raw PHI | Approved audit retention |
| Plugin output | Namespaced extension data and schema/provenance | Controlled by plugin/policy |

## Relationships

```text
Patient identity reference -> intake session -> PatientDataObject snapshots
intake session -> consent records / source documents / alerts / delivery records
PatientDataObject -> extracted candidates / summary draft / plugin outputs
summary draft -> clinician decision and permitted integration delivery
```

## Multi-hospital boundary

- Multi-hospital tenancy is not an MVP feature.
- The model keeps a required deployment/facility scope boundary so future hospital isolation can be added without changing clinical modules.
- Actual tenant model, row-level policy, and cross-facility behavior remain unapproved.

→ For fields and extension contract, see `docs/database/PATIENT_DATA_OBJECT.md`.
→ For durable schema planning, see `docs/database/SCHEMA.md`.

## Open Questions

- Final entity fields, identifiers, tenant/facility model, record-retention schedule, encryption approach, and audit requirements require hospital and implementation approval.
