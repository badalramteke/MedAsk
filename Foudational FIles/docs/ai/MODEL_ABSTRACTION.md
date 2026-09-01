# Model Abstraction

Purpose: Defines the ModelService contract that isolates AI providers from MediKiosk workflows; read before integrating or changing any model provider.

## Non-negotiable rule

- Every model call goes through `ModelService`.
- Route handlers, plugins, clinical logic, and FHIR adapters must not call Ollama, vLLM, Gemini, Grok, Bhashini, or another provider SDK directly.

## Capability-based routing

| Capability | Primary path | Permitted fallback | Environment note |
| --- | --- | --- | --- |
| Clinical summary generation & synthesis (Module C) | MedGemma (27B/4B) ingesting structured history + OCR with source tags | Configured Gemini/Grok provider | Never bypass draft-only controls; must cite source provenance |
| Medical image description (X-rays, sonography, CT) | MedGemma 4B (Multimodal) | Configured Gemini Multimodal provider | Candidate findings with uncertainty flags |
| Physical document text/OCR extraction | Tesseract / PaddleOCR / EasyOCR | Local OCR fallback | Extracts text, lab ranges, handwriting before MedGemma summary |
| Low-network hackathon demo | Local/Colab model serving | Online API only when selected for online demo | Provider selection is configuration only |
| Production serving | Approved local vLLM/on-prem model service | Approved provider route under hospital policy | Hardware and data-governance approval required |

## ModelService responsibilities

- Accept a typed task contract, minimal required input, consent/session context, and requested capability.
- Choose only an enabled provider that satisfies capability, environment, availability, and policy constraints.
- Apply consistent instruction templates, input sanitization, timeouts, structured-output validation, and output safety checks.
- Return typed output plus provider/model version, task version, timestamp, status, and safe error metadata.
- Record audit-safe observability; do not log unnecessary patient content or secrets.

## Fallback rules

- Fallback occurs only for configured availability/compatibility failures, never to evade a safety, consent, or validation failure.
- A fallback output must meet the same schema, scope, and safety constraints as the primary output.
- If no provider produces a valid result, return a safe failure and preserve the workflow for touch input, clinician review, or retry.
- Provider choice and fallback outcome are captured as provenance.

## Split-brain workload separation

- **Live interaction path:** short-turn speech/history work, optimized for responsiveness and confirmation.
- **Heavy processing path:** document understanding and summary generation, optimized for structured validation rather than conversational speed.
- Both paths share ModelService policy and PatientDataObject contracts; neither can bypass the other.

## Provider-adapter contract

| Adapter input | Adapter output |
| --- | --- |
| Capability, structured task, sanitized data, allowed configuration | Typed generated data, provider/model version, usage/status metadata, declared failure |

Adapters do not decide clinical policy, persist patient state, construct FHIR, or return unvalidated free text to a caller.

→ For AI task contracts, see `docs/ai/PROMPT_LIBRARY.md`.
→ For plugin rules, see `docs/architecture/PLUGIN_INTERFACE.md`.

## Open Questions

- Exact endpoint configuration, timeouts, rate limits, serving runtimes, GPU sizing, and fallback ordering require benchmark and deployment approval.
