// MediKiosk Remix - Complete Sequential Flow Definition
const FLOW_STAGES = [
    {
        key: 'STAGE_0',
        name: 'Stage 0: Attract & Welcome',
        screens: [
            {
                id: 'welcome_gate',
                title: 'WelcomeGate — Attract / Idle Screen',
                file: 'ae1f7b4e_Refined MediKiosk Landing Scre.html',
                description: 'Initial kiosk standby touch screen with bilingual welcome audio prompt and touch trigger.'
            },
            {
                id: 'idle_screensaver',
                title: 'IdleAttract — Kiosk Ambient Screensaver',
                file: '2e10b0ea_MediKiosk Idle Screensaver.html',
                description: 'Ambient screensaver cycling through regional languages with hospital service announcements.'
            }
        ]
    },
    {
        key: 'STAGE_1',
        name: 'Stage 1: Language, Mode & Identification',
        screens: [
            {
                id: 'language_picker',
                title: 'TonguePicker — Language Selection',
                file: '0a11af49_Refined Language Selection Scr.html',
                description: 'Touch and voice language selection. Supports English and regional Indian languages with audio sample playout.'
            },
            {
                id: 'mode_selection',
                title: 'PathFork — Clinical Mode (Allopathy / AYUSH / Specialist)',
                file: '994a7e63_OPD Mode Selection Screen.html',
                description: 'Branches workflow between standard Modern Medicine, AYUSH Dashavidha Pariksha, and Specialist Clinics.'
            },
            {
                id: 'patient_id_options',
                title: 'IdentityVault — Patient Identification Hub',
                file: '9f1d0b7e_Patient Identification & ABHA .html',
                description: 'Authentication routing: ABHA ID, Aadhaar OTP, Scan ABHA QR, or Walk-in registration.'
            },
            {
                id: 'scan_abha_qr',
                title: 'QRPulse — Scan ABHA QR Code',
                file: 'cfac1ba7_Scan ABHA QR Code - Patient Id.html',
                description: 'Contactless ABHA barcode/QR scanner integration for instant profile retrieval.'
            },
            {
                id: 'aadhaar_otp',
                title: 'AadhaarLock — OTP Verification',
                file: '081f3b50_Aadhaar OTP Verification - Pat.html',
                description: 'Secure 6-digit OTP verification with countdown timer and audio confirmation.'
            },
            {
                id: 'walkin_registration',
                title: 'NewPatientForm — Walk-in Registration (English)',
                file: '8987c2a0_New Patient Registration - Ste.html',
                description: 'Quick demographic intake for walk-in patients without prior digital health IDs.'
            },
            {
                id: 'abha_create_wizard',
                title: 'ABHACreateWizard — Create New ABHA ID',
                file: 'bce10dad_ABHACreateWizard - Step 1 of 3.html',
                description: 'Guided 3-step wizard to register a new ABHA health ID directly at the kiosk.'
            },
            {
                id: 'consent_chamber',
                title: 'ConsentChamber — DPDP & ABDM Privacy Gate',
                file: 'e6aabff4_Patient Privacy & Consent.html',
                description: 'DPDP Act 2023 compliant granular consent capture with voice readout and opt-in toggles.'
            }
        ]
    },
    {
        key: 'STAGE_2',
        name: 'Stage 2: Multimodal Conversational History (Voice & Touch)',
        screens: [
            {
                id: 'chief_complaint',
                title: 'ChiefComplaintArena — Primary Symptom Selection',
                file: '0624525c_Symptom Intake & Assessment.html',
                description: 'Top presenting complaints cards (Chest Pain, Fever, Cough, Abdominal Pain) with direct voice microphone.'
            },
            {
                id: 'voice_orb',
                title: 'VoiceOrb — Active Clinical Voice Intake',
                file: '08aafed3_VoiceOrb - Active Clinical Int.html',
                description: 'Pulsating voice orb with real-time audio waveform visualizer and live speech-to-text transcription card.'
            },
            {
                id: 'pain_mapper',
                title: 'PainMapper — Body Pain Locator & Wong-Baker Scale',
                file: 'c1d1156e_PainMapper - Pain Assessment I.html',
                description: 'Interactive anatomical front/back body diagram with pulsating red pain dots and 0-10 intensity slider.'
            },
            {
                id: 'socrates_engine',
                title: 'SocratesOracle — SOCRATES Deep-Dive Clinical Engine',
                file: '6a120e45_SOCRATES Clinical Deep-Dive Qu.html',
                description: 'Clinical reasoning engine probing Site, Onset, Character, Radiation, Associations, Timing, Exacerbating factors.'
            },
            {
                id: 'past_medical',
                title: 'ChronicLedger — Past Medical Visits & Surgeries',
                file: '143e58b5_Past Medical Visits & History.html',
                description: 'Timeline of pre-existing chronic conditions, hospital admissions, and surgical history.'
            },
            {
                id: 'allergy_vault',
                title: 'AllergyVault — Drug & Allergy History Intake',
                file: '8f14f247_AllergyVault - Drug & Allergy .html',
                description: 'Dedicated intake for drug sensitivities, food allergies, and current ongoing prescriptions.'
            },
            {
                id: 'family_saga',
                title: 'FamilySaga — Family Health History Tree',
                file: '0de966fd_FamilySaga - Family History Co.html',
                description: 'Visual family member cards capturing hereditary heart disease, diabetes, hypertension, and cancer risks.'
            },
            {
                id: 'lifestyle_sketch',
                title: 'LifestyleSketch — Personal & Social History',
                file: 'f71a8903_Lifestyle Assessment - Persona.html',
                description: 'Touch cards and sliders for smoking status, alcohol use, dietary habits, and sleep duration.'
            },
            {
                id: 'ros_checklist',
                title: 'ROSChecklist — System-by-System Review of Systems',
                file: '0b957e05_ROSChecklist - Review of Syste.html',
                description: 'Comprehensive 10-system card grid for cardiorespiratory, neurological, GI, and musculoskeletal symptoms.'
            },
            {
                id: 'ayush_intake',
                title: 'PrakritiFold — Ayurvedic Dashavidha Pariksha Intake',
                file: '799f7cdf_Ayurvedic Assessment & Intake.html',
                description: 'Extended AYUSH OPD intake measuring Prakriti constitution, Vikriti imbalance, Agni, and Ahara-Vihara.'
            }
        ]
    },
    {
        key: 'STAGE_3',
        name: 'Stage 3: Medical Document Digitization & Timeline',
        screens: [
            {
                id: 'document_scan',
                title: 'DocPortal — Optical Document Scanner & Upload',
                file: '5c686871_Document Scanning & OCR Intake.html',
                description: 'Live camera scan or physical scanner slot feed for paper prescriptions, discharge sheets, and lab reports.'
            },
            {
                id: 'doc_timeline',
                title: 'DocTimeline — Chronological Medical Record Timeline',
                file: '6d5b3405_DocTimeline - Medical History .html',
                description: 'Year-by-year chronological timeline synthesizing multiple hospital visits into a single unified record.'
            },
            {
                id: 'doc_detail_viewer',
                title: 'DocDetailViewer — Extracted OCR Entity Inspector',
                file: 'a8485404_DocDetailViewer - Medical Docu.html',
                description: 'Dual-pane inspector displaying scanned paper image with bounding boxes alongside structured FHIR entities.'
            },
            {
                id: 'abnormal_flag_panel',
                title: 'AbnormalFlagPanel — Out-of-Range Clinical Alerts',
                file: '8ccb24e7_AbnormalFlagPanel - Clinical A.html',
                description: 'High-visibility flags for abnormal lab values (HbA1c, Creatinine) and drug interaction warnings.'
            }
        ]
    },
    {
        key: 'STAGE_4',
        name: 'Stage 4: AI Summary Synthesis, ABDM Push & Token',
        screens: [
            {
                id: 'patient_summary_review',
                title: 'CrystalReport — AI Clinical Summary Review',
                file: '5f46dc60_Patient Summary & Document Rev.html',
                description: 'Patient-facing synthesized clinical summary in clear English language prior to doctor transmission.'
            },
            {
                id: 'summary_signoff',
                title: 'SignoffPad — Patient Confirmation & Signature',
                file: '4bed5906_Summary Confirmation & Review.html',
                description: 'Final review checklist where the patient reviews captured complaints and grants transmission consent.'
            },
            {
                id: 'abdm_push_status',
                title: 'ABHAPushStatus — ABDM FHIR Data Push Progress',
                file: 'bbcadfe9_ABHAPushStatus - Data Upload P.html',
                description: 'Live progress animation: FHIR Bundle compilation, sandbox encryption, and ABHA PHR sync.'
            },
            {
                id: 'his_route_confirm',
                title: 'HISRouteConfirm — Hospital System Delivery Confirmation',
                file: '41bd010b_HISRouteConfirm - Hospital Syn.html',
                description: 'Confirmation that intake has arrived at the specific consultation room and doctor queue.'
            },
            {
                id: 'token_receipt',
                title: 'TokenDispenser — Token Completion & Printed Receipt',
                file: 'cfbb13f9_Token Completion & Receipt.html',
                description: 'OPD Queue token number, designated room, QR voucher for phone, and estimated wait time.'
            },
            {
                id: 'waiting_queue',
                title: 'QueuePulse — Live Hospital OPD Queue Display',
                file: 'a006cb85_OPD Waiting Queue.html',
                description: 'Real-time department queue dashboard showing currently called tokens and upcoming turns.'
            }
        ]
    },
    {
        key: 'STAGE_5',
        name: 'Stage 5: Physician Consultation & Clinical Systems',
        screens: [
            {
                id: 'doctor_desk',
                title: 'DoctorDesk — Physician Consultation History View',
                file: '0d74dd84_DoctorDesk - Physician Consult.html',
                description: 'Physician screen showing ready-made history summary (Chief Complaint, HPI, Meds, Labs) with voice replay.'
            },
            {
                id: 'physician_editor',
                title: 'PhysicianEditor — Clinical Summary Review & Edit',
                file: '8745cd29_PhysicianEditor - Clinical Sum.html',
                description: 'Editable clinical intake draft allowing the physician to accept AI suggestions, amend, or add ICD-10 codes.'
            },
            {
                id: 'triage_dashboard',
                title: 'TriageCommand — Emergency Alert Monitoring Dashboard',
                file: '4f0e9786_Emergency Alert Monitoring Das.html',
                description: 'Central nurse triage console receiving high-priority red flag alerts from all hospital kiosks.'
            },
            {
                id: 'triage_ack_modal',
                title: 'AckPulse — Nurse Emergency Triage Acknowledgment Modal',
                file: '4d6a4b98_Nurse Emergency Triage Dashboa.html',
                description: 'Modal for triage staff to claim emergency alerts and dispatch response personnel.'
            },
            {
                id: 'admin_dashboard',
                title: 'AdminNexus — Admin & IT Observability Dashboard',
                file: '8df122f5_Admin & IT Observability Dashb.html',
                description: 'Real-time telemetry: active kiosk terminals, daily patient intake count, and ABDM API latency.'
            }
        ]
    }
];
