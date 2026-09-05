# DPDP Compliance

Purpose: Records a proposed DPDP compliance approach for MediKiosk; read before making privacy claims or processing patient data in a deployment.

## Compliance position

- This is a design checklist, not legal advice or a certification of compliance.
- The deploying hospital should be treated as the proposed Data Fiduciary for its patient-care deployment; MediKiosk’s legal role must be fixed by written agreement and legal review.
- Requirements and commencement dates must be rechecked against current notifications before release.

## Design checklist

| Area | MediKiosk requirement |
| --- | --- |
| Lawful/purpose-limited processing | Define the care-intake purpose and do not reuse data for a new purpose without appropriate authority/consent |
| Notice and consent | Give clear accessible notice; record granular affirmative consent and support withdrawal |
| Data principal rights | Design supported processes for access, correction/erasure, grievance, and applicable requests |
| Security safeguards | Apply reasonable security practices, least privilege, secure development, and incident handling |
| Retention | Erase data when no longer necessary for the stated purpose, subject to lawful/hospital record obligations |
| Children | Do not deploy child-data processing until age/guardian requirements and applicable rules are approved |
| Vendors/providers | Document provider data handling, purpose, location, retention, and security controls before enablement |
| Governance | Name responsible contacts, risk owners, processors/roles, policy/version evidence, and review cadence |

## Current legal-status note

- The DPDP Act has phased commencement notifications. This documentation must not assert that every provision applies on the same date; legal counsel must validate the applicable timeline and rules for the deployment date.

## Sources

- [Digital Personal Data Protection Act, 2023](https://www.indiacode.nic.in/bitstream/123456789/22037/2/a2023-22.pdf).
- [2025 commencement notification](https://egazette.gov.in/WriteReadData/2025/267647.pdf).
- [ABDM FAQ](https://abdm.gov.in/FAQ) on health-record consent and applicable legal framework.

→ For operational consent design, see `docs/privacy/CONSENT_ARCHITECTURE.md`.

## Open Questions

- Formal Data Fiduciary/processor allocation, grievance contact, retention schedule, child-data workflow, breach process, vendor agreements, and legal sign-off are pending.
