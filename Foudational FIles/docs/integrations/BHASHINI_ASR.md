# Bhashini ASR and Audio Pipeline

Purpose: Defines the provider-agnostic speech integration boundary for MediKiosk; read before implementing ASR, TTS, or streaming audio.

## Scope

- Bhashini is the primary configured ASR/TTS provider.
- Gemini/grok is the configured fallback path for approved .
- The MVP language set is English, Hindi, Bengali, Marathi, Telugu, and Tamil; provider/model support must be verified before release.
- Every spoken interaction has an equivalent touch path.

## Responsibilities

| Component | Responsibility |
| --- | --- |
| Kiosk UI | Capture audio, display transcription/confirmation, offer touch fallback, and avoid durable raw-audio retention |
| Audio preprocessing | Local voice-activity/noise processing where configured; do not make clinical decisions |
| Speech adapter | Convert approved audio/text requests to provider-specific format and return typed result/status |
| History workflow | Confirm or clarify low-confidence transcription and write validated data to PatientDataObject |
| TTS adapter | Render approved prompts/confirmations in the selected language |

## Integration rules

- Provider calls occur through the speech/model-provider abstraction, never directly from routes or clinical workflows.
- Treat transcripts as patient-provided data requiring confirmation, not as verified clinical facts.
- Do not hardcode Bhashini endpoints, credentials, model identifiers, or request formats; obtain them from current approved provider documentation/configuration.
- Any fallback must preserve consent, provenance, data-minimization, validation, and touch-fallback behavior.
- Audio chunks remain volatile processing inputs unless a separate, explicit consent/retention policy is approved.

## Low-network behavior

- Prefer small streamed/chunked audio transfer when the configured provider supports it.
- If ASR is unavailable or poor quality, ask for repeat/confirmation or continue through touch.
- Do not claim an audio response was transcribed successfully when the provider is unavailable or output fails validation.

## Sources

- `docs/architecture/TECH_STACK.md` is the source of the project’s Bhashini/AI4Bharat selection and browser audio-capture approach.
- [ABDM language/accessibility context](https://abdm.gov.in/FAQ) is relevant to consent-enabled patient-facing services; it does not define Bhashini API behavior.

→ For provider routing, see `docs/ai/MODEL_ABSTRACTION.md`.

## Open Questions

- Bhashini account/API documentation, model identifiers, streaming protocol, supported-language verification, TTS voices, quality thresholds, and offline fallback packaging are pending.
