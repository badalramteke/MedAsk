# Database Migrations

Purpose: Defines safe schema and data-contract change practices for MediKiosk; read before modifying persistent data or PatientDataObject structure.

## Principles

- Migrations are versioned, reviewed, tested, reversible where practical, and applied separately per environment.
- Never change or delete clinical/patient data through an unreviewed manual production operation.
- Schema migrations, PatientDataObject migrations, plugin-output migrations, and FHIR-mapping changes are independently versioned but coordinated.
- Back up and test restoration before a material production migration.

## Change classes

| Change | Required approach |
| --- | --- |
| Add optional core/extension field | Backwards-compatible migration, default-safe handling, contract minor version |
| Remove/rename/change meaning | Parallel read/write or explicit conversion, migration plan, contract major version |
| New plugin namespace | Register plugin/schema version; no core-schema migration unless independently justified |
| Retention/deletion policy change | Legal/hospital approval, deletion evidence, and recovery assessment |
| FHIR mapping change | Target-system validation and integration version update |

## Required migration evidence

- Purpose, owner, affected records/data classification, and rollback/restore plan.
- Development and test-environment results using synthetic/de-identified data.
- Compatibility impact on APIs, plugins, prompts/rules, reports, and integrations.
- Approval for production window, backup verification, and post-migration validation.

## Open Questions

- Migration tool, naming convention, deployment automation, backup/PITR implementation, migration ownership, and production approval process are pending.
