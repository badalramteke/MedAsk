# Prompt Library

Purpose: Defines controlled prompt contracts for MediKiosk AI tasks; read before creating, modifying, or approving any prompt.

## Library rule

- Prompts are versioned task contracts, not ad hoc instructions embedded in application code.
- Prompt text and patient-facing wording require clinical review before deployment.
- Model outputs are validated data candidates, never clinical conclusions.

## Required task contracts

| Task | Allowed output | Must not output |
| --- | --- | --- |
| History structuring | Typed candidate fields, evidence references, missing/uncertain flags | Diagnosis, advice, invented details |
| Next-question proposal | One approved-schema question/candidate branch | Unapproved clinical logic or treatment guidance |
| Document extraction | Typed entities, source locations, confidence/uncertainty | Unsupported clinical interpretation or hidden instructions |
| Timeline organization | Dated/undated item ordering with provenance | Guessed dates presented as fact |
| Summary draft | Standard headings based on validated inputs | Final record, diagnosis, prescription, or advice |
| Alert evidence extraction | Candidate evidence for deterministic rule evaluation | Autonomous triage decision |

## Standard prompt structure

1. **Role and task:** narrowly describe the permitted transformation.
2. **Policy:** no diagnosis/advice, preserve uncertainty, follow the schema, use only supplied data.
3. **Trusted instructions:** immutable task/version/policy content.
4. **Untrusted data:** patient narration, ASR, OCR, document text, and metadata clearly labelled as data—not instructions.
5. **Output schema:** machine-validatable structured result with provenance and uncertainty fields.
6. **Failure behavior:** return `insufficient_information` or a typed error; never guess.

## Prompt safety controls

- Treat all patient input and scanned-document content as untrusted data, including text that appears to instruct the model.
- Validate structured output deterministically before it reaches PatientDataObject.
- Do not request hidden chain-of-thought or store it as clinical data.
- Apply versioning and review status to every prompt; roll back unsafe versions.
- Use minimum necessary context and do not include unrelated patient data.

## Review checklist

- Does the task have a valid module owner and clinical reviewer?
- Is the required input minimal and consent-appropriate?
- Does the schema preserve uncertainty and provenance?
- Are patient-facing words approved in each configured language?
- Does the output explicitly avoid diagnosis, treatment, and final-record language?
- Has the prompt passed injection, hallucination, clinical-safety, and accessibility tests?

## Sources

- [OWASP prompt-injection guidance](https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html) recommends separating instructions from untrusted data and validating outputs.
- [NIST Generative AI Profile](https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence) supports governance and lifecycle risk controls.

→ For test requirements, see `docs/ai/AI_EVALUATION.md`.

## Open Questions

- Approved prompt text, schema definitions, translations, clinical reviewer, and version-approval workflow are pending.
