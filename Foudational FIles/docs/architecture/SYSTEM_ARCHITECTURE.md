# System Architecture

Purpose: Defines MediKiosk's system boundaries, data flow, and module relationships; read this before designing a service, plugin, or integration.

## Scope boundary

- Current scope is limited to four modules:
  - Module A: conversational history engine, including red-flag alerting and AYUSH history mode.
  - Module B: medical-document digitization and structured extraction.
  - Module C: editable, physician-facing history-summary generation and patient-facing audio confirmation.
  - Module D: consent, ABHA/ABDM linkage, FHIR mapping, and HIS hand-off.
- MediKiosk prepares a clinical-history draft. It does not diagnose, prescribe, replace an HIS/EMR, or manufacture kiosk hardware.
- Future ideas belong only in `docs/product/FUTURE.md` until they are approved and added to the PRD.

## Logical architecture

```text
Patient voice / touch / documents
            |
            v
Kiosk UI (Next.js) <--> API gateway (FastAPI)
            |                    |
            |                    v
            |          Session + consent boundary
            |                    |
            v                    v
      PatientDataObject <--> approved plugins
                                  |- Module A: history + triage alert
                                  |- Module B: document extraction
                                  |- Module C: summary draft
                                  `- Module D: ABDM/HIS hand-off
                                             |
                                             v
                           FHIR R4 mapping -> HIS / ABDM boundary
```

## Architectural rules

- `PatientDataObject` is the canonical internal contract. Plugins read it and return validated, attributable updates; they do not call one another directly.
- Plugins implement the contract in `PLUGIN_INTERFACE.md` and are loaded from an approved manifest at startup.
- Plugins may own their API routes; the gateway loads only approved route declarations. A central route file is not manually edited for a new plugin.
- The stable PatientDataObject core is extended through namespaced plugin outputs, so a future plugin does not require a core-schema change.
- Every AI request goes through `ModelService`; no route handler or business workflow calls a model-provider SDK directly.
- Clinical rules, API routing, persistence, model/provider adapters, and FHIR mapping remain separate concerns.
- The physician remains the final reviewer: generated summaries are editable drafts, never autonomous diagnoses or final records.

## Main layers

| Layer | Responsibility | Must not do |
| --- | --- | --- |
| Patient interface | Voice/touch interaction, accessible prompts, document capture, local progress UI | Make clinical decisions or persist clinical data directly |
| API gateway | Authenticate/authorize requests, validate transport payloads, stream audio, load approved plugin routes | Contain clinical or persistence business logic |
| Workflow and plugin layer | Run each module against PatientDataObject and emit validated updates/events | Bypass the model, data, consent, or plugin contracts |
| Model and provider layer | Provide model, ASR/TTS, OCR, and integration adapters behind stable interfaces | Leak provider-specific behavior into modules |
| Data layer | Store approved durable data and short-lived resumable state according to retention policy | Be called directly by routes |
| Integration layer | Produce validated FHIR R4 outputs and use hospital/ABDM adapters | Invent external endpoint behavior or credentials |

## Resilience and low-network design

- Voice always has a touch alternative.
- The kiosk may keep an encrypted, short-lived resumable session while connectivity is interrupted.
- Final external submission occurs only when the configured integration is reachable and validation succeeds.
- A failed submission resumes from the last valid session state; it must not silently drop the draft or falsely report delivery.
- Exact offline encryption, retry, conflict, and expiry controls are defined in `OFFLINE_SYNC.md` and remain implementation decisions until validated.

## Extension path

To add a future approved capability:

1. Add one plugin implementing the shared interface.
2. Declare its manifest entry and, if needed, its owned routes.
3. Store additions under its namespaced `plugin_outputs` area with provenance.
4. Add only its own focused documentation and tests.

Existing modules, core PatientDataObject fields, and central routing are not changed for that extension.

→ For plugin contracts, see `docs/architecture/PLUGIN_INTERFACE.md`.
→ For the canonical data contract, see `docs/database/PATIENT_DATA_OBJECT.md`.
→ For clinical safety boundaries, see `docs/clinical/CLINICAL_SAFETY.md`.
→ For deployment-specific implementation, see `docs/operations/DEPLOYMENT.md`.

## Open Questions

- Exact ABDM sandbox/HIS endpoint and credential arrangements are not yet available.
- Service-level objectives, retry limits, and hospital-specific network constraints are pending approval.
