# ABDM and FHIR Specification

Purpose: Defines the MediKiosk boundary for ABDM-compatible FHIR exchange; read before implementing, testing, or claiming ABDM integration.

## Scope

- MediKiosk prepares validated FHIR R4 content from PatientDataObject for permitted HIS/ABDM hand-off.
- It does not invent ABDM API behavior, credentials, consent artefacts, or certification status.
- Until sandbox access is available, use clearly labelled synthetic/mock payloads only; do not call them ABDM-certified or production-ready.

## Confirmed standards boundary

- ABDM documentation identifies HL7 FHIR R4 as the supported data-format version for ABHA systems.
- Health information is packaged as a FHIR document `Bundle`; the documentation describes `Composition` as the first resource for contextual grouping.
- External exchange requires consent and configured authentication/encryption under the approved ABDM integration flow.

## Proposed mapping boundary

| PatientDataObject concern | Candidate FHIR representation | Validation condition |
| --- | --- | --- |
| Patient identity/demographics | `Patient` | Approved identity/ABHA mapping only |
| OPD encounter | `Encounter` | Hospital workflow mapping required |
| Patient-reported/clinician-reviewed findings | `Observation` or `Condition` | Final resource selection by approved implementation guide/clinical policy |
| Medication history | Medication-related resource(s) | Preserve source and clinician-review state |
| Laboratory findings | `Observation` / `DiagnosticReport` | Preserve values, units, ranges, source, and uncertainty |
| Procedures/surgical history | `Procedure` | Source/clinician validation required |
| Original/permitted documents | `DocumentReference` | Only if consent/retention policy permits |
| Editable intake summary | `Composition` within document `Bundle` | Must remain a draft until clinician action |

## Delivery flow

1. Confirm relevant consent, purpose, identity, recipient, and configuration.
2. Map validated PatientDataObject data using the approved implementation guide.
3. Validate FHIR R4 structure/profiles before external packaging.
4. Submit only through the configured HIS/ABDM adapter with approved credentials and encryption.
5. Record truthful outcome: prepared, queued, accepted, rejected, or failed.

## Sandbox and mock policy

- Obtain sandbox registration/credentials before real ABDM API testing.
- Store client secrets outside source control and use only approved test identities/data.
- Mock adapters must use synthetic IDs/data and expose that delivery is simulated.
- Production entry requires applicable ABDM functional/security testing and approvals.

## Sources

- [ABDM APIs and standards](https://docs.coronasafe.network/abdm-documentation/overview-of-fhr-framework/apis-and-standards).
- [ABDM data packaging guidance](https://docs.coronasafe.network/abdm-documentation/preparation-of-data-and-data-packaging/the-main-envelope).
- [ABDM sandbox/testing FAQ](https://abdm.gov.in/faq/integration.support%40nha.gov.in).

→ For consent controls, see `docs/privacy/CONSENT_ARCHITECTURE.md`.
→ For canonical data, see `docs/database/PATIENT_DATA_OBJECT.md`.

## Open Questions

- HIP/HIU role, exact resource profiles/codes, consent artefact use, identity flow, sandbox credentials, encryption details, and HIS recipient contract are pending.
