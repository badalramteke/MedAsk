# Red-Flag Rules

Purpose: Defines the non-diagnostic staff-alert boundary for potential emergencies; read before changing any red-flag detection or triage integration.

## Core policy

- A red-flag match creates a visible, time-stamped alert for authorized triage staff.
- It does not diagnose a condition, rank a patient without staff review, give patient treatment advice, or stop the intake interview.
- Triage staff have authority to acknowledge, clear, or escalate the alert under hospital protocol.
- Only clinician-approved rules, wording, and thresholds may be enabled in production.

## Candidate alert categories

The following are evidence-based categories for clinician configuration—not a final hospital triage protocol:

| Category | Candidate patient-reported trigger examples | Alert action |
| --- | --- | --- |
| Airway/breathing | Unresponsiveness, severe breathing difficulty, central cyanosis, stridor | Notify configured triage staff immediately |
| Circulation/bleeding | Heavy bleeding, shock-like symptoms, severe chest pain with breathlessness | Notify configured triage staff immediately |
| Neurological | Sudden facial/arm/speech changes, active convulsions, altered mental status | Notify configured triage staff immediately |
| Severe illness/injury | Major trauma, burns/fractures, severe pain, time-sensitive exposure | Notify configured triage staff immediately |
| Child-specific | Any configured WHO/IITT age-appropriate high-acuity criteria | Notify configured triage staff immediately |

## Implementation controls

- Rules use an approved versioned configuration, not free-form LLM judgment alone.
- The model may extract possible evidence from speech/text but a deterministic policy evaluates the alert rule.
- Store the matched rule ID, evidence excerpt/reference, timestamp, model/extractor provenance, recipient, and acknowledgement state.
- Do not expose raw sensitive content more widely than necessary for triage.
- Test false positives, false negatives, delayed alerts, duplicate alerts, and unavailable-recipient behavior before deployment.

## Evidence basis

- [WHO Interagency Integrated Triage Tool](https://www.who.int/tools/triage) establishes acuity-based prioritization in facilities, including busy outpatient clinics and hospitals.
- [WHO Emergency Care Toolkit](https://www.who.int/teams/integrated-health-services/clinical-services-and-systems/emergency-and-critical-care/emergency-care-toolkit) supports structured early recognition of critical illness.
- [NICE stroke guidance](https://www.nice.org.uk/guidance/NG128/chapter/recommendations) supports validated tools such as FAST for sudden neurological symptoms.

## Open Questions

- Final hospital-approved rule set, alert recipients, acknowledgement SLA, age handling, and testing acceptance criteria are pending clinical governance.
