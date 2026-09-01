# MediKiosk: AI-Powered Digital Clinical Intake Platform

## 1. Background

### 1.1 The Clinical History-Taking Bottleneck in Indian Hospitals
History taking is critical, yielding correct diagnoses in 70-80% of cases even before examination[cite: 1]. However, India's high-patient-density hospitals (4,000–10,000 OPD patients/day) limit consultation times to 2–5 minutes[cite: 1]. This causes systematic under-elicitation of history, missed comorbidities, and diagnostic errors[cite: 1]. Furthermore, AYUSH institutions face added complexity; Ayurvedic history taking involves extensive parameters (Prakriti, Vikriti, Agni, Dashavidha Pariksha, Ahara-Vihara, etc.) that are effectively impossible to capture manually within these time constraints[cite: 1].

### 1.2 The Documentation and Records Fragmentation Problem
Patients typically carry unstructured, physical documents (handwritten prescriptions, lab reports, discharge summaries) from multiple providers[cite: 1]. Physicians lose valuable time manually scanning these chronologically disordered documents[cite: 1]. Despite the Ayushman Bharat Digital Mission (ABDM) establishing infrastructure like ABHA IDs and FHIR standards, there is no 'first-mile' patient-facing software to digitize and structure these documents prior to consultation[cite: 1].

### 1.3 The Opportunity: AI-Powered Digital Clinical Intake Platform
The convergence of mature technologies—robust Indian-language Automatic Speech Recognition (ASR), Large Language Models (LLMs), high-accuracy OCR, and ABDM's FHIR interoperability—now makes it feasible to build a comprehensive, AI-powered clinical history software platform[cite: 1].

---

## 2. Problem Description

### 2.1 The Problem in Precise Terms
There is no purpose-built software platform enabling patients to independently record their medical history via natural voice and touchscreen interaction, while simultaneously digitizing existing physical documents into a structured, physician-ready summary integrated with the hospital information system and ABDM[cite: 1].

### 2.2 Why Existing Solutions Fall Short
* **Hospital Registration Systems:** Only capture demographic and appointment data, completely lacking clinical history elicitation[cite: 1].
* **Mobile Apps / Tele-triage:** Require smartphone literacy and stable connectivity, excluding the elderly, rural, and low-literacy patients who form the bulk of government hospital loads[cite: 1].
* **Manual Triage Desks:** Cannot scale to 5,000+ daily patients and simply reintroduce the transcription bottleneck[cite: 1].
* **Generic Scanners:** Digitize images but fail to extract, structure, or chronologically organize clinical content[cite: 1].

### 2.3 Specific Challenges
* Multilingual and multi-accent voice capture across Hindi, English, and major regional languages in noisy hospital environments[cite: 1].
* Accessibility for low-literacy and elderly users through intuitive icon-driven UIs and audio prompts[cite: 1].
* Accurate clinical history structuring (converting free-form patient narration into standardized physician-readable formats, including AYUSH parameters)[cite: 1].
* Reliable multilingual OCR for handwritten and printed medical documents[cite: 1].
* Strict privacy, consent, and data security compliance (Digital Personal Data Protection Act 2023 and ABDM framework)[cite: 1].

---

## 3. Expected Solution: 'MediKiosk' Platform

### 3.1 Solution Overview
MediKiosk is an AI-powered software platform that allows any patient to record a comprehensive medical history (via voice and touch), scan prior medical documents, and generate a structured, physician-ready summary linked to their ABHA record and pushed to the hospital information system before the consultation begins[cite: 1].

### 3.2 & 3.3 Software & AI Stack (Integrated Modules)

#### Module A - Conversational Multimodal History Engine
* **Adaptive Questioning:** Dynamically branches based on the chief complaint (e.g., SOCRATES framework) to elicit a complete History of Present Illness (HPI) and review of systems[cite: 1].
* **Dual-Mode Input:** Every question is answerable by speaking or tapping, ensuring usability across all literacy levels[cite: 1].
* **AYUSH History Mode:** Captures extended Ayurvedic assessments like Dashavidha Pariksha and Ahara-Vihara[cite: 1].
* **Red-Flag Detection:** AI identifies emergency symptoms (e.g., acute chest pain with dyspnoea) and triggers immediate priority alerts to triage staff rather than routine queueing[cite: 1].

