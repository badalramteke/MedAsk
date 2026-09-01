# MediKiosk — Product Requirements Document

---

| Field | Detail |
| --- | --- |
| Project Name | MediKiosk — AI Clinical History Platform |
| PS Number | SIH26047 |
| Organization | Ministry of Ayush |
| Department | All India Institute of Ayurveda (AIIA) |
| Category | Software |
| Theme | Smart Automation |
| Version | 1.0 |
| Status | Draft |
| Last Updated | [Not Started] |
| Authors | Badal, Bhushan , Om, Vansh , Pratiksha , Janhavi |
| Reviewers | Claude, Gemini, OpenAI models |

## Document Map

| Section | Summary | Detail File |
| --- | --- | --- |
| Problem Statement | Why this exists | → docs/product/SCOPE.md |
| User Personas | Who uses this | → docs/product/USER_PERSONAS.md |
| Functional Requirements | What it does | → docs/clinical/QUESTION_ENGINE_SPEC.md |
| Architecture | How it's built | → docs/architecture/SYSTEM_ARCHITECTURE.md |
| AI Requirements | Model behaviour | → docs/ai/AI_ARCHITECTURE.md |
| Clinical Requirements | Medical rules | → docs/clinical/CLINICAL_PROTOCOLS.md |
| Data Requirements | Data contract | → docs/database/PATIENT_DATA_OBJECT.md |
| Integrations | External systems | → docs/integrations/ |
| Privacy & Compliance | Legal requirements | → docs/privacy/DPDP_COMPLIANCE.md |
| Security | Threat model | → docs/security/SECURITY_MODEL.md |
| Operations | Phases + deployment | → docs/operations/PHASES.md |

## 2. Executive Summary

### What, Why, Who

#### 1. WHAT is it?

MediKiosk is an AI-powered, patient-facing digital clinical intake software platform that structures medical history and digitizes prior documents before a patient's consultation begins.

**Core Modules:**

- **Conversational History Engine:** Conducts adaptive clinical interviews via voice and touch. It leverages regional Automatic Speech Recognition (ASR) engines (e.g., Bhashini, AI4Bharat, or similar models) and a clinical dialogue manager paired with text-to-speech prompts.
    - Probes symptoms intelligently (e.g., utilizing clinical mnemonics like the SOCRATES framework).
    - Features a dedicated AYUSH mode capturing deep Ayurvedic parameters (including Trividha, Ashtavidha, Dashavidha Pariksha, Prakriti, Vikriti, Agni, Koshtha, Ahara-Vihara, Nidana, Samprapti, Sara, Samhanana, Pramana, Satmya, Sattva, Ahara Shakti, Vyayama Shakti, and Vaya).
    - Automatically detects red-flag emergency symptoms for immediate priority triage.
- **Document Digitization:** Uses high-accuracy, multilingual OCR to extract diagnoses, medications (with dosages), and lab results (with exact values and reference ranges) from printed or handwritten records. It organizes these chronologically into a timeline and highlights out-of-range abnormal values for the physician.
- **Summary Generator:** Synthesizes the conversational history and digitized documents into a single, standardized, and editable format (Chief complaint, HPI, Past history, Drug/allergy, Family, Personal, Menstrual cycle, ROS, Investigations). Generates bilingual output: patient-facing local language audio and a physician-facing English/Hindi text summary.
- **Consent & Integration:** Ensures strict DPDP Act 2023 compliance with granular, audio-guided consent and immediate session termination. Authenticates patients (via ABHA or [Aadhaar Redacted]) and securely pushes data to the Hospital Information System (HIS) via FHIR APIs.

**End-to-End Patient Journey:**

1. **Identify:** Authenticate, select preferred language, and grant consent.
2. **Converse:** AI captures the full history and routes severe cases directly to triage.
3. **Scan:** Patient uploads physical documents for structuring and timelining.
4. **Summarize:** AI pushes a structured clinical summary to the HIS and ABHA network.
5. **Consult:** The physician reviews the compiled history in seconds, dedicating the visit to examination and counseling.

---

#### 2. WHY is it needed?

- **The Time Bottleneck:** While a well-conducted history yields a correct diagnosis in 70-80% of cases, Indian public OPDs handle 4,000–10,000 patients daily. This results in 2-5 minute consultation windows—among the shortest globally, according to a 2017 study published in *BMJ Open*.
- **Failed Alternatives:** Standard hospital systems only capture demographic data; mobile apps demand high smartphone literacy and connectivity; manual triage desks cannot scale; and generic document scanners fail to extract or organize structured clinical content.
- **Record Fragmentation:** Patients arrive with disorganized, multilingual paper records from multiple providers, consuming massive amounts of the doctor's time (the "first-mile problem").
- **AYUSH Constraints:** Ayurvedic practitioners require extensive diagnostic assessments that are effectively impossible to document manually within current OPD time constraints, forcing practitioners to compromise on personalized care.
- **Environmental Realities:** The software platform must function flawlessly in noisy hospital environments (requiring robust multi-accent capture) and be fully usable by first-time, low-literacy patients with zero training.

