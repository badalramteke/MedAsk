# Low-Network Session Resilience

Purpose: Defines how MediKiosk preserves a safe intake session during poor connectivity; read this before implementing local persistence, retries, or delivery status.

## Scope

- MediKiosk is designed for unreliable or low-bandwidth connectivity, not as a fully offline clinical platform.
- Patient interview progress may be resumed after a recoverable network interruption.
- HIS/ABDM delivery requires the configured external connection and must not be simulated as successful.

## Design principles

- Voice input always has touch fallback.
- Keep only the minimum necessary session data locally and for the shortest approved period.
- Encrypt any locally persisted resumable session data.
- Preserve a clear distinction between **draft saved locally**, **queued for delivery**, **delivered**, and **delivery failed**.
- Never duplicate or overwrite a clinician-approved record during retry.

## State model

| State | Meaning | Permitted action |
| --- | --- | --- |
| Active | Interview is progressing | Update short-lived session state |
| Interrupted | Connectivity/service interruption occurred | Preserve encrypted resumable state and offer resume |
| Queued | Valid submission awaits connectivity | Retry through the integration boundary |
| Delivered | External system confirms accepted delivery | Record delivery outcome and complete session handling |
| Failed | Delivery cannot safely complete | Keep recoverable draft only for approved expiry window and show truthful status |
| Expired/cleared | Session was completed, cancelled, or exceeded policy | Purge temporary state |

## Resume and retry rules

- Resume from the last validated PatientDataObject checkpoint, not from raw audio or camera frames.
- Retry only idempotent/identified integration operations; a retry must not create duplicate submissions.
- If the external destination is unavailable, do not fabricate an ABDM/HIS response or mark the consultation package delivered.
- A patient or authorized staff member may continue a recoverable session under the final identity/consent rules.

## Data handling

- Audio chunks and camera frames are volatile processing inputs, not offline archives.
- The proposed short-lived dialogue checkpoint is Redis-backed in normal operation; the exact encrypted local fallback technology is TBD.
- Durable records follow the hospital-approved retention policy, not the local-resume policy.

## Open Questions

- Exact local storage technology, encryption/key handling, retry cadence, session expiry, and conflict resolution are pending implementation and hospital policy.
- ABDM/HIS idempotency and recovery behavior must be verified against approved integration specifications.
