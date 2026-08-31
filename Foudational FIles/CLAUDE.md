# MediKiosk AI Working Context

Purpose: Provides portable project instructions for AI assistants working on MediKiosk; read before proposing or making project changes.

## Mission

MediKiosk is a patient-facing clinical-intake platform for Indian hospital OPDs. It captures structured voice/touch history, digitizes patient-provided records, produces a clinician-editable draft, and supports consented HIS/ABDM hand-off before consultation.

## Current scope

- Module A: conversational history, AYUSH history mode, and staff red-flag alerts.
- Module B: document digitization, structured extraction, and chronology.
- Module C: bilingual confirmation and clinician-editable summary draft.
- Module D: consent, ABHA/ABDM/FHIR/HIS hand-off.

Everything else is out of scope until approved in `docs/product/PRD.md`. `docs/product/FUTURE.md` is not a work queue.

## Non-negotiable rules

- No autonomous diagnosis, treatment recommendation, prescription, or final clinical record.
- PatientDataObject is the canonical workflow contract; modules never call each other directly.
- Every module/provider/integration follows the plugin interface and uses a controlled manifest.
- Future functionality must be a new plugin namespace, not a core rewrite.
- All model calls go through ModelService; all configuration/secrets remain outside code.
- Keep routes thin, validate all input/output, preserve provenance/uncertainty, and never fake HIS/ABDM delivery success.
- Ask/mark as open questions when clinical, hospital, legal, or integration details are not approved.

## Essential documents

- `ps.md`, `docs/product/PRD.md`, `docs/architecture/TECH_STACK.md`
- `docs/product/SCOPE.md`, `docs/product/MODULES.md`
- `docs/architecture/PLUGIN_INTERFACE.md`, `docs/database/PATIENT_DATA_OBJECT.md`
- `.ai/CONTEXT.md` and `.ai/memory/`

## Open Questions

- Exact clinical question banks, ABDM/Bhashini credentials, HIS integration, retention policy, and production operations are pending.