---

#### 3. WHO is it for?

- **Patients:** Specifically designed for elderly, rural, and low-literacy populations who benefit from zero-training, icon-driven UIs, and conversational audio guidance.
- **Allopathic & AYUSH Physicians:** Doctors who urgently need instant, structured patient data to eliminate transcription time, avoid missed comorbidities, and reduce diagnostic errors.
- **Triage Staff & Nurses:** Healthcare workers who rely on the platform's automated emergency symptom alerts to prioritize critical cases over the routine queue.
- **Hospitals & National IT Infrastructure:** Facilities seeking seamless integration with the national Ayushman Bharat Digital Mission (ABDM) health exchange and existing HIS platforms.

**Problem**
Doctors only get 2 to 5 minutes per patient, leading to rushed medical histories and disorganized paper records ⏳.

**Solution**
An AI-powered software platform that lets patients record their full history and scan documents before entering the consultation room 🤖.

**Expected Impact in Numbers**

- **70-80%:** The percentage of cases where a well-conducted history alone yields the correct diagnosis 🎯.
- **4,000 to 10,000:** The daily volume of outpatients at major hospitals whose intake process can be automated 🏥.
- **2 to 5 minutes:** The tiny consultation window that will now be saved for actual medical treatment instead of data entry ⏱️.

→ Full problem detail: docs/product/SCOPE.md
→ Full KPIs: docs/operations/PHASES.md

## 3. Problem Statement

#### 3.1 Clinical History Bottleneck

- A well-conducted history yields the correct diagnosis in 70-80% of cases even before examination or investigation .
- India operates a highly patient-dense healthcare system, with tertiary government hospitals registering 4,000–10,000 outpatient department (OPD) patients per day .
- Doctor-to-patient consultation time is frequently reported between 2 and 5 minutes .
- A 2017 study published in BMJ Open across 67 countries placed India's average primary-care consultation at just over 2 minutes .
- Physicians must simultaneously elicit history, examine, review records, diagnose, counsel, and prescribe within this brief window .
- This constraint causes systematic under-elicitation of history, missed comorbidities, repeated questioning, and diagnostic errors .

#### 3.2 AYUSH Complexity Layer

- Ayurvedic history taking requires detailed assessments like Trividha, Ashtavidha, and Dashavidha Pariksha .
- Practitioners must evaluate Prakriti (constitution), Vikriti (current imbalance), Agni (digestive capacity), Koshtha (bowel nature), Ahara-Vihara (diet and lifestyle), Nidana (causative factors), and Samprapti (pathogenesis) .
- Capturing this extensive framework manually within OPD time constraints is effectively impossible .
- This forces practitioners to abbreviate the assessments that define personalized Ayurvedic care .

#### 3.3 Documentation Fragmentation

- Patients typically carry physical paper prescriptions, laboratory reports, discharge summaries, and imaging films from multiple prior providers .
- Physicians consume a significant fraction of consultation time manually scanning unstructured, handwritten, multilingual, and chronologically disordered documents .
- There is no point-of-entry mechanism to digitize, structure, and chronologically organize prior medical documents before the consultation room .
- Despite the Ayushman Bharat Digital Mission (ABDM) establishing ABHA IDs and FHIR standards, there is no patient-facing software platform to capture structured history into the ecosystem before the clinical encounter .

#### 3.4 Why Existing Solutions Fail

- Existing hospital registration systems capture only demographic and appointment data, failing to elicit clinical history or process medical documents .
- Mobile health apps and tele-triage chatbots require smartphone literacy and stable connectivity, excluding the large elderly, rural, and low-literacy patient populations .
- Manual nurse-led triage desks are human-resource-limited, cannot scale to 5,000+ daily patients, and reintroduce the same time and transcription bottlenecks .
- Generic document scanners digitize images but do not extract, structure, chronologically organize clinical content, or link it to a structured history or ABHA record .

#### 3.5 Specific Challenges to Overcome

