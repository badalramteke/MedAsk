# Phase 1 Clinical JSON Datasets Documentation

## Overview
The `data/clinical/` directory contains four standardized, machine-readable clinical JSON datasets. These datasets serve as the deterministic ground truth for the MediKiosk clinical intake assessment engine, red-flag alert processor, AYUSH history module, and laboratory value evaluator.

---

## Dataset Inventory

### 1. `questions_socrates.json`
* **Purpose:** Standardized clinical symptom questioning framework based on the **SOCRATES** methodology (*Site, Onset, Character, Radiation, Association, Time Course, Exacerbating/Relieving factors, Severity*).
* **Key Features:**
  - Standardized symptom domains (e.g., `CHEST_PAIN`, `HEADACHE`).
  - Structured `question_id` and `option_id` identifiers for deterministic branching.
  - Full multilingual support across 6 Indian languages: English (`en`), Hindi (`hi`), Marathi (`mr`), Bengali (`bn`), Tamil (`ta`), and Telugu (`te`).
* **Primary Use Case:** Conducts adaptive voice and touch HPI (History of Present Illness) questionnaires during patient intake.

---

### 2. `ayush_dashavidha_pariksha.json`
* **Purpose:** Traditional Ayurvedic 10-parameter examination framework (**Dashavidha Pariksha**) for holistic clinical history taking.
* **Key Parameters (10 Primary Parameters):**
  1. `DUSHYAM` (Structural tissues & humors affected)
  2. `DESHAM` (Habitational and bodily climate/land)
  3. `BALAM` (Physical & mental strength)
  4. `KALAM` (Seasonal & biological time factor)
  5. `ANALA` (Digestive fire / Agni capacity)
  6. `PRAKRITI` (Psycho-somatic constitution: Vata, Pitta, Kapha)
  7. `VAYA` (Age group / life stage)
  8. `SATTVAM` (Mental resilience & temperament)
  9. `SATMYAM` (Habituation & dietary tolerances)
  10. `AHARA` (Dietary habits & Vihara lifestyle factors)
* **Key Features:** Includes supporting parameters (`ROGA_BALA`, `VEGA_DHARANA`) and multilingual options across 6 Indian languages.
* **Primary Use Case:** Enables specialized AYUSH OPD intake assessments integrated alongside standard allopathic clinical history.

---

### 3. `red_flags_rules.json`
* **Purpose:** Deterministic high-priority clinical red-flag alert rules for outpatient and kiosk triage prioritization.
* **Key Categories:**
  - **Cardiovascular Emergencies:** `RF_CARD_001` (Chest pain radiating to arm/jaw), `RF_CARD_002` (Cold sweating & breathlessness).
  - **Neurological Emergencies:** `RF_NEURO_001` (Sudden collapse/syncope), `RF_NEURO_002` (FAST criteria: sudden facial drooping, arm weakness, slurred speech).
  - **Respiratory Emergencies:** `RF_RESP_001` (Severe acute dyspnea), `RF_RESP_002` (Stridor / upper airway obstruction), `RF_RESP_003` (Central cyanosis).
  - **Trauma & Hemorrhage Emergencies:** `RF_TRAUMA_001` (Active major bleeding), `RF_TRAUMA_002` (Major open fracture), `RF_TRAUMA_003` (Severe facial/airway burn).
* **Urgency Levels:** `EMERGENCY_CRITICAL` and `URGENT_PRIORITY`.
* **Primary Use Case:** Real-time keyword and structured fact evaluator that immediately dispatches priority alerts to triage staff to bypass routine queues.

---

### 4. `lab_reference_ranges.json`
* **Purpose:** Standardized laboratory reference ranges and critical value threshold rules for clinical lab report analysis.
* **Included Test Panels:**
  - `FBG` (Fasting Blood Glucose, LOINC: `1558-6`)
  - `PPBG` (Postprandial Blood Glucose, LOINC: `1521-4`)
  - `HBA1C` (Hemoglobin A1c, LOINC: `4548-4`)
  - `SERUM_CREATININE` (Serum Creatinine, LOINC: `2160-0`)
  - `HEMOGLOBIN` (Blood Hemoglobin, LOINC: `718-7`)
  - `ALT_SGPT` (Alanine Aminotransferase, LOINC: `1742-6`)
* **Key Features:**
  - Standardized units (`mg/dL`, `%`, `g/dL`, `U/L`).
  - Age-appropriate adult and pediatric reference bounds (`min_normal`, `max_normal`).
  - Critical thresholds (`critical_low`, `critical_high`) triggering immediate alerts.
* **Primary Use Case:** Out-of-bounds highlighting and critical laboratory value alerts during patient document digitization and record processing.

---

## Integration & Verification Rules
1. **Immutable Ground Truth:** Application code and test fixtures must strictly map to the exact `question_id`, `option_id`, `rule_id`, and `test_code` strings defined in these four JSON files.
2. **Referential Integrity:** Test personas (`tests/fixtures/synthetic_patient_personas.json`) and FHIR R4 bundles (`tests/fixtures/mock_fhir_bundles.json`) are verified against these definitions.
3. **Encoding:** All files are UTF-8 encoded valid JSON documents.
