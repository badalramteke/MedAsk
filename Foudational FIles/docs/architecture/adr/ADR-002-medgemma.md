# ADR-002: Use MedGemma as the Primary Clinical AI Model Family

Purpose: Records the primary model selection for MediKiosk; read before changing AI model routing or clinical-model assumptions.

## Status

- Accepted
- Date: 2026-08-30

## Context

- The product needs text-based clinical-history elicitation/summarization and multimodal document understanding.
- The approved stack identifies MedGemma 4B for multimodal work and MedGemma 27B for higher-capacity text work when hardware allows.
- The system must remain provider-neutral and never allow a provider to bypass safety controls.

## Decision

- Use MedGemma 4B as the primary multimodal model for document/image understanding.
- Use MedGemma 27B as the primary higher-capacity text model where the configured hardware supports it.
- Access both exclusively through ModelService.
- Permit configured Gemini or Grok fallback only via ModelService, with the same consent, validation, logging, and no-diagnosis controls.

## Consequences

| Positive | Trade-off / risk | Mitigation or follow-up |
| --- | --- | --- |
| Separates multimodal and text needs | Local hardware may not support every model | Select provider/model by environment configuration |
| Keeps model vendors replaceable | Fallbacks can vary in behavior | Apply shared prompts, validation, and evaluation gates |
| Supports Colab/local and online-demo modes | Final benchmark evidence is pending | Evaluate before production adoption |

## Open Questions

- Exact model weights, serving parameters, benchmark thresholds, and production GPU capacity are not yet approved.
