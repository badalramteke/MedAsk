# Threat Model

Purpose: Identifies priority threats to MediKiosk and required mitigations; read before implementation, security review, and release.

## Assets to protect

- Patient identity, consent, history, documents, summaries, and FHIR hand-off data.
- Session state, service credentials, encryption keys, and provider configuration.
- Alert integrity, clinician-edit history, and external delivery status.

## Priority threats

| Threat | Example | Required mitigation |
| --- | --- | --- |
| Unauthorized access | Another patient/staff member views a record | Session isolation, role/purpose authorization, audited access |
| Data disclosure | PHI appears in logs, errors, model prompts, or third-party service | Minimum necessary data, redaction, provider policy, output/log controls |
| Data tampering | Summary, consent state, or FHIR payload is changed | Typed validation, provenance, audit trail, least privilege |
| Identity/consent misuse | A session is linked/shared without valid authorization | Server-side consent verification and approved ABHA/HIS integration flow |
| Prompt injection | Scanned document tells a model to ignore policy | Treat documents as untrusted data, constrain task/output, validate result |
| Unsafe clinical output | Model presents diagnosis/advice or hides uncertainty | Draft-only policy, deterministic controls, clinician review, red-team tests |
| Missed/misrouted alert | A red-flag event does not reach triage staff | Versioned rules, recipient monitoring, acknowledgement state, failure visibility |
| Low-network loss/duplication | Retry loses a draft or duplicates external submission | Encrypted checkpoints, idempotent delivery, truthful state model |
| Dependency/provider compromise | A package or external provider becomes unsafe/unavailable | Pinned/reviewed dependencies, secrets isolation, provider abstraction, fallback validation |

## Security review requirements

- Review threats at each new plugin, model provider, document type, route, and external integration.
- Test direct and indirect prompt injection, authorization bypass, data leakage, invalid input, failed delivery, and alert-recipient outage.
- Treat reproducible PHI exposure, credentials exposure, false delivery status, or autonomous clinical output as release blockers.

## Sources

- [CERT-In secure application guidelines](https://www.cert-in.org.in/PDF/Application_Security_Guidelines.pdf).
- [OWASP prompt-injection guidance](https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html).

→ For adversarial model testing, see `docs/ai/RED_TEAM_PLAN.md`.

## Open Questions

- Formal risk-owner assignments, risk ratings, accepted-risk process, penetration-test scope, and incident reporting obligations require hospital/deployment approval.
