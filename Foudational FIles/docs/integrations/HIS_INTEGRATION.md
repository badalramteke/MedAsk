# HIS Integration

Purpose: Defines the generic hospital-information-system integration boundary for MediKiosk; read before connecting to a hospital system.

## Scope

- MediKiosk is a first-mile clinical-intake layer, not an HIS/EMR replacement.
- It delivers a clinician-reviewable structured draft through approved FHIR-based or hospital-approved adapters.
- Hospital-specific behavior is not assumed; every target HIS requires its own adapter/configuration and acceptance testing.

## Integration contract

| Contract area | Requirement |
| --- | --- |
| Identity | Use approved patient/encounter identity mapping; do not create ambiguous links |
| Consent | Confirm permitted purpose and scope before sharing |
| Payload | Map validated PatientDataObject data through the approved FHIR/integration contract |
| Draft status | Preserve that the generated summary is editable and clinician-reviewed |
| Delivery result | Return accepted/rejected/queued/failed truthfully with correlation/reference where available |
| Errors | Preserve recoverable draft state and route failures to an approved operational workflow |

## Adapter design

- Each hospital connector implements the common plugin interface and owns its own configuration, route declarations if needed, and validation.
- The adapter receives a validated integration request; it does not create clinical content, make diagnoses, or directly alter other module state.
- Credentials, URLs, certificates, mapping versions, and retry policy are environment configuration—not source code.
- A mock adapter may demonstrate the contract using synthetic data until a hospital sandbox is available.

## Acceptance requirements

- Hospital validates identity/encounter mapping, consent handling, field mapping, draft visibility, response/error behavior, and audit requirements.
- Integration tests use de-identified/synthetic data unless hospital governance authorizes otherwise.
- Production use requires security review, access approval, and agreed support/escalation process.

## Sources

- [ABDM HMIS integration information](https://abdm.gov.in/our-partners/HMIS).
- [ABDM implementer’s guide](https://docs.coronasafe.network/abdm-documentation/implementers-guide).

→ For FHIR hand-off, see `docs/integrations/ABDM_FHIR_SPEC.md`.

## Open Questions

- Target HIS vendor, interface method, sandbox, credentials, field mapping, receiving workflow, support owner, and go-live acceptance criteria are pending.