- Capturing multilingual, multi-accent voice in noisy hospital environments across Hindi, English, and major regional languages for patients of varying literacy .
- Ensuring accessibility for low-literacy and elderly users through intuitive icon-driven UIs, audio prompts, and conversational guidance with zero training .
- Accurately converting free-form patient narration into standardized, physician-readable history and Dashavidha Pariksha parameters for AYUSH settings .
- Providing reliable OCR digitization of handwritten and printed medical documents in multiple languages, with intelligent extraction of diagnoses, medications, and investigation values .
- Ensuring privacy, consent, and data security compliance with the Digital Personal Data Protection Act 2023 and ABDM consent framework .

→ Full challenge detail: docs/product/SCOPE.md
→ Accessibility rules: docs/product/USER_PERSONAS.md
→ Privacy architecture: docs/privacy/DPDP_COMPLIANCE.md

## 4. Goals & Success Metrics

#### 4.1 Primary Goals

- Offload structured data-entry tasks from human staff to the patient to dramatically improve throughput and accuracy without requiring prior digital literacy .
- Generate a structured, physician-ready clinical history summary that integrates with the Hospital Information System (HIS) and the ABDM ecosystem before the patient enters the consultation room .
- Solve the "first-mile" digitization problem by capturing, structuring, and chronologically organizing a patient's prior medical documents at the point of entry .
- Enable AYUSH practitioners to comprehensively capture extensive Ayurvedic assessments (such as Dashavidha Pariksha) that are otherwise impossible to record manually within current time constraints .up

#### 4.2 Quantitative KPIs

- **Diagnostic Accuracy Baseline:** Achieve the classical medical benchmark where the well-conducted, structured history yields the correct diagnosis in 70-80% of cases prior to physical examination .
- **System Scalability:** Successfully process and handle the daily volume of 4,000 to 10,000 OPD patients without relying on human-resource-limited manual triage desks .
- **Consultation Time Reclaimed:** Shift the burden of history-taking and document-scanning outside the brief 2 to 5 minute consultation window, allowing doctors to dedicate 100% of that time to examination, clinical reasoning, and counseling .

#### 4.3 Qualitative KPIs

- **Zero-Training Accessibility:** The platform must prove fully usable by first-time, non-tech-savvy, low-literacy, and elderly patients through intuitive icon-driven UIs and audio prompts .
- **Clinical Data Completeness:** The system must accurately structure free-form patient narration into standardized formats (Chief complaint, HPI, past history, drug/allergy, family, personal, review of systems) and capture complex AYUSH parameters (Prakriti, Vikriti, Agni, Koshtha, etc.) .
- **Document Intelligence Precision:** Multilingual OCR must reliably extract exact clinical entities—including diagnoses, prescribed medications with dosages, and investigation results with reference ranges and abnormal-value highlighting .
- **Strict Security & Compliance:** Must demonstrate full compliance with the Digital Personal Data Protection Act 2023 and the ABDM consent framework, featuring granular audio-guided consent and immediate temporary session termination after data submission .

→ docs/operations/PHASES.md        ← milestones + deliverables
→ docs/operations/MVP_BACKLOG.md   ← hackathon KPIs
→ docs/operations/TESTING_STRATEGY.md  ← validation metrics
→ docs/product/SCOPE.md            ← success boundaries

## 5. User Personas

#### 5.1 The Patient (Primary User)

- **Who uses the system:** Elderly, rural, low-literacy, and first-visit patient populations who form the bulk of government hospital OPD loads .
- **Their pain points:** Managing unstructured, multilingual, and chronologically disordered physical paper records from multiple prior providers, and enduring repeated questioning across visits , about medical history, .
- **Their technical comfort level:** Non-tech-savvy with low smartphone literacy and limited connectivity; strictly requires a zero-training environment via intuitive icon-driven UIs and conversational audio guidance .

#### 5.2 The Allopathic Physician

- **Who uses the system:** Doctors operating in overburdened tertiary government hospitals and apex institutions handling up to 10,000 patients daily .
- **Their pain points:** Trapped in 2-5 minute consultation windows where manually scanning fragmented paper records leads to systematic under-elicitation of history, missed comorbidities, and diagnostic errors .
- **Their technical comfort level:** High (Professional); requires physician-ready, standardized clinical summaries (e.g., HPI, ROS) that are fully editable and verifiable on their consultation screen .

#### 5.3 The AYUSH Practitioner

- **Who uses the system:** Doctors practicing traditional Indian medicine in AYUSH institutions .
- **Their pain points:** Forced to severely abbreviate the extensive diagnostic frameworks that define personalized Ayurvedic care because capturing them manually is impossible within OPD time constraints .
- **Their technical comfort level:** High (Professional); requires specialized software modes to digitally capture deep Ayurvedic parameters (such as Trividha, Ashtavidha, Dashavidha Pariksha, Prakriti, and Vikriti) .

