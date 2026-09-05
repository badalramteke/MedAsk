# MediKiosk — End-to-End Frontend Pages & UI Components Specification

> **Purpose:** Exhaustive reference catalog of all screens, page routes, sub-views, and reusable UI components required for the MediKiosk platform. Use this guide to prepare all Figma / UI mockups before starting Phase 11 (Frontend Patient Flow) and Phase 12 (Frontend Clinician Flow).

---


## 2. Complete Screen-by-Screen Specification (16 Screens)

### Screen 01: Landing & Attractor Screen (`/`)
* **Target Audience:** First-time walk-in patients, elderly, rural users with zero training.
* **Layout:** Clean, high-contrast, welcoming hero with prominent touch button and ambient audio greeting.
* **Core UI Components:**
  1. `KioskHeader`: Hospital Logo (AIIA / AIIMS / General), Emergency SOS button, Current Time.
  2. `HeroWelcomeCard`: Animated visual illustration of a patient speaking / tapping.
  3. `StartIntakeButton`: Massive 64px+ primary action button with pulsating highlight ("यहाँ शुरू करें / Tap to Start").
  4. `QuickLanguageBar`: 6 language badges (English, हिंदी, मराठी, বাংলা, தமிழ், తెలుగు).
  5. `AudioWelcomePrompt`: Speaker icon playing audio guidance: *"Welcome to MediKiosk. Please tap the green button to begin."*

---

### Screen 02: Language Selection Screen (`/language`)
* **Target Audience:** All patients choosing their native language for voice and touchscreen prompts.
* **Layout:** 2x3 or 3x2 responsive card grid with prominent script typography and native flags/icons.
* **Core UI Components:**
  1. `LanguageCard` (x6):
     - English (`English`)
     - Hindi (`हिन्दी`)
     - Marathi (`मराठी`)
     - Bengali (`বাংলা`)
     - Tamil (`தமிழ்`)
     - Telugu (`తెలుగు`)
  2. `AudioSampleButton`: Plays 2-second preview: *"नमस्ते, क्या आप हिंदी चुनना चाहते हैं?"*
  3. `NextStepButton`: Large footer action button with directional arrow icon.

---

### Screen 03: Patient Identification & ABHA Authentication (`/auth`)
* **Target Audience:** Patients with existing ABHA IDs, Aadhaar cards, or walk-in guests.
* **Layout:** 4-tab authentication selector with on-screen virtual numpad (no external keyboard required).
* **Core UI Components:**
  1. `AuthModeTabs`:
     - **Tab A: ABHA Number / Address** (14-digit `XX-XXXX-XXXX-XXXX` or `name@abdm`).
     - **Tab B: Scan ABHA QR Code** (Live camera viewfinder for physical ABHA card or ABHA App scan).
     - **Tab C: Aadhaar OTP / Demographic** (Aadhaar last-4 digits + OTP entry).
     - **Tab D: Quick Walk-in Guest Mode** (Direct Name, Age, Gender input for immediate intake without ABHA).
  2. `VirtualNumpad`: Large high-contrast touch keys (0-9, Backspace, Clear, Submit).
  3. `OTPVerificationModal`: 6-digit pin boxes with countdown timer and "Resend OTP" button.
  4. `PatientProfilePreviewCard`: Displays verified photo, name, age, gender, and ABHA ID badge upon successful verification.

---

### Screen 04: DPDP & ABDM Granular Consent Screen (`/consent`)
* **Target Audience:** Compliant consent capture under Digital Personal Data Protection Act 2023.
* **Layout:** Audio-guided notice with granular toggle cards and legal privacy trust badges.
* **Core UI Components:**
  1. `ConsentAudioPlayer`: Auto-plays spoken notice in selected language: *"We will record your symptoms to help your doctor. Your audio is erased after consultation."*
  2. `GranularScopeCheckboxes`:
     - Scope 1: **Clinical Intake** (Voice & symptom history).
     - Scope 2: **Document Scanning** (Prescriptions & lab reports extraction).
     - Scope 3: **Summary Synthesis** (AI draft for doctor review).
     - Scope 4: **ABDM & HIS Sharing** (Link to ABHA personal health locker).
  3. `InteractionBadge`: Logs whether consent was given via `TOUCH_SCREEN` or `VOICE_CONFIRMED`.
  4. `ConsentActionButtons`:
     - `AgreeButton`: Green "सहमत हैं / I Agree".
     - `DeclineButton`: Neutral "अस्वीकार / Decline & Continue as Anonymous".

---

