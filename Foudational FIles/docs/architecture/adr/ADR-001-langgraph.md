# ADR-001: Use LangGraph for Clinical Workflow Orchestration

Purpose: Records why MediKiosk uses LangGraph for stateful, branching intake workflows; read before changing interview orchestration.

## Status

- Accepted
- Date: 2026-08-30

## Context

- Module A requires adaptive, multi-turn questioning that branches on the chief complaint and prior answers.
- The workflow must retain validated session state and safely resume after interruption.
- The architecture requires the canonical PatientDataObject contract and must preserve the editable-draft, no-diagnosis boundary.

## Decision

- Use LangGraph for workflow state, nodes, conditional transitions, and checkpoint-based continuity.
- Use LangChain only as the model-interaction layer; it does not own clinical workflow state.
- Keep model access behind ModelService and plugin boundaries.

## Consequences

| Positive | Trade-off / risk | Mitigation or follow-up |
| --- | --- | --- |
| Supports branching and looped intake flows | Adds an orchestration dependency | Isolate it behind workflow/plugin boundaries |
| Supports checkpoint-based resumption | Checkpoint retention must be controlled | Use short-lived, consent-aware session storage |
| Keeps flow separate from provider SDKs | Requires disciplined state contracts | Validate PatientDataObject updates at each boundary |

## Sources

- [LangGraph Graph API overview](https://langchain-ai.github.io/langgraph/how-tos/state-reducers/)
- [LangGraph persistence concepts](https://langchain-ai.github.io/langgraph/concepts/persistence/)

## Open Questions

- Production checkpointer implementation and final TTL remain to be validated.
