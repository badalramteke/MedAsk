# Secure Code Standards

Purpose: Defines mandatory coding practices for MediKiosk; read before writing, reviewing, or approving application code.

## Required practices

- One file has one concern; keep API transport, clinical policy, persistence, providers, and FHIR mapping separate.
- Validate external input server-side with typed schemas; never trust browser, OCR, ASR, or model output.
- Keep route handlers thin; no direct database access, clinical logic, or provider SDK calls from routes.
- Use PatientDataObject for module communication and ModelService for all model access.
- Use approved plugins and configuration; do not add feature-specific changes to core modules for future ideas.
- Use parameterized data access, explicit authorization checks, safe errors, and least-privilege service identities.
- Store secrets only in approved environment/secret management; do not commit them, echo them, or log them.
- Add tests for authorization, validation, failure handling, and safety boundaries alongside each change.

## Prohibited practices

- Hardcoded credentials, URLs, encryption keys, patient identifiers, or production configuration.
- Raw SQL concatenation, unsafe deserialization, unbounded upload processing, or silently ignored validation errors.
- Logging of health data, tokens, prompts, raw documents, audio, or secrets unless explicitly approved for a secure diagnostic path.
- Model/provider calls outside ModelService or direct inter-plugin calls.
- Autonomous diagnosis, treatment guidance, prescription generation, or final-record commits by AI.

## Review checklist

- Is the responsibility isolated and the dependency direction correct?
- Are consent and authorization checked before sensitive data use?
- Does the change minimize data handled and logged?
- Are error paths truthful and safe?
- Are new configuration keys documented in `.env.example` without values?
- Does a future plugin remain addable without changing core files?

## Source

- [CERT-In secure application guidelines](https://www.cert-in.org.in/PDF/Application_Security_Guidelines.pdf) emphasize secure design throughout development and operations.

## Open Questions

- Final language-specific linters, dependency scanners, code-review tooling, and branch-protection rules are pending repository setup.