### Screen 05: Intake Mode Selector (Demo & Environment Switch) (`/intake/mode-select`)
* **Target Audience:** Demonstration switch to choose between General Allopathic Hospital OPD vs Ayurvedic AYUSH Hospital OPD.
* **Layout:** Two high-impact visual selector cards comparing the two intake protocols.
* **Core UI Components:**
  1. `AllopathicModeCard`:
     - Title: **General OPD (Allopathic)**
     - Subtitle: SOCRATES Symptom Engine, Past History, Medications, Allergies, Review of Systems.
     - Icon: Stethoscope / Modern Hospital Icon.
  2. `AyushModeCard`:
     - Title: **Ayurvedic OPD (AYUSH - AIIA New Delhi)**
     - Subtitle: Dashavidha Pariksha, Prakriti, Vikriti, Agni, Koshtha, Ahara-Vihara assessment.
     - Icon: Lotus / Ayurveda Herbal Medicine Icon.
  3. `DemoNoticeBadge`: *"Selected mode configures question sequence and clinical ontology."*

---

### Screen 06: Symptom Intake & SOCRATES Adaptive Engine (`/intake/symptoms`)
* **Target Audience:** Patient recording chief complaint and deep-dive HPI via voice and touch.
* **Layout:** Split dual-mode interface: Top = Question text & Audio prompt, Center = Option cards & body map, Bottom = Push-to-Talk Mic & Navigation bar.
* **Core UI Components:**
  1. `AudioQuestionBanner`: Displays question text in vernacular + speaker button to re-play audio.
  2. `BodyMapSelector`: Interactive anatomical diagram (tap Head, Chest, Throat, Abdomen, Back, Joint) to pick chief complaint.
  3. `CommonComplaintChips`: Quick-tap cards (Chest Pain, Fever, Cough, Headache, Vomiting, Weakness).
  4. `SingleSelectGrid` / `MultiSelectGrid`: Big 24px text cards with checkmark states.
  5. `PainSeveritySlider`: 1-to-10 visual slider with Wong-Baker facial expression scale (😊 Mild -> 😭 Severe).
  6. `PushToTalkMicButton`: Massive floating microphone button with pulsing audio waveform animation when speaking.
  7. `StepProgressBar`: Shows progress percentage through SOCRATES and General sections.

---

### Screen 07: Ayurvedic Dashavidha Pariksha Intake (`/intake/ayush`)
* **Target Audience:** Patients in Ayurvedic OPDs capturing traditional diagnostic parameters.
* **Layout:** Icon-driven holistic cards with audio explanations for classical terms.
* **Core UI Components:**
  1. `TridoshaBalanceSlider`: Vata, Pitta, Kapha visual balance indicator with icon guides.
  2. `AgniStatusCards`:
     - *Samagni* (Normal / Balanced Digestion)
     - *Mandagni* (Slow / Sluggish Digestion)
     - *Tikshnagni* (Excess / Burning Digestion)
     - *Vishamagni* (Irregular / Bloating Digestion)
  3. `KoshthaSelector`: Bowel habit cards (*Mridu* - Soft, *Madhyama* - Regular, *Krura* - Hard/Constipated).
  4. `AharaViharaGrid`: Diet preferences (Veg/Non-veg/Spicy), Sleep quality (Good/Disturbed), Daily physical exertion.

---

### Screen 08: Document Scanner & Upload (`/documents/scan`)
* **Target Audience:** Patients carrying physical paper prescriptions, lab reports, discharge summaries, or X-ray films.
* **Layout:** Live camera feed with edge guide overlay + gallery/file upload picker.
* **Core UI Components:**
  1. `LiveCameraViewfinder`: Document auto-detection green border with flash toggle and capture button.
  2. `DocumentTypeSelector`:
     - Prescription (`Rx`)
     - Lab Report (`🧪`)
     - Discharge Summary (`📋`)
     - Imaging / X-Ray Film (`🩻`)
  3. `FilePickerDropzone`: Drag & drop or browse PDF / JPG / PNG files (10MB limit).
  4. `CapturedThumbnailCarousel`: Displays uploaded pages with crop, delete, and re-take buttons.
  5. `OCRProcessingStatusBadge`: Animated spinner: *"Extracting medications & lab values..."*

---

### Screen 09: Digitized Records Review & Timeline (`/documents/timeline`)
* **Target Audience:** Patient reviewing what the system extracted before sending to the doctor.
* **Layout:** Vertical chronological medical timeline with extracted entity badges.
* **Core UI Components:**
  1. `ChronologicalTimeline`: Ordered timeline nodes dating from oldest to newest prior visits.
  2. `ExtractedMedicationPills`: Medication name, dosage, frequency (e.g. `Metformin 500mg - 1-0-1`).
  3. `LabValueCard`:
     - Normal: Green pill (`Hemoglobin: 13.5 g/dL`).
     - Out-of-Range: Red/Amber warning badge (`HbA1c: 7.8% [HIGH]`, `Ref: <5.7%`).
  4. `SourceDocumentThumbnail`: Clickable preview to view original uploaded image.

---