#### Module B - Medical Document Digitization & Intelligence
* **Intelligent Extraction:** High-accuracy, multilingual OCR extracts diagnoses, prescribed medications, dosages, and investigation results[cite: 1].
* **Chronological Organization:** Automatically dates and orders documents into a cohesive medical timeline for the physician[cite: 1].
* **Abnormal-Value Highlighting:** Flags out-of-range lab values and potential drug interactions for physician attention[cite: 1].

#### Module C - Structured History Summary Generator
* **Standard Clinical Format:** Synthesizes data into a standard flow: Chief complaint → HPI → Past medical/surgical → Drug & allergy → Family → Personal → ROS → Prior investigations summary[cite: 1].
* **Editable & Verifiable:** The summary acts as a draft; the physician retains full control to accept, amend, or reject[cite: 1].
* **Bilingual Output:** Patient-facing audio confirmation in the local language; physician-facing structured summary in English/Hindi[cite: 1].

#### Module D - Consent, Privacy & ABDM Integration
* **Consent-First Design:** Granular, revocable consent with audio explanations tailored for low-literacy patients[cite: 1].
* **Secure Processing & Session Termination:** Voice and document AI are processed securely; temporary session data is cleared immediately after submission[cite: 1].
* **ABDM Integration:** Authenticates via ABHA ID and pushes the structured history via FHIR APIs[cite: 1].

---

### 3.4 End-to-End Patient Journey

1. **Step 1 - Identify:** Patient logs into the software platform, authenticates via ABHA ID or [Aadhaar Redacted], selects their preferred language, and grants audio-guided consent[cite: 1].
2. **Step 2 - Converse:** The AI conducts an adaptive voice and touch history interview; severe red flags immediately trigger priority triage[cite: 1].
3. **Step 3 - Scan:** The patient uploads prior prescriptions and lab reports, which the AI digitizes, structures, and timelines[cite: 1].
4. **Step 4 - Summarize & Route:** The AI generates a structured history summary, links it to the ABHA record, and pushes it directly to the physician's screen[cite: 1].
5. **Step 5 - Consult:** The physician reviews the complete history in seconds, edits/confirms the information, and dedicates the full consultation to examination, reasoning, and counseling[cite: 1].

---

## 4. Clinical Datasets & Testing Fixtures

### 4.1 Phase 1 — Clinical JSON Datasets
Located in `data/clinical/`:
* `questions_socrates.json`: Standardized SOCRATES symptom questionnaire framework across 6 Indian languages (en, hi, mr, bn, ta, te).
* `questions_general_intake.json`: General clinical intake framework across 6 Indian languages covering past medical/surgical history, medications, allergies, family, social history, and female-specific menstrual/reproductive history with conditional branching triggers.
* `ayush_dashavidha_pariksha.json`: Ayurvedic 10-parameter Dashavidha Pariksha clinical history framework.
* `red_flags_rules.json`: High-priority emergency red-flag alert rules with multilingual keyword triggers and emergency action codes.
* `lab_reference_ranges.json`: Standardized laboratory test reference ranges with LOINC mapping, adult/pediatric bounds, and critical flags.

### 4.2 Phase 2 — Synthetic Patient Personas
Located in `tests/fixtures/synthetic_patient_personas.json`:
* 10 distinct, multilingual synthetic patient journeys (P01–P10) covering emergency red flags, chronic disease timelines (T2DM/HTN), AYUSH assessments, pediatric edge cases, laboratory out-of-bounds validation, and session lifecycle edge cases.

### 4.3 Phase 3 — FHIR R4 Integration Test Fixtures
Located in `tests/fixtures/mock_fhir_bundles.json`:
* **FHIR Bundles:** 4 FHIR R4 collection bundles (`BUNDLE_001` through `BUNDLE_004`) covering `Patient`, `Encounter`, `Condition`, `Observation`, `MedicationStatement`, `DocumentReference`, and `Consent`.




