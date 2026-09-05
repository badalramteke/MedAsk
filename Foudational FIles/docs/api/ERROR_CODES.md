# Error Codes

Purpose: Defines stable error categories for MediKiosk APIs and plugins; read before returning, handling, or documenting an error.

## Error response contract

- Return a stable machine-readable code, safe human-readable message, correlation ID, retry guidance, and field-level details only when safe.
- Never include secrets, stack traces, raw model/provider output, or another patient’s information.
- Use standard transport status semantics at implementation time; this file does not lock exact HTTP status codes.

## Canonical codes

| Code | Meaning | Retry guidance |
| --- | --- | --- |
| `VALIDATION_FAILED` | Input/output schema or field validation failed | Correct/confirm input |
| `UNAUTHORIZED` | No valid authenticated context | Re-authenticate through approved flow |
| `FORBIDDEN` | Actor lacks role, purpose, or consent scope | Do not retry without changed authorization/consent |
| `CONSENT_REQUIRED` | Required consent is absent, expired, or withdrawn | Obtain valid consent |
| `SESSION_NOT_FOUND` | Session reference is unknown or expired | Start/recover approved session |
| `SESSION_CONFLICT` | State version is stale or conflicting | Refresh/reconcile safely |
| `DOCUMENT_REJECTED` | File/type/size/security policy rejected a document | Use permitted input or request support |
| `PROCESSING_UNAVAILABLE` | ASR/OCR/model capability unavailable | Touch fallback, retry, or clinician review |
| `PROCESSING_INVALID_OUTPUT` | Provider output failed schema/safety validation | Safe failure; do not trust output |
| `ALERT_DELIVERY_FAILED` | Alert could not reach configured recipient | Surface operational failure immediately |
| `INTEGRATION_NOT_CONFIGURED` | HIS/ABDM adapter is unavailable for environment | Use mock/demo or configure approved adapter |
| `INTEGRATION_QUEUED` | Valid hand-off awaits retry/connectivity | Observe delivery status; do not treat as accepted |
| `INTEGRATION_REJECTED` | External system rejected validated submission | Review integration error safely |
| `INTEGRATION_FAILED` | External hand-off failed without acceptance | Retry only when safe/idempotent |
| `RATE_LIMITED` | Request limit reached | Retry after policy window |
| `INTERNAL_ERROR` | Unexpected safe failure | Correlate with secure operations logs |

## Plugin error rules

- Plugins return a canonical code plus plugin ID/version and retry classification.
- A plugin failure may not silently mutate PatientDataObject.
- A model/provider safety failure is not eligible for fallback unless the task can be safely retried under the same policy.

→ For low-network handling, see `docs/architecture/OFFLINE_SYNC.md`.

## Open Questions

- Exact HTTP status mapping, localization, client-visible messages, retry intervals, and alert-delivery escalation mechanics are pending.