### Screen 10: Patient Summary Confirmation (`/summary`)
* **Target Audience:** Patient confirming the recorded facts before finishing.
* **Layout:** Visual card summary + native language audio playback.
* **Core UI Components:**
  1. `SummaryAudioPlayer`: Large player reading the vernacular audio script: *"You reported chest pain for 2 hours with left arm radiation. Tap confirm to send to doctor."*
  2. `SectionSummaryAccordion`: Collapsible cards for Chief Complaint, HPI, Past Illness, Meds, Allergies.
  3. `EditSectionButton`: Allows patient to correct an answer if misunderstood.
  4. `FinalSubmitButton`: Large green button: *"डॉक्टर को भेजें / Submit to Doctor"*.

---

### Screen 11: Emergency Red-Flag Triage Bypass Overlay (`/triage/alert`)
* **Target Audience:** Critical patients triggering emergency triage rules (e.g. acute chest pain radiating to arm).
* **Layout:** High-urgency red pulsing screen with prominent instructions and staff notification status.
* **Core UI Components:**
  1. `EmergencyAlertBanner`: High-contrast red banner: *"Emergency Symptom Detected / आपातकालीन लक्षण पहचाने गए"*.
  2. `TriageInstructionCard`: *"Please proceed immediately to Emergency Room / Triage Desk. Nursing staff has been notified."*
  3. `StaffAlertStatusBadge`: *"Alert Sent to Nurse Station Priya (Bay 2)"*.
  4. `CallStaffButton`: Direct SOS bell to call kiosk assistant.

---

### Screen 12: Intake Complete & OPD Queue Token (`/complete`)
* **Target Audience:** Patient finished with intake, receiving queue token.
* **Layout:** Clean receipt-style card with session termination countdown.
* **Core UI Components:**
  1. `OPDTokenCard`:
     - Big Token Number: `Token # 42`
     - Assigned Room: `Room 104 - Dr. Arvind Kumar (Cardiology OPD)`
     - QR Code for instant doctor scan.
  2. `SessionPurgeCountdown`: 30-second countdown timer: *"Your session data is now securely cleared from this kiosk."*
  3. `PrintTokenButton` / `ExitButton`.

---

### Screen 13: OPD Waiting Queue Dashboard (`/doctor/queue`)
* **Target Audience:** OPD Physicians & Consultation Room Staff.
* **Layout:** Desktop/Tablet responsive table with real-time intake status badges and filter controls.
* **Core UI Components:**
  1. `QueueTable`: Columns for Token #, Patient Name/Age/Gender, ABHA ID, Chief Complaint, Intake Mode (Allopathic/AYUSH), Summary Status (`PENDING`, `ACCEPTED`, `AMENDED`), Wait Time.
  2. `UrgencyFilter`: All, Normal, Red-Flag Priority.
  3. `OpenSummaryButton`: Action button to load patient's full clinical review screen.

---

### Screen 14: Clinician Review & Draft Summary Editor (`/doctor/summary/[patientId]`)
* **Target Audience:** Attending Doctor in consultation room (2-5 minute consultation window).
* **Layout:** Desktop Split-View: **Left (60%)** = 9-Section Editable Clinical Draft, **Right (40%)** = Original Scanned Documents & Medical Image Viewer.
* **Core UI Components:**
  1. `PatientDemographicsHeader`: Name, Age, Gender, ABHA Number, Consultation Time.
  2. `ClinicalSectionEditor` (9 distinct sections):
     - Chief Complaint
     - History of Present Illness (HPI)
     - Past Medical & Surgical History
     - Medications & Known Allergies
     - Family History
     - Personal & Social History
     - Review of Systems (ROS)
     - Prior Investigations & Lab Summary
     - Imaging Findings (Chest X-Ray / CT observations)
     - AYUSH Dashavidha Summary (if AYUSH mode)
  3. `ProvenanceCitationBadges`: Embedded tags (e.g. `[Patient Spoken]`, `[Doc#1: Lab 2024-05-12]`, `[AI Draft: 96% confidence]`).
  4. `DocumentSplitViewer`: Interactive image zoom/pan for handwritten prescriptions and X-rays.
  5. `ClinicianActionToolbar`:
     - `AcceptDraftButton` (Green)
     - `AmendSectionButton` (Blue - with inline diff highlighting)
     - `RejectDraftButton` (Red)
     - `PushToHisButton` (Purple - FHIR R4 Bundle hand-off to hospital EMR & ABDM)

---

### Screen 15: Nurse Emergency Triage Dashboard (`/nurse/triage-dashboard`)
* **Target Audience:** Hospital Triage Nurses & Casualty Staff.
* **Layout:** Real-time live emergency alert cards with audio chime notifications.
* **Core UI Components:**
  1. `ActiveAlertCards`: Kiosk ID, Patient Demographics, Flag ID (e.g. `RF_CARD_001_CHEST_PAIN`), Elapsed Time counter, Severity (`CRITICAL`, `HIGH`).
  2. `FastTrackActions`: Fast-track ECG, Immediate Vitals, Route to Resuscitation Bay.
  3. `AcknowledgeModal`: Nurse Staff ID, Triage action taken, Clinical notes.

