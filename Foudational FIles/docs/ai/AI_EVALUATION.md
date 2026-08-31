# AI Evaluation

Purpose: Defines how MediKiosk AI is evaluated before release; read before claiming model quality or approving an AI configuration.

## Evaluation principle

- No model, provider, prompt, language, or workflow is “clinically ready” without documented evaluation and clinician approval.
- Use de-identified or synthetic test data unless an approved data-governance process permits otherwise.
- Report failures and uncertainty; do not claim accuracy figures that have not been measured.

## Evaluation areas

| Area | Evidence to evaluate | Required reviewer |
| --- | --- | --- |
| ASR | Transcription and confirmation behavior in configured languages and noisy conditions | Language/accessibility and clinical reviewers |
| History structuring | Faithful mapping of narration to history fields, gaps, and contradictions | Clinician reviewer |
| Question flow | Relevance, completeness, scope adherence, voice/touch parity | Clinician and accessibility reviewers |
| AYUSH capture | Correct field capture without unapproved interpretation | AYUSH clinician |
| Red-flag alerting | Rule-match evidence, false alerts, missed alerts, delivery/acknowledgement behavior | Triage/clinical owner |
| OCR/document extraction | Entity fidelity, source provenance, uncertainty, timeline ordering | Clinician reviewer |
| Summary | Faithfulness, completeness, draft-only language, editable structure | Clinician reviewer |
| Security | Prompt injection, data leakage, provider/fallback consistency | Security reviewer |

## Test design requirements

- Establish a clinician-reviewed reference set for each task and language.
- Separate development, validation, and holdout sets; track dataset provenance and limitations.
- Evaluate primary and fallback providers separately and compare the same acceptance criteria.
- Test adverse cases: ambiguous narration, low-quality scans, conflicting documents, missing data, refusal, ASR uncertainty, and failed integrations.
- Re-run evaluation when a prompt, model, provider, clinical rule, language pack, or extraction schema changes.

## Release evidence

- Test-set version and governance approval.
- Model/provider, prompt, plugin, and rule versions.
- Task-specific results, error analysis, known limitations, and sign-off status.
- Accessibility and clinical-review evidence.
- Red-team result and remediation status.

## Sources

- [NIST AI RMF Generative AI Profile](https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence) for lifecycle evaluation and risk management.
- [NIST AI Resource Center](https://airc.nist.gov/) for testing, evaluation, verification, and validation resources.

→ For adversarial testing, see `docs/ai/RED_TEAM_PLAN.md`.

## Open Questions

- Reference datasets, ground-truth process, evaluation metrics/thresholds, reviewer roster, and release sign-off authority are pending.
