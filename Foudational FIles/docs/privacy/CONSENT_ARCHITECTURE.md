# Consent Architecture

Purpose: Defines consent-state requirements for MediKiosk data collection and sharing; read before implementing intake, external sharing, or consent UI.

## Consent principles

- Consent is explicit, purpose-specific, granular, revocable, and explained through accessible audio and touch UI.
- The patient controls whether eligible records are shared through ABDM; no sharing occurs merely because an ABHA identifier exists.
- Consent records are evidence of permission, not a substitute for identity, authorization, or clinical review.
- The consent UI must not pressure a patient or obscure refusal/revocation choices.

## Required consent scopes

| Scope | Covers | Minimum state |
| --- | --- | --- |
| Intake | Voice/touch history and applicable AYUSH answers | Granted / denied / withdrawn |
| Document processing | Scanning, extraction, and configured retention of source documents | Granted / denied / withdrawn |
| Summary creation | Creation of clinician-reviewable draft | Granted / denied / withdrawn |
| HIS/ABDM sharing | Permitted FHIR hand-off/linking for stated recipient and purpose | Granted / denied / withdrawn / expired |

## Consent lifecycle

1. Present purpose, data categories, recipient, duration, and refusal/revocation option in the selected language.
2. Capture the affirmative consent event with user interaction method, time, policy/version, scope, and session/identity context.
3. Enforce scope before each sensitive collection, processing, or sharing action.
4. Allow revocation through the configured patient/hospital workflow and stop future processing/sharing within that scope.
5. Preserve evidence of the consent/revocation event only as permitted by retention policy; do not retain data no longer necessary.

## ABDM boundary

- ABDM describes a consent-based, federated model in which records remain with the provider/where created and are shared with the patient’s consent.
- Exact consent artefact format, endpoints, identity flow, and integration behavior must use approved ABDM specifications—not guesses in this documentation.

## Sources

- [ABDM FAQ: consent-based record sharing and revocation](https://abdm.gov.in/FAQ).
- [ABDM Health Data Management Policy](https://abdm.gov.in/static/media/health_management_policy_bac9429a79.80f74bc3e039c00acd4f.pdf).
- [Digital Personal Data Protection Act, 2023](https://www.indiacode.nic.in/bitstream/123456789/22037/2/a2023-22.pdf).

→ For retention and minimization, see `docs/privacy/DATA_MINIMIZATION.md`.

## Open Questions

- Final consent language, accessibility scripts, identity proofing, consent artefact integration, withdrawal workflow, and retention period require legal/hospital approval.
