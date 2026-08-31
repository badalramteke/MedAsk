# Plugin Interface

Purpose: Defines the single extension contract for MediKiosk modules and adapters; read this before creating any current or future plugin.

## Contract objective

- Current modules A–D and future approved capabilities use the same lifecycle.
- Each plugin has one concern and never invokes another plugin directly.
- Every meaningful data exchange occurs through PatientDataObject.
- A new plugin is added by creating its own package and one approved manifest entry; it does not change existing plugins, the core schema, or central route wiring.

## Plugin declaration

Each plugin declares the following metadata in the approved plugin manifest:

| Field | Meaning |
| --- | --- |
| `id` | Stable, unique plugin identifier |
| `version` | Plugin contract version |
| `kind` | Product module, provider adapter, or integration adapter |
| `capabilities` | Explicit supported operations |
| `input_contract` | Accepted PatientDataObject state and required consent/session conditions |
| `output_namespace` | Reserved namespaced location under `plugin_outputs` |
| `routes` | Optional plugin-owned API route declarations |
| `configuration` | Environment/configuration keys; never secret values |
| `health_check` | Availability/readiness contract |

## Runtime lifecycle

1. **Discover:** the application reads a controlled manifest at startup.
2. **Validate:** IDs, versions, namespaces, route declarations, and configuration are checked before activation.
3. **Authorize:** the workflow confirms required consent and actor permissions.
4. **Execute:** the plugin receives an immutable input snapshot and permitted execution context.
5. **Return:** it emits a typed result; the orchestrator validates and applies the update.
6. **Observe:** it emits non-sensitive status/health information and audit-safe provenance.

## Input and output contract

| Contract element | Requirement |
| --- | --- |
| Input | Valid PatientDataObject snapshot plus minimal execution context |
| Output | Validated patch, output namespace data, provenance, status, declared events, and recoverable errors |
| Data ownership | Core fields are written only through allowed validated patches; plugin-specific data stays in the declared namespace |
| Provenance | Identify plugin ID/version, time, source type, and validation status; do not store secrets or unnecessary raw input |
| Failure | Use standard error category, indicate whether retry is safe, and leave state unchanged unless the update validates |
| Side effects | Must be declared; external delivery requires a truthful outcome status |

## Route registration

- A plugin that needs an API surface declares its own route module in its manifest.
- The gateway registers routes only from allow-listed, startup-validated plugins.
- Route handlers remain transport-only and delegate to the plugin/use-case service boundary.
- A plugin may not override another plugin’s route, namespace, or capability.

## Required safety rules

- No plugin may make an autonomous diagnosis, treatment recommendation, prescription, or final clinical commitment.
- Clinical plugins must preserve the editable-draft boundary and route red-flag events to the configured staff-alert mechanism.
- Provider plugins must be called only through their respective abstraction (for AI, ModelService).
- Integration plugins may not invent ABDM/HIS protocol behavior; they require approved mappings/configuration.
- Plugin removal or disablement must fail safely and preserve already approved durable records.

## Reference plugin roles

| Plugin | Role |
| --- | --- |
| History Engine | Produces structured history updates and red-flag alert events |
| Document Digitization | Produces extracted document data and chronology updates |
| Summary Generator | Produces an editable summary draft and local-language confirmation request |
| Consent + Integration | Manages consent-state updates and permitted FHIR/HIS/ABDM hand-off |
| Future approved plugin | Uses its own namespace and manifest entry without modifying the above |

→ For data extensions, see `docs/database/PATIENT_DATA_OBJECT.md`.
→ For route contracts, see `docs/api/API_CONTRACTS.md`.
→ For model-provider isolation, see `docs/ai/MODEL_ABSTRACTION.md`.

## Open Questions

- Final manifest file format, package layout, signature/approval process, and runtime deployment location are implementation decisions.
- Exact per-plugin consent scopes and staff permissions await the consent and authorization design.
