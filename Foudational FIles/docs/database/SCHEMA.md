# Database Schema Boundary

Purpose: Defines schema-level rules for MediKiosk persistence; read before creating tables, indexes, or database access code.

## Storage allocation

| Data | Target layer | Rule |
| --- | --- | --- |
| Patient/durable workflow records | PostgreSQL through approved Supabase deployment | Persist only under consent/record policy |
| Active dialogue/session state | Redis | Short-lived; proposed 10-minute TTL pending validation |
| Original artifacts | Approved encrypted artifact storage | Retain only with explicit consent and hospital policy |
| Audio/camera processing buffers | Volatile memory | Do not make routine durable records |

## Schema rules

- Use stable internal IDs; keep ABHA/HIS identifiers as protected external references, not universal primary keys.
- Every patient-scoped durable row must carry appropriate facility/deployment, consent/purpose, provenance, and lifecycle metadata where applicable.
- Use explicit foreign keys/referential integrity for durable relationships where the implementation supports it.
- Store plugin-specific extension data in namespaced, versioned structures linked to the canonical state—not by altering the core schema for each new feature.
- Keep clinical data, security/audit data, configuration/secrets, and operational metrics logically separated.
- Access occurs only through the data/repository layer; route handlers and plugins do not query persistence directly.

## Integrity requirements

- Preserve original source reference and review status for extracted data.
- Use optimistic concurrency/versioning for mutable intake state and clinical drafts.
- Prevent a retry from producing duplicate external-delivery records.
- Enforce deletion/expiry workflows rather than treating retention as an application-only convention.

→ For migration rules, see `docs/database/MIGRATIONS.md`.
→ For privacy retention, see `docs/privacy/DATA_MINIMIZATION.md`.

## Open Questions

- Exact table definitions, column types, row-level security model, encryption/key design, partitioning/indexes, artifact-store implementation, and backup/PITR policy are pending.
