# Security Model

Purpose: Defines MediKiosk security boundaries and access expectations; read before designing authentication, authorization, storage, integrations, or operations.

## Security objectives

- Protect patient health and identity data from unauthorized access, alteration, loss, and disclosure.
- Enforce consent and purpose limits at every sensitive workflow boundary.
- Preserve clinician and triage-staff accountability without exposing unnecessary clinical content.
- Operate safely in low-network conditions without claiming external delivery that has not occurred.

## Trust boundaries

| Boundary | Required control |
| --- | --- |
| Patient kiosk to API | Encrypted transport, server-side validation, session isolation, rate/abuse controls |
| API to plugin/model provider | Approved plugin/configuration only, minimum necessary data, ModelService abstraction, typed validation |
| API to data services | Least-privilege service identity, parameterized data access, encrypted storage, audit-safe logging |
| Integration to HIS/ABDM | Approved credentials/configuration, FHIR validation, consent/purpose check, delivery receipt handling |
| Staff access | Role and purpose-based authorization, auditability, no broad default record access |

## Proposed minimum role model

| Actor | Minimum access |
| --- | --- |
| Patient | Their in-progress intake and permitted confirmation/review screen |
| Triage staff | Red-flag alert and minimum necessary patient context; alert acknowledgement/escalation |
| Clinician | Full editable draft and permitted linked records for the consultation |
| Administrator/IT support | Operational metadata by default; clinical-content access only through approved, audited break-glass policy |
| Integration service | Only the scoped data/configuration required for the permitted external hand-off |

## Mandatory controls

- Use encrypted transport and encrypted storage; select exact algorithms/key-management implementation before deployment.
- Keep credentials, endpoints, feature flags, and provider selection in environment/configuration, never source code.
- Validate all client input server-side and treat document/OCR/ASR content as untrusted.
- Minimize logs; never write raw health content, tokens, secrets, or unredacted identifiers to routine logs.
- Record security-relevant events, consent lifecycle, alert lifecycle, clinician edits, and external delivery outcomes under approved retention rules.
- Apply least privilege, secure dependency management, security testing, patching, and incident response.

## Sources

- [CERT-In secure application guidelines](https://www.cert-in.org.in/PDF/Application_Security_Guidelines.pdf).
- [ABDM privacy and security overview](https://abdm.gov.in/static/media/Session%206%20-%20Digital%20health%20-%20Privacy%20%26%20Security.083a5b3e73ba533e321b.pdf).

→ For risks and mitigations, see `docs/security/THREAT_MODEL.md`.
→ For consent controls, see `docs/privacy/CONSENT_ARCHITECTURE.md`.

## Open Questions

- Exact authentication method, cryptographic configuration, key management, break-glass process, audit retention, and hospital access-policy approval are pending.
