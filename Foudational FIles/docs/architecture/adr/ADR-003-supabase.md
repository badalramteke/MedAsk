# ADR-003: Use PostgreSQL via Supabase as the Primary Data Platform

Purpose: Records the data-platform decision for MediKiosk; read before changing persistence or deployment topology.

## Status

- Accepted
- Date: 2026-08-30

## Context

- MediKiosk needs relational, auditable patient-data persistence plus a practical development/demo path.
- The target production environment may require hospital-controlled deployment and limited external connectivity.
- The technology stack selects PostgreSQL through Supabase, Redis for ephemeral dialogue state, and encrypted artifact storage.

## Decision

- Use PostgreSQL through Supabase as the primary relational data platform.
- Use managed Supabase only where approved for demonstrations.
- Use self-hosted Supabase on hospital-controlled infrastructure for production, subject to hospital security, backup, operations, and compliance approval.
- Keep Redis limited to short-lived dialogue/session state; it is not the durable clinical record.

## Consequences

| Positive | Trade-off / risk | Mitigation or follow-up |
| --- | --- | --- |
| Provides PostgreSQL-backed relational storage | Self-hosting transfers operational responsibility | Define production backup, monitoring, and recovery runbooks |
| Supports demo and hospital-edge modes | Deployment capability differs by environment | Configure environment explicitly; do not assume cloud availability |
| Keeps temporary state separate from durable records | Retention rules require governance | Enforce data minimization and hospital policy |

## Sources

- [Supabase database overview](https://supabase.com/docs/guides/database/overview)
- [Supabase self-hosting guide](https://supabase.com/docs/guides/self-hosting)

## Open Questions

- Production hosting, backup ownership, retention controls, and tenant configuration require hospital approval.