#### 5.4 Hospital Triage & Nursing Staff

- **Who uses the system:** Human-resource-limited manual triage and history desks .
- **Their pain points:** The physical inability to scale manual history-taking to 5,000+ daily patients without reintroducing massive transcription bottlenecks .
- **Their technical comfort level:** Moderate to High (Professional); relies on the platform's AI red-flag detection to receive immediate priority alerts for emergency symptoms, bypassing the routine queue .

→ docs/product/USER_PERSONAS.md

## 6. User Stories

#### 6.1 The Patient

- **As a** first-time patient with low digital literacy, **I want** to record my medical history using natural voice conversation and simple touchscreen icons, **so that** I can provide a comprehensive account of my symptoms without needing any technical training or smartphone apps.
- **As a** patient carrying fragmented paper records from multiple providers, **I want** to scan my physical prescriptions and lab reports at the kiosk, **so that** my doctor has a chronologically organized medical timeline and I don't have to face repeated questioning.

#### 6.2 The Allopathic Physician

- **As an** allopathic physician in an overburdened OPD, **I want** a structured, physician-ready clinical summary (including HPI and ROS) presented on my screen before the patient enters, **so that** I can dedicate my brief 2-5 minute consultation window entirely to examination and treatment rather than data entry.

#### 6.3 The AYUSH Practitioner

- **As an** AYUSH practitioner, **I want** the software platform to automatically capture deep Ayurvedic assessments (like Dashavidha Pariksha, Prakriti, and Vikriti) from the patient beforehand, **so that** I can deliver fully personalized traditional care without being forced to abbreviate crucial diagnostic steps due to severe time constraints.

#### 6.4 Hospital Triage & Nursing Staff

- **As a** triage nurse, **I want** the AI to automatically detect and flag emergency symptoms (such as acute chest pain with dyspnoea), **so that** I can immediately pull critical patients out of the routine queue and provide urgent priority care.

## 7. Scope

#### 7.1 In Scope — What We Build (SIH MVP)

- **Multimodal Intake Interface:** A patient-facing software platform driven by an intuitive icon-driven GUI and conversational audio (Voice + Touch).
- **AI History Engine:** An adaptive dialogue manager covering Allopathic frameworks (SOCRATES, HPI, ROS) and specialized AYUSH parameters (Dashavidha Pariksha, Ahara-Vihara).
- **Medical Document AI:** A multilingual OCR pipeline capable of scanning, extracting, and chronologically timelining physical prescriptions, lab reports, and discharge summaries.
- **Red-Flag Triage System:** Automated detection of emergency symptoms to trigger immediate alerts to nursing staff.
- **Structured Summary Generator:** An AI summarization module that outputs a physician-ready, editable clinical draft (English/Hindi) and a patient-facing audio confirmation.
- **ABDM & Privacy Layer:** ABHA ID authentication, FHIR API payload generation for HIS integration, and DPDP Act 2023 compliant consent frameworks (including automated session termination).
- **Voice UI Navigation (Accessibility Engine):** Patient navigation across permitted kiosk pages and controls via natural voice commands mapped to allow-listed element action identifiers (`data-voice-action`), preserving touch as a continuous fallback.

#### 7.2 Out of Scope — What We Explicitly *Don't* Build

- **Autonomous AI Diagnosis:** The system generates a structured clinical *history*, not a diagnosis. It is strictly a draft for the physician to accept, amend, or reject. It does not prescribe medication or offer medical advice.
- **Physical Kiosk Hardware:** We are building the *software platform* that powers the intake kiosks, not manufacturing the physical kiosk terminals, screens, or scanner hardware.
- **Full-Scale HIS/EMR Replacement:** The solution acts as a "first-mile" integration layer. It is not intended to replace a hospital's entire backend management system; it pushes data *into* existing systems.

#### 7.3 Future Scope — What Comes After SIH

- **IoT Hardware Integration:** Interfacing the software kiosk with physical diagnostic sensors (e.g., automated BP cuffs, pulse oximeters, and weighing scales) to capture live vital signs alongside the clinical history.
- **Deep ABDM Sandbox Certification:** Transitioning from FHIR API demonstrations to official certification and deployment on the national Ayushman Bharat Health Information Exchange.
- **Predictive Population Health Analytics:** Aggregating anonymized, geography-based symptom data to help government health ministries track infectious disease outbreaks (e.g., a sudden spike in fever/cough clusters in a specific district).
- **Expanded Vernacular Support:** Scaling the Automatic Speech Recognition (ASR) and OCR capabilities from major regional languages to deeper rural dialects to maximize accessibility.

