# API and Contract Versioning

Purpose: Defines versioning rules for MediKiosk APIs, plugins, data contracts, prompts, and mappings; read before making a breaking change.

## Versioned assets

| Asset | Why version it |
| --- | --- |
| API contracts | Client compatibility and safe rollout |
| PatientDataObject core schema | Cross-plugin data integrity |
| Plugin interface/manifest | Extension compatibility |
| Plugin output namespace schema | Independent future-plugin evolution |
| Prompt/rule/model configuration | AI provenance and reproducibility |
| FHIR mapping | Integration traceability |
| Consent/clinical policy | Governance and auditability |

## Policy

- Use semantic versions for published contracts: `MAJOR.MINOR.PATCH`.
- `MAJOR`: incompatible removal/meaning change; requires an explicit migration and parallel support/rollout plan.
- `MINOR`: backwards-compatible optional additions, including a new plugin namespace.
- `PATCH`: clarification, defect fix, or non-semantic change.
- Never change the meaning of an existing PatientDataObject field or error code in place.
- Add new future-plugin data only under its own namespaced output schema.
- Record applied contract/policy/model versions in provenance for generated and integration-bound data.

## Compatibility rules

- Consumers must ignore unknown optional fields/namespaces safely.
- Producers must not require a newly added optional field until a documented major/minor rollout is complete.
- Plugin activation validates interface compatibility at startup and fails closed on mismatch.
- FHIR mapping versions are deployed only with validated test evidence and target-system approval.

→ For data extension rules, see `docs/database/PATIENT_DATA_OBJECT.md`.

## Open Questions

- Version header/path convention, deprecation period, compatibility test tooling, release process, and public-client support policy are pending.
