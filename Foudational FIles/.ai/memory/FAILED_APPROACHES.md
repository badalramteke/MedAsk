# Failed and Rejected Approaches

## Phase 1: Core Data Contract
- **Rejected: Loosely Typed JSON Dicts for Sessions** 
  - *Attempted:* Initially considered keeping the `PatientDataObject` as a generic Python dictionary for flexibility before hitting the database.
  - *Reason for Rejection:* AI modules need strict types to prevent hallucination. A loose dict allows an LLM to accidentally inject non-clinical fields. Enforcing it through strict Pydantic schemas guarantees safety.

## Phase 0: Foundation
- **Rejected: Direct Database Access from Frontend routes**
  - *Reason for Rejection:* Security and HIPAA/DPDP compliance mandates an API middleware layer.
- **Rejected: Multi-Tenant Architecture for MVP**
  - *Reason for Rejection:* Adding hospital tenancy logic before the core intake module is verified adds unnecessary complexity. Reverted to a single-tenant baseline for MVP.
