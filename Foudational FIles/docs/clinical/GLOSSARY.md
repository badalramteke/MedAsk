# Clinical Glossary

Purpose: Defines terms used in MediKiosk documentation; read when interpreting product, clinical, AI, or integration requirements.

| Term | MediKiosk meaning |
| --- | --- |
| Chief complaint | The patient’s main reason for seeking care, captured in their words and structured form. |
| HPI | History of Present Illness: chronological detail about the current concern. |
| ROS | Review of Systems: structured inquiry for symptoms not already covered. |
| SOCRATES | Symptom/pain-history framework: Site, Onset, Character, Radiation, Associated factors, Timing, Exacerbating/relieving factors, Severity. |
| Red flag | A configured possible-emergency indicator that creates a staff alert; it is not a diagnosis. |
| Triage | Staff-led prioritization by urgency. |
| Editable draft | A summary that a clinician can accept, amend, or reject; it is not a final autonomous record. |
| AYUSH mode | The configured intake branch for AYUSH history frameworks. |
| Dashavidha Pariksha | Tenfold Ayurvedic assessment framework documented in `DASHAVIDHA_PARIKSHA.md`. |
| Ahara-Vihara | Named AYUSH history area concerning diet and lifestyle; detailed values require clinician approval. |
| PatientDataObject | The canonical internal data contract through which modules exchange validated patient-state updates. |
| Provenance | Information about where a data item came from, such as patient input, source document, plugin, model version, or clinician edit. |
| FHIR R4 | The interoperability standard selected for structured data mapping at the HIS/ABDM boundary. |

→ For full clinical protocol context, see `docs/clinical/CLINICAL_PROTOCOLS.md`.

## Open Questions

- Local-language term glossary and clinician-approved patient-facing translations are pending.