---

### Screen 16: Kiosk & Hardware Health Monitor (`/admin/status`)
* **Target Audience:** Hospital IT and Administrative Engineers.
* **Layout:** System observability dashboard for microservices and kiosk peripheral hardware.
* **Core UI Components:**
  1. `HardwareStatusWidgets`: Microphone status, Camera status, Thermal Printer status, Touchscreen calibration.
  2. `BackendServiceCards`: Colab MedGemma GPU latency, Bhashini ASR/TTS latency, PostgreSQL/Redis health, ABDM Sandbox Gateway connectivity.
  3. `ActiveKioskGrid`: Health status of all 10-50 physical kiosk terminals in the OPD lobby.

---

## 3. Core Reusable UI Component Library

| Component Category | Component Name | Description & Usage |
| :--- | :--- | :--- |
| **Voice & Audio** | `VoiceWaveformVisualizer` | Real-time Canvas/SVG audio wave visualizer for spoken input. |
| | `PushToTalkButton` | Massive 64px floating/inline microphone with mic active animations. |
| | `AudioPromptPlayer` | Auto-playing and manual speaker icon for question audio. |
| | `TTSPlaybackControl` | Speed, play, pause, replay controls for patient summary confirmation. |
| **Navigation & Layout** | `KioskHeader` | Hospital branding, Emergency SOS, Language switcher, High-contrast toggle. |
| | `KioskFooter` | Persistent Back, Next, Help, and Touch/Speak mode indicator. |
| | `StepProgressBar` | Visual progress tracker showing completed clinical sections. |
| | `DemoModeSwitch` | Quick-toggle between Allopathic and AYUSH intake modes. |
| **Interactive Inputs** | `OptionCard` | Large, high-contrast selectable card with icon, title, and vernacular translation. |
| | `BodyMapSelector` | Interactive SVG human anatomy selector for symptom localization. |
| | `PainSeveritySlider` | 1-10 slider with Wong-Baker facial expressions. |
| | `VirtualNumpad` | Large on-screen numeric keypad for OTP, age, and ABHA numbers. |
| **Documents & Imaging** | `LiveCameraViewfinder` | Camera preview with green bounding box and flash/crop tools. |
| | `ChronologicalTimeline` | Vertical medical timeline linking prior prescriptions & labs. |
| | `LabRangeBadge` | Colored pills (Green = Normal, Red = High, Blue = Low) with reference ranges. |
| | `DocumentSplitViewer` | Side-by-side zoomable image and PDF viewer for physician screen. |
| **Clinician & Review** | `ClinicalSectionEditor` | Rich text / formatted section editor with undo/redo and provenance tags. |
| | `ProvenanceCitationBadge` | Small pill tag indicating source (`[Doc#1]`, `[Spoken]`, `[AI Draft]`). |
| | `ClinicianActionToolbar` | Accept, Amend, Reject, and Push to ABDM action buttons. |
| **Modals & Alerts** | `RedFlagEmergencyModal` | Pulsing red emergency alert modal for critical symptom detection. |
| | `ConsentAudioModal` | Granular DPDP consent notice modal with audio playback. |
| | `SessionPurgeCountdown` | Ephemeral data purge countdown timer modal. |
| | `StaffAcknowledgeModal` | Nurse triage acknowledgement form with staff ID and notes. |

---

## 4. Design Guidelines for UI/Figma Preparation

1. **Responsiveness:**
   - **Mobile Viewport:** 375px – 430px (Vertical scrolling, bottom floating mic, thumb-friendly tap zones).
   - **Tablet Viewport:** 768px – 1024px (4:3 and 16:10 iPad/Android tablets, 2-column option grids).
   - **Kiosk / Desktop Viewport:** 1920x1080 Full HD (Touchscreen optimized, big buttons, split-screen doctor view).
2. **Accessibility & Contrast:**
   - Touch targets must be minimum **48px x 48px** (recommended **64px** for kiosk buttons).
   - High color contrast ratio (WCAG AAA compliant, minimum 7:1 for text).
   - Font family: `Inter` for English + `Noto Sans Devanagari/Tamil/Telugu/Bengali` for Indian scripts.
3. **Mandatory Element Attributes:**
   - Every interactive component must carry `data-element`, `data-voice-action`, `data-testid`, `id`, and `aria-label` matching [`PATHS.md`](file:///c:/Users/ASUS/OneDrive/Pictures/college%205th%20sem/SIH/Foudational%20FIles/docs/architecture/PATHS.md).
