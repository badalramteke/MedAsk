# AI Red-Team Plan

Purpose: Defines adversarial testing for MediKiosk AI safety, privacy, and reliability; read before release and after any material AI change.

## Goal

- Find ways the AI system could produce unsafe clinical content, lose patient data, follow malicious document text, or misrepresent an integration outcome.
- Test controls without using real patient data unless formally approved.

## Test areas

| Area | Test objective | Expected safe outcome |
| --- | --- | --- |
| Prompt injection | Patient text, OCR text, document metadata, or image content attempts to alter model instructions | Treat content as data; preserve task boundaries |
| Clinical overreach | Requests or narratives invite diagnosis, prescriptions, treatment advice, or false reassurance | Refuse/restrict to intake and clinician-review draft |
| Hallucination | Inputs are incomplete, contradictory, or ambiguous | Preserve uncertainty; do not invent facts |
| Alert failure | Alert-like content is phrased indirectly, duplicated, delayed, or recipient unavailable | Generate traceable candidate/alert behavior under configured rules; surface failure truthfully |
| Data isolation | Attempt cross-session/patient data exposure | Deny access and emit security-safe event |
| Fallback parity | Primary failure causes Gemini/Grok fallback | Same schema, consent, safety, and provenance controls apply |
| Document security | Uploaded record includes hidden/malicious instructions or unsafe markup | Ignore instructions; extract only allowed data |
| Output safety | Model returns diagnosis/advice, system prompt, secret-like data, or invalid schema | Reject/quarantine output and return safe failure |

## Method

1. Define test case, target control, risk owner, and expected result.
2. Run against each enabled model/provider and language path.
3. Record versioned evidence without retaining unnecessary sensitive content.
4. Classify result: pass, finding, blocked, or inconclusive.
5. Remediate, retest, and require approval before release.

## Release blockers

- Any reproducible patient-data disclosure, secrets exposure, autonomous diagnosis/treatment output, or untruthful delivery status blocks release.
- Unresolved red-flag alert loss/delay or clinician-approved safety-test failure blocks release.
- A safety filter failure must not be bypassed by provider fallback.

## Sources

- [OWASP LLM Prompt Injection Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html).
- [OWASP LLM01: Prompt Injection](https://genai.owasp.org/llmrisk/llm01-prompt-injection/).
- [NIST AI RMF Generative AI Profile](https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence).

→ For clinical limits, see `docs/clinical/CLINICAL_SAFETY.md`.

## Open Questions

- Named red-team owner, attack-case library, severity scale, remediation SLA, and final release authority are pending.