→ docs/product/SCOPE.md

## 8. Functional Requirements

#### 8.1 Module A — Conversational Multimodal History Engine

- **Dual-Mode Interaction:** The system must capture structured clinical history by allowing patients to speak naturally in their preferred language or tap touchscreen options, making every question answerable via both modes .
- **Adaptive Questioning:** The dialogue manager must dynamically branch follow-up questions based on the chief complaint and prior answers, utilizing clinical frameworks like SOCRATES (e.g., probing onset, character, radiation, and aggravating factors for chest pain) .
- **AYUSH History Mode:** The module must include an extended interview setting for Ayurvedic OPDs to capture Dashavidha Pariksha parameters (Prakriti, Vikriti, Sara, Samhanana, Pramana, Satmya, Sattva, Ahara Shakti, Vyayama Shakti, Vaya) and Ahara-Vihara assessments .
- **Red-Flag Detection:** The AI must detect emergency symptoms (such as acute chest pain with dyspnoea or stroke symptoms) in real-time and trigger an immediate priority alert to triage staff instead of placing the patient in the routine queue .
- **Audio Guidance:** The interface must feature text-to-speech audio prompts to guide low-literacy and elderly patients through the interview .

#### 8.2 Module B — Medical Document Digitization & Intelligence

- **Multilingual OCR:** The system must perform high-accuracy Optical Character Recognition on uploaded or scanned printed and handwritten medical documents in multiple languages .
- **Intelligent Entity Extraction:** It must automatically extract clinical entities including diagnoses, prescribed medications with specific dosages, procedure/surgery history, and investigation results with their corresponding values and reference ranges .
- **Chronological Timelining:** The module must automatically date and organize fragmented prescriptions, lab reports, and discharge summaries into a coherent, ordered medical timeline for the physician .
- **Abnormal-Value Highlighting:** The system must flag out-of-range laboratory values and highlight potential drug interactions for the physician's immediate attention .

#### 8.3 Module C — Structured History Summary Generator

- **Standardized Formatting:** The engine must synthesize both the conversational history and digitized documents into a single, concise summary following a standard clinical format: Chief complaint, HPI, Past medical/surgical, Drug & allergy, Family, Personal, Menstrual cycle history, Review of systems (ROS), and Prior investigations summary .
- **Editable Draft Generation:** The generated summary must function strictly as a draft presented on the consultation screen; the physician must retain full control to edit, accept, amend, or reject the data before saving .
- **Bilingual Output:** The module must generate a patient-facing audio confirmation of the captured history in their local language, while simultaneously generating the physician-facing written summary in English or Hindi .

#### 8.4 Module D — Consent, Privacy & ABDM Integration

- **Granular Consent:** The platform must provide a consent-first design featuring granular, revocable consent with audio explanations tailored for low-literacy patients, strictly complying with the Digital Personal Data Protection Act 2023 .
- **Patient Authentication:** The system must authenticate users via their ABHA ID or [Aadhaar Redacted] details, or allow new user registration .
- **FHIR Interoperability:** It must link the structured history to the patient's ABHA Personal Health Record and push the data directly to the hospital's Information System (HIS/EMR) via FHIR APIs .
- **Secure Processing & Session Termination:** All voice and document AI processing must occur securely within the software platform, and all temporary session data must be immediately cleared/terminated after submission .

#### 8.5 Innovation Modules (Key Differentiators)

- **Zero-Training Multimodal UI:** Offloading complex clinical data entry directly to non-tech-savvy users (the "first-mile" problem) by combining icon-driven touch interfaces with Indian-language speech recognition, requiring absolutely no digital literacy .
- **Automated Triage Bypassing:** Utilizing the conversational AI not just for data entry, but as a live emergency filter that proactively pulls critical patients out of wait-lines based on spoken red-flag symptoms .
- **Digital AYUSH Translation:** Digitizing extremely complex, previously manual Ayurvedic diagnostic frameworks (like Trividha and Dashavidha Pariksha) into an automated patient-facing flow, solving the unique OPD time constraints of traditional Indian medicine .

#### 8.6 Module E — Voice UI Navigation & Accessibility Plugin

- **Hands-Free Navigation:** Enables patients to navigate permitted kiosk views and trigger allowed actions via natural voice phrases (e.g., "start intake", "scan document", "change language to Hindi", "back", "next", "confirm consent").
- **Semantic Allow-List Matching:** Spoken navigation commands map exclusively to allow-listed `data-voice-action` and `data-element` identifiers on approved UI controls. Arbitrary script execution, unrestricted DOM manipulation, or raw text evaluation is strictly prohibited.
- **Continuous Touch Parity:** Every voice-navigable action must correspond 1-to-1 with a visible, tappable UI element with clear visual focus/feedback, maintaining seamless touch fallback.

