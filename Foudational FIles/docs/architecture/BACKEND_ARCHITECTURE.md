# Backend Architecture

Purpose: Defines backend responsibilities and boundaries for MediKiosk; read this before adding an API, workflow, persistence adapter, or integration.

## Chosen foundation

| Concern | Decision |
| --- | --- |
| API framework | FastAPI, served by Uvicorn |
| Transport validation | Pydantic models; PatientDataObject is the canonical workflow contract |
| Conversation orchestration | LangGraph, with LangChain as the model-interaction layer |
| Model access | Provider-neutral `ModelService` abstraction |
| Durable data | PostgreSQL through Supabase, self-hosted for hospital production and managed service where approved for demo |
| Short-lived session state | Redis, with the currently proposed 10-minute TTL |
| Deployment form | Docker and Docker Compose for development and hospital-edge deployment |

## Request path

1. A route validates its transport payload and establishes the caller/session context.
2. A use-case service checks consent and authorization, then loads or creates PatientDataObject state through the data layer.
3. The service invokes an approved plugin or workflow.
4. The plugin returns a validated update, status, provenance, and declared events.
5. The service persists only permitted state, returns a transport-safe response, and emits an audit-safe event.

## Required boundaries

- Route handlers are thin: no clinical logic, direct database access, direct model-provider calls, or FHIR construction.
- Use-case services coordinate a single workflow concern and enforce consent/session rules.
- Plugins own module-specific behavior and communicate only through PatientDataObject.
- Provider adapters isolate Bhashini, AI4Bharat, MedGemma, Gemini/Grok fallback, OCR, and HIS/ABDM implementation details.
- Repositories/data services isolate PostgreSQL, Redis, and artifact-storage behavior.
- FHIR mapping belongs to the integration boundary, not the summary or history plugins.

## Model and provider routing

- MedGemma 4B is the primary multimodal model for image/document understanding.
- MedGemma 27B is the primary text model for higher-capacity text tasks when hardware permits.
- The ModelService selects the provider based on configured environment and capability.
- For the hackathon, local/Colab model serving supports the low-network demo path; approved online APIs may be used for the online demo path.
- Gemini or Grok may be configured as a fallback only through ModelService. A fallback must preserve the same safety, logging, consent, and output-validation controls.

## State and data handling

- Volatile microphone chunks and camera frames are not durable records.
- Active dialogue state is short-lived and resumable after a recoverable connectivity failure.
- Consent evidence, clinician-approved summaries, FHIR submission outcomes, and approved source-document references are durable only under the hospital-approved retention policy.
- Original source documents are retained only with explicit consent and an approved hospital retention policy; otherwise they are deleted after permitted processing.

## Production guardrails

- All configuration, credentials, provider URLs, and feature/plugin selection come from environment/configuration—not source code.
- Startup fails closed when a required plugin contract or configuration is invalid.
- Logs and health checks must not expose patient-identifying or clinical content.
- The backend reports delivery status truthfully; it never treats a queued or failed HIS/ABDM push as complete.

## Sources

- [FastAPI documentation](https://fastapi.tiangolo.com/) for the selected API framework and WebSocket capability.
- [LangGraph Graph API overview](https://langchain-ai.github.io/langgraph/how-tos/state-reducers/) for graph state, nodes, and conditional workflow control.
- [LangGraph persistence concepts](https://langchain-ai.github.io/langgraph/concepts/persistence/) for resumable, thread-scoped workflow state.
- [Supabase self-hosting documentation](https://supabase.com/docs/guides/self-hosting) for the hospital-controlled deployment option.

→ For plugin lifecycle rules, see `docs/architecture/PLUGIN_INTERFACE.md`.
→ For environment configuration, see `.env.example`.
→ For storage schema and migration policy, see `docs/database/`.

## Open Questions

- The proposed 10-minute Redis TTL must be validated against the final session UX and hospital policy.
- Exact provider credentials, API limits, GPU capacity, and fallback eligibility remain environment-specific.
- Authentication/authorization mechanics for staff interfaces are pending the integration and security design.
