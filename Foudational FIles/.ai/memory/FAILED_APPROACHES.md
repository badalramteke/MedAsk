# Failed and Rejected Approaches

## Phase 5: Summary Generator & Model Orchestration
- **Rejected: Monolithic "All History" String for Patient Summary**
  - *Attempted:* Collapsing family, personal, and ROS sections into a single `past_history_summary` string.
  - *Reason for Rejection:* Violates FHIR R4 `Composition.section` mapping criteria in ABDM specifications and prevents clinician section-level review and editing in the frontend UI. Decomposed into 9 distinct typed fields.
- **Rejected: Autonomous Summary Finalization**
  - *Attempted:* Committing the summary directly as a final record when generation finishes.
  - *Reason for Rejection:* AI summaries must never be committed as final medical records without human clinician verification (PRD Section 11.4). Enforced `draft_status: PENDING` and explicit `POST /{session_id}/summary/review` action.
- **Rejected: Permitting Unconstrained Thought Output on Edge/Colab Models**
  - *Attempted:* Allowing the model to output free-form reasoning tokens before markdown blocks.
  - *Reason for Rejection:* Exhausts token limits and creates unpredictable JSON boundaries. Replaced with explicit direct-JSON prompt constraints and regex block isolation.


## Phase 2: Question Engine & Flow Control
- **Rejected: Hardcoded Procedural Question Ordering in Python Code**
  - *Attempted:* Considered defining the question sequence and branching logic as hardcoded Python `if/elif` statements inside the route handler or flow controller.
  - *Reason for Rejection:* Hardcoded logic prevents clinical teams from extending question sets, adding new symptom domains, or modifying translations without changing code. By storing `followup_triggers` (`VALUE_MATCH`, `ALWAYS`) directly inside the clinical JSON datasets, the engine remains data-driven and easily extensible.
- **Rejected: In-App Runtime Switch for AYUSH vs Allopathic Modes**
  - *Attempted:* Initially planned a runtime toggle button for patients to switch between Allopathic and AYUSH mode inside a general hospital kiosk.
  - *Reason for Rejection:* AYUSH hospitals (AIIA, NIS, NIUM, NIH) are separate institutions governed under the Ministry of AYUSH with distinct clinical intake paradigms. A general hospital deployment must run allopathic intake only; AYUSH deployment is a dedicated configuration at setup time.

## Phase 1: Core Data Contract
- **Rejected: Loosely Typed JSON Dicts for Sessions** 
  - *Attempted:* Initially considered keeping the `PatientDataObject` as a generic Python dictionary for flexibility before hitting the database.
  - *Reason for Rejection:* AI modules need strict types to prevent hallucination. A loose dict allows an LLM to accidentally inject non-clinical fields. Enforcing it through strict Pydantic schemas guarantees safety.

## Phase 0: Foundation
- **Rejected: Direct Database Access from Frontend routes**
  - *Reason for Rejection:* Security and HIPAA/DPDP compliance mandates an API middleware layer.
- **Rejected: Multi-Tenant Architecture for MVP**
  - *Reason for Rejection:* Adding hospital tenancy logic before the core intake module is verified adds unnecessary complexity. Reverted to a single-tenant baseline for MVP.
