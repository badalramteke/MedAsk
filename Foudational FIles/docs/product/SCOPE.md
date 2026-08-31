# Product Scope

Purpose: Defines what MediKiosk will and will not build now; read before proposing, planning, or approving any feature.

## In scope: SIH foundation and MVP

- Patient-facing multimodal intake: icon-driven touch, voice interaction, local-language prompts, and zero-training accessibility.
- Module A: adaptive clinical history capture using approved frameworks, AYUSH history mode, and red-flag staff alerts.
- Module B: multilingual digitization/extraction and chronological organization of patient-provided medical documents.
- Module C: structured, bilingual patient/clinician output with an editable clinician draft.
- Module D: granular consent, permitted ABHA/ABDM linkage, FHIR payload preparation, and HIS hand-off.
- Production-oriented modularity: PatientDataObject, plugin boundaries, ModelService, security, privacy, and low-network resilience.

## Explicitly out of scope

- Autonomous diagnosis, disease exclusion, treatment advice, or prescriptions.
- Physical kiosk/scanner hardware manufacturing.
- Full HIS/EMR replacement or hospital operations management.
- Any feature listed only in `docs/product/FUTURE.md`.
- Unapproved population analytics, biometric/voice-marker analysis, menstrual tracking beyond the approved applicable history field, epidemic detection, or sensor/IoT integration.

## Future boundary

- Future ideas may shape extension boundaries but are not current work.
- A future capability becomes eligible only when explicitly approved and moved into `PRD.md`.
- It must enter as a new plugin/namespace without changing existing core modules, central routing, or core PatientDataObject schema.

## Sources of truth

- `ps.md`
- `docs/product/PRD.md`
- `docs/architecture/TECH_STACK.md`

→ For the four modules, see `docs/product/MODULES.md`.

## Open Questions

- MVP demonstration definition, provider/service availability, hospital partner, certified ABDM scope, and production rollout criteria are pending.