→ docs/clinical/QUESTION_ENGINE_SPEC.md
→ docs/architecture/PLUGIN_INTERFACE.md
→ docs/product/MODULES.md

## 9. Non-Functional Requirements

#### 9.1 Performance

- **Speed:** The platform must synthesize conversational history and digitized documents into a complete, structured summary in seconds .
- **Time Efficiency:** It must ensure the summary is presented on the consultation screen the moment the patient enters the room, safeguarding the critical 2–5 minute physician consultation window .

#### 9.2 Scalability

- **High-Throughput Capacity:** The system must effortlessly scale to manage the massive loads of tertiary government hospitals and apex institutions, which routinely register 4,000 to 10,000 OPD patients per day .
- **Automation Over Human Limits:** It must eliminate the bottleneck of manual nurse-led triage desks, which physically cannot scale to process 5,000+ daily patients .

#### 9.3 Reliability

- **Environmental Robustness:** The automatic speech recognition (ASR) engine must reliably capture input in highly noisy hospital environments .
- **OCR Precision:** The document digitization pipeline must maintain high-accuracy extraction for both printed and handwritten, unstructured, and chronologically disordered medical documents .

#### 9.4 Security

- **Regulatory Compliance:** The platform must guarantee strict adherence to the Digital Personal Data Protection (DPDP) Act 2023 and the ABDM consent framework .
- **Data Handling:** Voice and document AI must be processed securely strictly within the software platform .
- **Session Management:** All temporary session data must be cleared and terminated immediately after submission .

#### 9.5 Accessibility

- **Zero-Training Usability:** The software must be fully accessible to first-time, non-tech-savvy, elderly, and low-literacy users requiring absolutely zero training .
- **Inclusive UI/UX:** It must utilize an intuitive icon-driven UI, dual-mode inputs (speaking OR tapping), conversational guidance, and audio prompts .
- **Linguistic Versatility:** It must support multilingual and multi-accent voice capture across Hindi, English, and major regional languages .

#### 9.6 Compatibility

- **ABDM Interoperability:** The system must natively integrate with the national digital health infrastructure, successfully authenticating and linking to ABHA (Ayushman Bharat Health Account) IDs .
- **Standardized Data Exchange:** It must push the structured clinical history directly to the hospital's Information System (HIS/EMR) utilizing standard FHIR-based APIs .

→ docs/architecture/SYSTEM_ARCHITECTURE.md
→ docs/operations/PRODUCTION_READINESS.md

## 10. System Architecture Overview

*(Note: This architecture is entirely technology-agnostic to accommodate future tech stack decisions, focusing instead on modularity, data flow, and standard integration principles.)*

#### 10.1 High-Level Diagram Description

The system operates as a centralized processing pipeline. Patient inputs—captured via natural voice, touchscreen, and physical document scans—flow into a central AI Orchestration Engine . This engine routes the raw data to specialized AI processing nodes for speech-to-text and image recognition . Once processed, the data is compiled and passed through a secure integration gateway, pushing the final structured clinical summary directly to the Hospital Information System (HIS) and the ABDM ecosystem before the physician consultation begins .

#### 10.2 Layer Breakdown

- **Presentation Layer (Patient Interface):** A dual-mode, zero-training UI featuring icon-driven touch controls and text-to-speech audio prompts to ensure complete accessibility for low-literacy users .
- **AI Intelligence Layer:** Houses the core processing models, including multilingual Automatic Speech Recognition (ASR), the clinical dialogue manager (handling frameworks like SOCRATES and AYUSH parameters), and high-accuracy OCR for document extraction .
- **Orchestration & Logic Layer:** The summary generator that synthesizes the conversational data and extracted document entities (diagnoses, medications, lab values) into a standardized, physician-ready format .
- **Integration & Security Layer:** Manages session termination, DPDP Act 2023 compliant granular consent, ABHA authentication, and FHIR-based API data exchange with external hospital networks .

#### 10.3 Plugin Architecture Principle

The platform is designed with a decoupled "plugin" architecture. Because the final tech stack is currently undecided, external dependencies are treated as swappable modules. Whether the system uses a specific regional ASR model (like Bhashini or AI4Bharat) , a proprietary OCR engine, or connects to different proprietary hospital HIS databases, these are integrated as interchangeable plugins. This ensures that upgrading an AI model or deploying to a new hospital does not break or require rewriting the core history-taking logic.

#### 10.4 PatientDataObject as Central Contract

