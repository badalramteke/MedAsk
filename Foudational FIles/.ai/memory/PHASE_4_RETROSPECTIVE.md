# Phase 4 Retrospective: LangGraph Clinical Workflow & Safety Rules

## Overview
- **Completed On**: 2026-09-05
- **Goal**: Migrate the procedural `FlowController` into a `StateGraph` powered by LangGraph, while strictly adhering to clinical protocols and non-blocking safety rules.
- **Status**: Completed successfully.

## What Went Well
- **LangGraph Integration**: The `StateGraph` elegantly encapsulated the clinical workflow. By building a strict `ClinicalInterviewState` using Python `TypedDict`, data contracts were strictly enforced throughout the graph nodes.
- **Non-blocking Red Flag Wrapper**: Implementing a Python decorator (`wrap_with_red_flag`) that intercepted the state updates of any node and ran the `RedFlagScanner` cleanly met the `CLINICAL_SAFETY.md` requirements. It decoupled safety scanning from core clinical node logic.
- **AYUSH and General Splitting**: The LangGraph conditional routing made branching between Allopathic (SOCRATES) and AYUSH workflows significantly more robust than the previous procedural approach.

## Challenges Encountered
- **Cyclic Execution and `END` Routes**: A major challenge was debugging LangGraph's cyclic execution model when paired with a stateless REST API boundary. If a node returns `END`, LangGraph considers the graph execution complete. When `update_state` is later called (when the user provides an answer), LangGraph must figure out where to resume. We learned that `update_state` triggers the evaluation of conditional edges of the *last* executed node. Because of this, any dynamic routing logic that depends on the user's answer (like mapping the chief complaint text to a SOCRATES domain) must be handled *before* injecting the state, so the router has the necessary context to determine the next node.

## Key Decisions
- **Moving Domain Logic to `process_step` API Boundary**: Instead of forcing the `chief_complaint_node` to re-execute, we moved the chief complaint domain mapping directly into the `process_step` method of the `ClinicalWorkflowManager`. This allowed the LangGraph router to smoothly transition to `SOCRATES_DEEP_DIVE` based on the updated state.
- **Removing Phase 2 `FlowController` Logic**: We completely migrated the `/api/v1/sessions` endpoints to `ClinicalWorkflowManager`.

## Next Steps
- Kick off Phase 5: Summary Generator (Module C).
- We have validated the stateful backend execution perfectly in tests; next, we need to generate the physician-editable clinical draft from this structured graph state.
