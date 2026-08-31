# Data Minimization

Purpose: Defines the minimum-data and retention approach for MediKiosk; read before adding a field, log, model input, document store, or analytics use.

## Rules

- Collect and use only data necessary for the stated consented intake, document-processing, summary, and permitted sharing purpose.
- Send only minimum task-specific context to a model/provider; do not send unrelated patient records.
- Separate volatile processing inputs, resumable session state, clinician-approved records, and audit evidence.
- Do not use identifiable patient data for model training, analytics, or future features without separately approved governance and purpose/consent.

## Data handling baseline

| Data category | Default handling |
| --- | --- |
| Microphone chunks/camera frames | Volatile processing only; do not retain as routine records |
| Active dialogue state | Short-lived, encrypted/resumable only where necessary; purge on completion, cancellation, or approved expiry |
| Patient history and document extraction | Keep only validated, necessary fields with provenance for the clinician draft/approved record workflow |
| Original source documents | Retain only with explicit consent and approved hospital retention policy; otherwise delete after permitted processing |
| Consent and delivery evidence | Retain only as required for proof, audit, and applicable policy |
| Logs/metrics | Use de-identified/aggregated operational data where possible; exclude raw PHI and secrets |

## Change test

Before adding data collection, answer:

1. What approved purpose needs it?
2. Is there a lower-data alternative?
3. Which consent scope/notice covers it?
4. Who can access it, and for how long?
5. Can it be excluded from logs, prompts, exports, and test data?
6. What deletes it when the purpose ends?

## Sources

- [ABDM privacy policy](https://abdm.gov.in/abha-PRIVACY-POLICY-english) describes collection/use limitation and non-retention when data is no longer necessary.
- [ABDM privacy and security overview](https://abdm.gov.in/static/media/Session%206%20-%20Digital%20health%20-%20Privacy%20%26%20Security.083a5b3e73ba533e321b.pdf) identifies need-to-know access and limited collection.
- [Digital Personal Data Protection Act, 2023](https://www.indiacode.nic.in/bitstream/123456789/22037/2/a2023-22.pdf).

## Open Questions

- Approved retention schedule, deletion evidence, local-resume expiry, audit-log retention, document-retention policy, and provider data-processing terms remain pending.
