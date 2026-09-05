# Testing Strategy

Purpose: Defines required testing layers for MediKiosk; read before implementing tests, accepting work, or approving a release.

## Test principles

- Use synthetic or de-identified data unless an approved governance process permits otherwise.
- Test every enabled language/provider/fallback path and record known limitations.
- Clinical review is required for clinical content; automated tests do not certify medical safety.
- Test failure states as seriously as successful paths.

## Test layers

| Layer | What to validate |
| --- | --- |
| Unit | Typed validation, consent/state transitions, plugin contract, rule behavior, FHIR mapping helpers |
| Integration | API-to-service-to-plugin flow, provider adapters, Redis/data store, mock HIS/ABDM hand-off |
| End-to-end | Identify → consent → history → documents → summary → clinician review → hand-off state |
| Clinical safety | Draft-only boundary, no diagnosis/advice, question-flow scope, alert evidence/acknowledgement behavior |
| AI evaluation | Faithfulness, uncertainty, extraction, prompt injection, fallback parity, model/prompt version changes |
| Accessibility | Voice/touch parity, audio guidance, language flow, low-literacy/elderly usability, failure fallback |
| Security | Authorization, session isolation, secrets/logging, upload validation, dependency and injection testing |
| Resilience | Network interruption/resume, retries/idempotency, provider outage, queue/delivery truthfulness |
| Performance/load | Representative high-throughput scenarios only after approved workload/targets are defined |

## Required release evidence

- Passing automated tests and documented manual/clinical/accessibility review.
- No unresolved critical safety, privacy, security, red-flag delivery, or data-integrity finding.
- Versioned evidence for models, prompts, rules, plugins, schemas, and integrations.
- Explicit record of scenarios not tested and why.

→ For AI-specific evaluation, see `docs/ai/AI_EVALUATION.md`.
→ For red-team tests, see `docs/ai/RED_TEAM_PLAN.md`.

## Open Questions

- Test framework/toolchain, environments, datasets, coverage targets, load profiles, clinical reviewers, acceptance thresholds, and release authority are pending.
