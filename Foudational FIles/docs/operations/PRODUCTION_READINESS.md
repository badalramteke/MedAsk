# Production Readiness

Purpose: Defines the evidence required before MediKiosk is described as production-ready; read before a pilot or production release decision.

## Readiness checklist

| Area | Required evidence |
| --- | --- |
| Clinical governance | Approved question flows, red-flag rules, translations, AYUSH workflow, clinician review ownership |
| Safety | No autonomous diagnosis/advice, draft-only workflow, alert delivery/acknowledgement tests, known limitations documented |
| Privacy/legal | Hospital role agreement, consent/revocation workflow, retention policy, DPDP/legal review, grievance/contact process |
| Security | Threat model review, secure configuration/secrets, access policy, audit design, vulnerability testing, incident process |
| AI | Versioned models/prompts/rules, evaluation evidence, red-team results, fallback validation, release approval |
| Data | Schema/migration review, backup/restore evidence, deletion/expiry controls, provenance/audit handling |
| Integration | Approved HIS/ABDM mapping, sandbox/target acceptance, truthful delivery/retry behavior, support contacts |
| Operations | Monitoring, health checks, alerting, runbooks, on-call/escalation owner, deployment rollback plan |
| Accessibility | Target-user testing for voice/touch, languages, audio prompts, low-literacy flow, and failure fallback |

## Release rule

- Any unresolved patient-data disclosure, unapproved clinical workflow, autonomous clinical output, untruthful delivery result, or red-flag alert failure blocks production release.

## Open Questions

- Approved measurable readiness thresholds, signed owners, audit/certification requirements, SLOs, recovery objectives, and pilot go-live authority are pending.
