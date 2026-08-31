# Incident Recovery

Purpose: Defines safe response boundaries for MediKiosk incidents; read when patient safety, privacy, security, delivery, or availability is affected.

## Ownership model

- Triage staff own clinical response to an emergency alert under hospital protocol.
- Deployment/operator team owns technical containment and restoration.
- Hospital governance/legal owners determine patient notification, regulatory reporting, and record-retention actions.
- Exact people and contacts are pending; no release may rely on unspecified incident ownership.

## Incident classes

| Class | Example | Immediate priority |
| --- | --- | --- |
| Clinical workflow | Alert not delivered, unsafe AI output, draft presented incorrectly | Protect patient/staff workflow; escalate clinical owner |
| Privacy/security | Suspected unauthorized access, PHI leak, lost credential | Contain exposure, preserve approved evidence, escalate security owner |
| Integration/data | HIS/ABDM hand-off failure, duplicate/incorrect delivery | Stop unsafe retry, preserve draft/status, escalate integration owner |
| Availability | API, model, storage, or network outage | Use defined fallback; avoid data loss/false success |

## Response sequence

1. Detect and record a correlation ID, time, affected environment, and safe impact summary.
2. Contain: disable affected integration/plugin/provider or access path when necessary.
3. Protect patients: use approved clinician/triage/manual fallback; do not rely on unavailable automation.
4. Preserve minimum necessary evidence and avoid further disclosure.
5. Restore using a tested rollback/recovery procedure.
6. Validate data integrity, consent scope, alert/delivery state, and service health before reopening.
7. Document cause, impact, actions, outstanding risks, and prevention tasks.

## Recovery limits

- Do not claim an incident is resolved until verification is complete.
- Do not resend, alter, or delete clinical data without authorization and idempotency/record-integrity checks.
- Major privacy/security/legal duties must follow current hospital policy and applicable law, not this generic runbook alone.

→ For threat-specific controls, see `docs/security/THREAT_MODEL.md`.

## Open Questions

- Severity definitions, notification/reporting duties, recovery objectives, contact tree, evidence retention, and post-incident approval are pending.
