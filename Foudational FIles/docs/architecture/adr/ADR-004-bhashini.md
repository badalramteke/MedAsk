# ADR-004: Use Bhashini as the Primary Indian-Language Speech Provider

Purpose: Records the speech-provider decision for MediKiosk; read before changing ASR/TTS integration.

## Status

- Accepted
- Date: 2026-08-30

## Context

- The patient interface must support English plus India’s five most-spoken Indian languages: Hindi, Bengali, Marathi, Telugu, and Tamil. This selection follows the latest nationwide language-count source currently available, Census 2011.
- The interface must operate in noisy hospital conditions and provide a touch alternative to speech.
- The stack identifies Bhashini as the primary ASR/TTS provider and AI4Bharat as a local/on-prem fallback.

## Decision

- Use Bhashini as the configured primary Indian-language ASR/TTS provider.
- Provide AI4Bharat as a provider-adapter fallback for approved air-gapped/on-prem deployments.
- Keep speech-provider access behind a provider abstraction and always retain touch input as the patient fallback.

## Consequences

| Positive | Trade-off / risk | Mitigation or follow-up |
| --- | --- | --- |
| Aligns with the Indian-language requirement | Provider coverage/credentials need validation | Confirm models and language support before release |
| Keeps an on-prem fallback path | Fallback quality and operations may differ | Evaluate it under realistic noisy conditions |
| Reduces voice-only accessibility risk | ASR can still fail in noise | Make every question touch-answerable |

## Sources

- [Census of India: scheduled languages by speaker strength, 2011](https://censusindia.gov.in/nada/index.php/catalog/42458/download/46089/C-16_25062018.pdf)

## Open Questions

- Bhashini model identifiers, API credentials, and benchmark acceptance criteria require confirmation.
