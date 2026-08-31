# PatientDataObject

Purpose: Defines MediKiosk’s canonical, extensible patient-workflow data contract; read before any module, API, database, or FHIR change.

## Contract role

- PatientDataObject is the single source of truth for the active clinical-intake workflow.
- Modules never communicate directly; each reads a validated snapshot and returns a validated patch.
- It is an internal canonical model mapped to FHIR at the integration boundary; it is not itself a FHIR resource.
- The core stays stable while future approved plugins use namespaced outputs.

## Stable core areas

| Area | Contents |
| --- | --- |
| Identity context | Internal session/patient reference, approved external identity references, preferred language, facility/deployment scope |
| Consent context | Scope, purpose, status, evidence reference, expiry/withdrawal state |
| Intake status | Session lifecycle, completeness, version, pending review/processing state |
| Patient-reported history | Chief complaint, HPI, past medical/surgical, medications/allergies, family, personal, ROS, applicable reproductive history |
| AYUSH history | Selected workflow and approved fields for Trividha, Ashtavidha, Dashavidha, Ahara-Vihara and related named scope |
| Documents and timeline | Permitted source references, extraction candidates, dates/uncertainty, review status |
| Summary draft | Structured clinician-editable draft, language, generation provenance, review status |
| Alerts | Red-flag candidate/rule evidence, lifecycle, recipient acknowledgement state |
| Integration status | Prepared/queued/accepted/rejected/failed hand-off metadata; never false success |
| Provenance | Source type, plugin/prompt/model/rule/schema version, timestamp, confidence/uncertainty, editor/review status |

## Extension area

```text
plugin_outputs:
  <reverse-domain-or-approved-plugin-id>:
    schema_version: <plugin schema version>
    data: <plugin-owned validated data>
    provenance: <source and processing metadata>
```

- A plugin owns only its declared namespace.
- New plugins add a namespace through their manifest; they do not alter stable core fields.
- Unknown namespaces are preserved safely but ignored by consumers that do not support them.
- Plugin outputs must not overwrite core clinical facts or bypass consent/authorization.

## Patch and validation rules

- Apply atomic, typed patches against a known object version.
- Reject invalid, stale, unauthorized, or out-of-scope patches without partial mutation.
- Preserve patient-reported text and distinguish it from extracted, model-generated, and clinician-edited fields.
- Validate core fields centrally; validate extension fields through the owning plugin schema.
- Record every material update with provenance and lifecycle/review status.

## FHIR mapping boundary

- Only the approved FHIR adapter converts validated PatientDataObject data to FHIR R4.
- FHIR mapping does not erase draft/review/provenance information required inside MediKiosk.
- No module writes a FHIR payload directly.

→ For plugin lifecycle, see `docs/architecture/PLUGIN_INTERFACE.md`.
→ For FHIR mapping, see `docs/integrations/ABDM_FHIR_SPEC.md`.

## Open Questions

- Exact Pydantic schema, required/optional fields, consent artefact fields, identities, code systems, reproductive-history workflow, persistence snapshots, and FHIR mapping approval are pending.
