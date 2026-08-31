# Rules

## Hard rules
- Never hardcode secrets, API keys, tokens, or credentials in code, config files, or notes.
- Do not perform autonomous medical diagnosis or claim clinical judgment beyond approved project documentation.
- Never bypass PatientDataObject as the source of truth for patient data and workflow state.
- No direct database access from routes, services, or handlers; keep persistence behind the planned data layer.
- Preserve the plugin architecture; do not fold plugin logic into route-level code or bypass interfaces.
- Do not invent missing APIs, endpoints, payloads, or integrations.
- Never assume ABDM or FHIR behavior without explicit documentation or human confirmation.
- If clinical terminology, medical safety, or protocol details are uncertain, ask before proceeding.
- Frontend Element Attribute Rule: Every interactive/identifiable frontend UI element must include `data-element`, `data-voice-action`, `data-testid`, `id`, and `aria-label`.
- Frontend Route Catalog Rule: All frontend routes and pages must be documented in `docs/architecture/PATHS.md`.
- Follow the .ai memory workflow at the start and end of every session.
- Keep .ai changes limited to memory and agent context; do not write project documentation here.

## Do not invent
- No fabricated endpoint behavior.
- No guessed clinical rules.
- No assumed integration contracts.
- No hidden assumptions about hospital systems, ABDM flows, or compliance behavior.
- If something is unclear, treat it as unknown and ask instead of guessing.

