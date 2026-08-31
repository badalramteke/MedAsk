# API Contracts

Purpose: Defines MediKiosk API boundary rules and transport contracts; read before designing a route, plugin-owned endpoint, or client integration.

## API principles

- APIs expose one concern per contract and validate all inputs/outputs with typed schemas.
- Route handlers authenticate, authorize, validate transport data, and delegate to a use-case/plugin service; they contain no clinical, persistence, model-provider, or FHIR logic.
- `PatientDataObject` is the canonical workflow payload. APIs return task-specific views, never unrestricted patient state by default.
- Plugins may declare their own approved routes through the plugin manifest; no central route file is manually edited for a future plugin.
- Exact HTTP paths, methods, external payloads, and authentication mechanics remain unapproved until implementation/integration design.

## Contract categories

| Category | Purpose | Contract outcome |
| --- | --- | --- |
| Session/consent | Start, resume, cancel, or inspect a permitted intake session | Session status and permitted next action |
| Patient intake | Submit voice/touch-confirmed structured updates | Validated draft state/field result and uncertainty |
| Document intake | Submit a permitted document and obtain processing state | Source reference, processing status, extracted-candidate availability |
| Clinical draft | Retrieve/update clinician-editable draft through authorized workflow | Draft data, provenance, review status |
| Triage alert | Deliver/acknowledge authorized staff alert | Alert lifecycle state; no diagnostic assertion |
| Integration | Request permitted HIS/ABDM hand-off and observe outcome | Prepared/queued/accepted/rejected/failed status |
| Operations | Health/readiness and non-sensitive configuration status | No patient or secret data |

## Common request requirements

- Correlation/session identifier and version/optimistic-concurrency information where state changes.
- Identity, authorization, and consent context established server-side; client-provided claims are not trusted.
- Typed payload, declared content type/size, and idempotency key for safe retryable external submissions where applicable.
- Minimum necessary data only; no secrets, raw audio, raw camera frames, or unrelated patient data.

## Common response requirements

- Stable contract version, request correlation ID, status, and typed result/error.
- Provenance/uncertainty for AI/document-derived data where returned.
- Truthful delivery state: queued is not accepted; accepted is not clinician-approved.
- Safe errors that do not expose internal details, credentials, or another patient’s data.

## Security rules

- Enforce role/purpose checks before sensitive reads or writes.
- Validate server-side before dispatching to plugins/providers.
- Apply rate/abuse controls and upload limits at the gateway.
- Do not return internal model prompts, provider diagnostics, raw storage paths, or secret configuration.

→ For shared errors, see `docs/api/ERROR_CODES.md`.
→ For version policy, see `docs/api/VERSIONING.md`.
→ For plugin route ownership, see `docs/architecture/PLUGIN_INTERFACE.md`.

## Open Questions

- Exact endpoint paths/methods, client authentication, staff authorization mechanism, pagination, streaming protocol, and request-size limits are pending implementation approval.