Throughout the end-to-end patient journey, a single, standardized internal data structure—the `PatientDataObject`—acts as the central source of truth and contract between all modules.

- **Step 1:** It initializes with demographic data and consent flags during ABHA authentication .
- **Step 2:** It progressively populates with the Chief Complaint, HPI, and ROS as the conversational AI conducts the voice interview .
- **Step 3:** It appends the chronological medical timeline and lab values extracted by the document digitization pipeline .
- **Step 4:** This unified object is finally serialized into standard FHIR payloads to safely push the completed, integrated history to both the physician's screen and the patient's digital record .

→ docs/architecture/SYSTEM_ARCHITECTURE.md
→ docs/architecture/BACKEND_ARCHITECTURE.md
→ docs/architecture/PLUGIN_INTERFACE.md
→ docs/database/PATIENT_DATA_OBJECT.md

## 11. AI & Model Requirements

#### 11.1 LLM (MedGemma / Equivalent) Usage Per Module

- **Module A (History Engine):** The language model powers the conversational dialogue manager, dynamically generating intelligent follow-up questions (e.g., the SOCRATES framework) based on the patient's chief complaint and prior answers, constrained by a clinical history ontology .
- **Module B (Document Intelligence):** AI assists in the intelligent extraction, structuring, and chronological timelining of clinical entities (diagnoses, medications, lab values) from raw OCR text .
- **Module C (Summary Generator):** The model acts as a summarization engine, synthesizing both the conversational history and digitized document data into a single, concise, standard clinical format .

#### 11.2 Bhashini / AI4Bharat ASR Requirements

- **Multilingual & Multi-Accent Capture:** The automatic speech recognition (ASR) models must reliably capture and transcribe spoken input across Hindi, English, and major regional languages, accommodating varying accents .
- **Environmental Robustness:** The acoustic models must be specifically tuned to handle highly noisy, overburdened government hospital environments .

#### 11.3 Prompt Behaviour & Guardrails

- **Clinical Constraint:** The AI must follow adaptive questioning trees mirroring a physician's clinical reasoning to elicit a complete HPI and review of systems, rather than engaging in open-ended or non-medical conversation .
- **Emergency Routing:** The system must actively listen for red-flag emergency symptoms (e.g., acute chest pain with dyspnoea, stroke signs) and immediately trigger priority alerts to triage staff, bypassing standard logic .
- **Dual-Mode Sync:** AI prompts must be strictly synchronized with the touchscreen GUI, ensuring that every spoken question has a corresponding touch-based multiple-choice option for the patient .

#### 11.4 What the AI Must NEVER Do

- **No Autonomous Diagnosis:** The AI is strictly an elicitation and summarization tool; it must never generate an autonomous diagnosis, offer medical advice, or prescribe treatments to the patient .
- **No Final Commitments:** The generated clinical summary must never be saved as a final, unalterable medical record automatically; it must remain a draft that the physician retains absolute control to accept, amend, or reject .

→ docs/ai/AI_ARCHITECTURE.md
→ docs/ai/MODEL_ABSTRACTION.md
→ docs/ai/PROMPT_LIBRARY.md

## 12. Clinical Requirements

- **SOCRATES Framework:** Drives the adaptive questioning engine to probe symptoms (e.g., onset, character, radiation, and aggravating factors) .
- **Dashavidha Pariksha Parameters:** Captures specialized Ayurvedic metrics including Prakriti, Vikriti, Agni, Koshtha, Ahara-Vihara, and Nidana .
- **Red Flag Rules:** AI continuously monitors for emergency symptoms (e.g., stroke, acute chest pain) to instantly bypass routine queues and alert triage staff .
- **Clinical Safety Boundaries:** The system strictly generates an editable draft; it is never permitted to make an autonomous medical diagnosis .

→ docs/clinical/CLINICAL_PROTOCOLS.md
→ docs/clinical/SOCRATES_FRAMEWORK.md
→ docs/clinical/RED_FLAG_RULES.md
→ docs/clinical/CLINICAL_SAFETY.md

## 13. Data Requirements

- **PatientDataObject Schema:** Must structure demographics, chief complaint, HPI, past history, and extracted lab values/medications into a standardized FHIR format .
- **Data Collected Per Module:** Captures voice/touch interview inputs alongside scanned physical prescriptions and discharge summaries .
- **Retention & Session Lifecycle:** Temporary session data must be cleared immediately after submission to the hospital system .

→ docs/database/PATIENT_DATA_OBJECT.md
→ docs/database/DATA_MODEL.md
→ docs/database/SCHEMA.md

## 14. Integration Requirements

