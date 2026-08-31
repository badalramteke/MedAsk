# AI Architecture

Purpose: Defines how AI assists MediKiosk without becoming a clinical decision-maker; read before adding an AI workflow, provider, or safeguard.

## Allowed AI responsibilities

| Module | Permitted AI assistance | Required control |
| --- | --- | --- |
| A: History engine | Transcribe, structure patient narration, and propose approved follow-up questions | Deterministic question policy and editable patient data |
| A: Red-flag monitor | Extract possible evidence for configured alert rules | Versioned deterministic rule evaluation and staff review |
| B: Document digitization | Read documents and extract structured entities/timeline candidates | Source provenance, confidence display, and clinician review |
| C: Summary generator | Create a concise, structured draft from validated PatientDataObject data | Draft-only output and clinician edit/accept/amend/reject |
| D: Integration | No clinical inference; may assist technical transformation only through validated mappings | FHIR validation and truthful delivery status |

## Prohibited AI behavior

- Diagnose, rule out disease, prescribe, recommend treatment, or make final triage decisions.
- Claim an external HIS/ABDM delivery succeeded without confirmation.
- Override consent, clinical-policy controls, or authorization.
- Read another patient’s data, expose secrets, or treat untrusted document text as instructions.

## Components

```text
Module/plugin -> ModelService -> capability/provider selection -> model provider
       |              |                    |
       |              |                    `-> MedGemma primary / approved Gemini-Grok fallback
       |              `-> input/output validation, provenance, observability
       `-> PatientDataObject validated patch or safe failure
```

## Primary model roles

- MedGemma 4B: primary multimodal model for document/image understanding.
- MedGemma 27B: primary higher-capacity text model for text-heavy history and summary work where configured hardware supports it.
- Bhashini/AI4Bharat: speech-provider adapters; they are not called directly from business logic.
- Gemini or Grok: approved fallback providers only through ModelService and only when configuration permits.

## Control layers

1. **Policy:** consent, authorization, clinical scope, and plugin capability checks.
2. **Input:** schema validation, trusted/untrusted content separation, size/type limits, and injection screening.
3. **Generation:** constrained task instructions and structured response requirements.
4. **Output:** schema validation, prohibited-content checks, provenance, and safe failure.
5. **Human oversight:** clinician review for summaries and triage-staff control for alerts.

## Sources

- [NIST Generative AI Profile](https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence) for lifecycle risk management.
- [OWASP Prompt Injection Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html) for untrusted-content controls.

→ For provider routing, see `docs/ai/MODEL_ABSTRACTION.md`.
→ For task contracts, see `docs/ai/PROMPT_LIBRARY.md`.

## Open Questions

- Model versions, benchmark thresholds, production GPU capacity, approved fallback credentials, and monitoring thresholds remain environment-specific.
