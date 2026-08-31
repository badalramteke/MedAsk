# Operations Runbooks

Purpose: Defines the minimum runbook set for MediKiosk; read during routine operations or when creating a detailed operational procedure.

## Required runbooks

| Runbook | Trigger | Safe first actions |
| --- | --- | --- |
| Service health | Health/readiness failure | Identify affected environment/service; use correlation IDs; do not expose PHI in diagnostics |
| ASR/model/OCR outage | Provider unavailable or invalid output | Use touch/clinician fallback; preserve truthful status; do not bypass safety controls |
| Low-network interruption | Kiosk loses connectivity | Preserve permitted encrypted resumable session; display queued/interrupted state; retry safely |
| HIS/ABDM delivery failure | External hand-off rejected/failed | Preserve recoverable draft; record safe outcome; follow approved escalation path |
| Red-flag alert delivery failure | Recipient not reached/acknowledgement unavailable | Surface failure immediately to configured operations/triage workflow; do not silently continue |
| Consent withdrawal | Patient withdraws scope | Stop future scoped processing/sharing and follow approved retention workflow |
| Security event | Suspected data/credential/authorization issue | Contain access, preserve approved evidence, activate incident process |

## Runbook rules

- Write detailed procedures only after owners, contacts, systems, and escalation paths are approved.
- Use least-privilege access and audit-safe diagnostic data.
- Do not delete records, rotate secrets, resend data, or alter clinical state without an approved procedure and authority.
- Record completion/outcome and unresolved risks for handoff.

→ For incident lifecycle, see `docs/operations/INCIDENT_RECOVERY.md`.

## Open Questions

- Named owners, contact tree, monitoring tools, escalation timings, support hours, and approved remediation commands are pending.