- **ABDM / ABHA:** Must authenticate patients against the national health account infrastructure .
- **FHIR & HIS Push:** Must utilize FHIR-based interoperability APIs to push structured history directly to the Hospital Information System before consultation .
- **Bhashini / AI4Bharat:** Integrates robust ASR models for multilingual, multi-accent Indian language processing .
- **OCR Pipeline:** Integrates high-accuracy extraction for chronologically sorting and parsing unstructured physical records .

→ docs/integrations/ABDM_FHIR_SPEC.md
→ docs/integrations/BHASHINI_ASR.md
→ docs/integrations/OCR_PIPELINE.md
→ docs/integrations/HIS_INTEGRATION.md

## 15. Privacy & Compliance

- **DPDP Act 2023 & ABDM Framework:** System architecture must guarantee strict adherence to national data protection and health exchange laws .
- **Sensitive Data & Consent:** Implements granular, revocable, audio-guided consent for low-literacy patients before capturing health data .

→ docs/privacy/DPDP_COMPLIANCE.md
→ docs/privacy/CONSENT_ARCHITECTURE.md
→ docs/privacy/DATA_MINIMIZATION.md

## 16. Security Requirements

- **Authentication:** Requires secure verification via ABHA ID or [Aadhaar Redacted] .
- **Session & Processing Security:** Voice and document AI must process sensitive health data securely within the platform and terminate immediately post-submission .

→ docs/security/SECURITY_MODEL.md
→ docs/security/THREAT_MODEL.md

## 17. Accessibility Requirements

- **Low Literacy & Elderly Users:** The software must be fully usable by a first-time, non-tech-savvy patient with zero training .
- **Language & UI Constraints:** Requires dual-mode inputs (speaking OR tapping), icon-driven GUIs, audio prompts, and multi-accent support across Hindi, English, and regional languages .

→ docs/product/USER_PERSONAS.md
→ docs/architecture/SYSTEM_ARCHITECTURE.md

## 18. Error Handling & Fallbacks *(Architecture Guidelines)*

- **Voice Fails → Touch Fallback:** The dual-mode interface ensures that if voice capture fails in a noisy environment, every question remains answerable via touch .
- *(Note: Manual OCR overrides, offline queue handling, and AI timeout rules are standard operational requirements to be defined based on the final tech stack).*

→ docs/architecture/OFFLINE_SYNC.md
→ docs/architecture/SYSTEM_ARCHITECTURE.md

## 19. Testing Requirements *(To Be Defined)*

- **Clinical Accuracy Testing:** Must validate that the AI correctly maps free-form patient narrations into the SOCRATES and Dashavidha Pariksha frameworks .
- **Accessibility Testing:** Must validate zero-training usability for the target low-literacy demographic .
- *(Note: Unit, Integration, and Load testing frameworks depend on final hosting and deployment architecture).*

→ docs/operations/TESTING_STRATEGY.md

## 20. Deployment Requirements *(To Be Defined)*

- **Multi-Tenant Target:** Must scale to handle 4,000–10,000 OPD patients daily across major government hospitals .
- *(Note: Hosting environment, offline capability, and update mechanisms are pending technical finalization).*

→ docs/operations/DEPLOYMENT.md
→ docs/operations/RUNBOOKS.md

## 21. Risks & Mitigations

- **Technical Risk:** Noisy hospital environments disrupting ASR . *Mitigation:* Integration of noise-robust Bhashini models and enforced touch fallbacks .
- **Clinical Risk:** Generating inaccurate histories . *Mitigation:* System enforces a strict "editable draft only" policy, leaving ultimate diagnostic authority to the physician .
- **Adoption Risk:** Patient inability to use the system . *Mitigation:* Icon-driven UI with audio guidance requiring zero prior smartphone literacy .
- 

→ docs/operations/INCIDENT_RECOVERY.md
→ docs/product/SCOPE.md

## 22. Open Questions & Dependencies

- Final selection of the proprietary OCR engine and specific LLM weights for the dialogue manager.
- Specific HIS database credentials and sandbox environments for FHIR API testing with ABDM.

→ docs/operations/PHASES.md

## 23. Appendix

- **Primary Source:** *Problem Statement.pdf* detailing the clinical bottleneck in Indian hospitals .
- **Reference:** 2017 BMJ Open study on global primary-care consultation times .
- **Framework References:** SOCRATES, Dashavidha Pariksha, FHIR standard, DPDP Act 2023.

→ docs/clinical/GLOSSARY.md

## 24. Changelog

- **v1.0:** Initial requirements compiled based on the core MediKiosk problem statement.

→ CHANGELOG.md