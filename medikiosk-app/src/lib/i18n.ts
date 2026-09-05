/**
 * MediKiosk — Internationalization (i18n) System
 * Multilingual support for 6 Indian languages per TECH_STACK.md
 */

import { LanguageCode } from './constants';

// ─── Type Definitions ────────────────────────────────────────────────
export type TranslationKey = keyof typeof en;

type TranslationDict = Record<string, string>;

// ─── English (Default) ──────────────────────────────────────────────
const en: TranslationDict = {
  // Header & Navigation
  'app.name': 'MediKiosk',
  'app.subtitle': 'AI Clinical History Platform',
  'header.hospital': 'at City General Hospital',
  'header.sos': 'SOS ASSIST',
  'header.help': 'Help',
  'nav.back': 'Back',
  'nav.next': 'Next',
  'nav.continue': 'Continue',
  'nav.skip': 'Skip',
  'nav.confirm': 'Confirm',
  'nav.cancel': 'Cancel',

  // Landing / Welcome
  'welcome.title': 'Welcome to MediKiosk',
  'welcome.subtitle': 'AI-Powered Clinical Check-in',
  'welcome.tap_to_start': 'Tap to Start',
  'welcome.audio_greeting': 'Welcome to MediKiosk. Please tap the green button to begin your check-in.',

  // Language Selection
  'language.title': 'Choose your language',
  'language.subtitle': 'You can change this anytime during your check-in.',
  'language.selected': 'Selected',
  'language.listen': 'Listen',

  // Mode Selection
  'mode.title': 'Select your consultation type',
  'mode.allopathic': 'General OPD (Allopathic)',
  'mode.allopathic_desc': 'Modern Medicine – SOCRATES Symptom Assessment',
  'mode.ayush': 'Ayurvedic OPD (AYUSH)',
  'mode.ayush_desc': 'Dashavidha Pariksha, Prakriti & Vikriti Assessment',

  // Patient Identification
  'auth.title': 'Verify your identity',
  'auth.abha_tab': 'ABHA Number',
  'auth.qr_tab': 'Scan QR Code',
  'auth.aadhaar_tab': 'Aadhaar OTP',
  'auth.guest_tab': 'Walk-in Guest',
  'auth.enter_abha': 'Enter your 14-digit ABHA number',
  'auth.scan_qr': 'Place your ABHA card under the scanner',
  'auth.enter_otp': 'Enter the 6-digit OTP sent to your mobile',
  'auth.resend_otp': 'Resend OTP',
  'auth.verify': 'Verify',
  'auth.guest_name': 'Full Name',
  'auth.guest_age': 'Age',
  'auth.guest_gender': 'Gender',
  'auth.guest_register': 'Register as Guest',

  // Consent
  'consent.title': 'Privacy & Data Consent',
  'consent.subtitle': 'We need your permission to proceed. Your data is protected under the DPDP Act 2023.',
  'consent.scope_intake': 'Clinical Intake — Voice & symptom history recording',
  'consent.scope_documents': 'Document Scanning — Prescriptions & lab report extraction',
  'consent.scope_summary': 'Summary Synthesis — AI draft for your doctor',
  'consent.scope_his': 'ABDM & HIS Sharing — Link to your ABHA health record',
  'consent.agree': 'I Agree',
  'consent.decline': 'Decline & Continue Anonymously',
  'consent.audio_notice': 'We will record your symptoms to help your doctor. Your audio is erased after consultation.',

  // Symptom Intake
  'intake.title': 'Tell us about your symptoms',
  'intake.chief_complaint': 'What is your main problem today?',
  'intake.body_map': 'Tap on the body area where you feel pain',
  'intake.speak_or_tap': 'Speak or tap to answer',
  'intake.recording': 'Listening...',
  'intake.tap_to_speak': 'Tap to speak',
  'intake.common_complaints': 'Common symptoms',

  // Pain Assessment
  'pain.title': 'How severe is your pain?',
  'pain.scale_mild': 'Mild',
  'pain.scale_moderate': 'Moderate',
  'pain.scale_severe': 'Severe',
  'pain.scale_worst': 'Worst',

  // SOCRATES Deep Dive
  'socrates.site': 'Where exactly do you feel it?',
  'socrates.onset': 'When did it start?',
  'socrates.character': 'What does it feel like?',
  'socrates.radiation': 'Does the pain spread anywhere?',
  'socrates.associations': 'Any other symptoms along with this?',
  'socrates.timing': 'Is it constant or does it come and go?',
  'socrates.exacerbating': 'What makes it worse?',
  'socrates.severity': 'How bad is it on a scale of 1 to 10?',

  // Past History
  'history.title': 'Past Medical History',
  'history.conditions': 'Do you have any of these conditions?',
  'history.surgeries': 'Any previous surgeries?',
  'history.hospitalizations': 'Any hospital admissions?',

  // Medications & Allergies
  'allergy.title': 'Medications & Allergies',
  'allergy.current_meds': 'Are you currently taking any medicines?',
  'allergy.known_allergies': 'Do you have any known allergies?',
  'allergy.drug_allergy': 'Drug Allergies',
  'allergy.food_allergy': 'Food Allergies',

  // Family History
  'family.title': 'Family Medical History',
  'family.subtitle': 'Has anyone in your family been diagnosed with:',

  // Lifestyle
  'lifestyle.title': 'Personal & Lifestyle',
  'lifestyle.smoking': 'Do you smoke?',
  'lifestyle.alcohol': 'Do you consume alcohol?',
  'lifestyle.exercise': 'How physically active are you?',
  'lifestyle.diet': 'Dietary preference',

  // Review of Systems
  'ros.title': 'Review of Systems',
  'ros.subtitle': 'Have you experienced any of these recently?',

  // Documents
  'documents.title': 'Scan Your Medical Documents',
  'documents.subtitle': 'Upload prescriptions, lab reports, or discharge summaries',
  'documents.capture': 'Take Photo',
  'documents.upload': 'Upload File',
  'documents.type_prescription': 'Prescription',
  'documents.type_lab': 'Lab Report',
  'documents.type_discharge': 'Discharge Summary',
  'documents.type_imaging': 'X-Ray / Imaging',
  'documents.processing': 'Extracting medications & lab values...',
  'documents.skip': 'Skip — No documents to scan',

  // Timeline
  'timeline.title': 'Your Medical Records',
  'timeline.subtitle': 'Review what we extracted from your documents',

  // Summary
  'summary.title': 'Review Your Information',
  'summary.subtitle': 'Please confirm everything is correct before submitting to your doctor.',
  'summary.listen': 'Listen to Summary',
  'summary.edit': 'Edit Section',
  'summary.submit': 'Submit to Doctor',

  // Emergency / Triage
  'emergency.title': 'Emergency Symptom Detected',
  'emergency.instruction': 'Please proceed immediately to the Emergency Room. Nursing staff has been notified.',
  'emergency.staff_alert': 'Alert Sent to Nurse Station',
  'emergency.call_staff': 'Call Staff',

  // Complete
  'complete.title': 'Check-in Complete!',
  'complete.token': 'Your Token Number',
  'complete.room': 'Assigned Room',
  'complete.purge': 'Your session data will be securely cleared in',
  'complete.print': 'Print Token',
  'complete.exit': 'Exit',

  // Session
  'session.timeout_warning': 'Your session will expire soon. Tap to continue.',
  'session.expired': 'Session expired. Please start again.',

  // Error States
  'error.title': 'Something went wrong',
  'error.retry': 'Try Again',
  'error.network': 'Connection lost. Please check your network.',
  'error.voice_failed': 'Voice capture failed. Please use touch input.',

  // Help / SOS
  'help.title': 'Need Assistance?',
  'help.call_staff': 'Call for staff assistance',
  'help.calling': 'Calling staff...',
};

// ─── Hindi ──────────────────────────────────────────────────────────
const hi: TranslationDict = {
  'app.name': 'MediKiosk',
  'app.subtitle': 'AI नैदानिक इतिहास प्लेटफ़ॉर्म',
  'header.hospital': 'सिटी जनरल अस्पताल',
  'header.sos': 'SOS सहायता',
  'header.help': 'मदद',
  'nav.back': 'पीछे',
  'nav.next': 'आगे',
  'nav.continue': 'जारी रखें',
  'nav.skip': 'छोड़ें',
  'nav.confirm': 'पुष्टि करें',
  'nav.cancel': 'रद्द करें',
  'welcome.title': 'MediKiosk में आपका स्वागत है',
  'welcome.subtitle': 'AI-संचालित नैदानिक चेक-इन',
  'welcome.tap_to_start': 'शुरू करने के लिए टैप करें',
  'welcome.audio_greeting': 'MediKiosk में आपका स्वागत है। कृपया हरे बटन पर टैप करके अपना चेक-इन शुरू करें।',
  'language.title': 'अपनी भाषा चुनें',
  'language.subtitle': 'आप अपनी चेक-इन के दौरान कभी भी इसे बदल सकते हैं।',
  'language.selected': 'चयनित',
  'language.listen': 'सुनें',
  'mode.title': 'अपना परामर्श प्रकार चुनें',
  'mode.allopathic': 'सामान्य OPD (एलोपैथिक)',
  'mode.allopathic_desc': 'आधुनिक चिकित्सा – SOCRATES लक्षण मूल्यांकन',
  'mode.ayush': 'आयुर्वेदिक OPD (आयुष)',
  'mode.ayush_desc': 'दशविध परीक्षा, प्रकृति और विकृति मूल्यांकन',
  'auth.title': 'अपनी पहचान सत्यापित करें',
  'auth.abha_tab': 'ABHA नंबर',
  'auth.qr_tab': 'QR कोड स्कैन करें',
  'auth.aadhaar_tab': 'आधार OTP',
  'auth.guest_tab': 'वॉक-इन अतिथि',
  'auth.verify': 'सत्यापित करें',
  'consent.title': 'गोपनीयता और डेटा सहमति',
  'consent.agree': 'मैं सहमत हूँ',
  'consent.decline': 'अस्वीकार करें',
  'intake.title': 'अपने लक्षण बताएं',
  'intake.chief_complaint': 'आज आपकी मुख्य समस्या क्या है?',
  'intake.tap_to_speak': 'बोलने के लिए टैप करें',
  'intake.recording': 'सुन रहे हैं...',
  'pain.title': 'आपका दर्द कितना गंभीर है?',
  'pain.scale_mild': 'हल्का',
  'pain.scale_moderate': 'मध्यम',
  'pain.scale_severe': 'गंभीर',
  'pain.scale_worst': 'सबसे ज्यादा',
  'documents.title': 'अपने चिकित्सा दस्तावेज़ स्कैन करें',
  'documents.capture': 'फोटो लें',
  'documents.upload': 'फ़ाइल अपलोड करें',
  'summary.title': 'अपनी जानकारी की समीक्षा करें',
  'summary.submit': 'डॉक्टर को भेजें',
  'emergency.title': 'आपातकालीन लक्षण पहचाने गए',
  'emergency.instruction': 'कृपया तुरंत आपातकालीन कक्ष में जाएं। नर्सिंग स्टाफ को सूचित किया गया है।',
  'complete.title': 'चेक-इन पूरा!',
  'complete.token': 'आपका टोकन नंबर',
  'complete.print': 'टोकन प्रिंट करें',
  'complete.exit': 'बाहर निकलें',
  'error.title': 'कुछ गलत हो गया',
  'error.retry': 'पुनः प्रयास करें',
  'help.title': 'सहायता चाहिए?',
  'help.call_staff': 'स्टाफ सहायता के लिए कॉल करें',
};

// ─── Marathi ────────────────────────────────────────────────────────
const mr: TranslationDict = {
  'app.name': 'MediKiosk',
  'welcome.title': 'MediKiosk मध्ये आपले स्वागत',
  'welcome.tap_to_start': 'सुरू करण्यासाठी टॅप करा',
  'language.title': 'तुमची भाषा निवडा',
  'nav.back': 'मागे',
  'nav.next': 'पुढे',
  'nav.confirm': 'पुष्टी करा',
  'consent.agree': 'मी सहमत आहे',
  'intake.title': 'तुमची लक्षणे सांगा',
  'intake.tap_to_speak': 'बोलण्यासाठी टॅप करा',
  'summary.submit': 'डॉक्टरांना पाठवा',
  'complete.title': 'चेक-इन पूर्ण!',
};

// ─── Bengali ────────────────────────────────────────────────────────
const bn: TranslationDict = {
  'app.name': 'MediKiosk',
  'welcome.title': 'MediKiosk-এ স্বাগতম',
  'welcome.tap_to_start': 'শুরু করতে ট্যাপ করুন',
  'language.title': 'আপনার ভাষা বেছে নিন',
  'nav.back': 'পিছনে',
  'nav.next': 'পরবর্তী',
  'nav.confirm': 'নিশ্চিত করুন',
  'consent.agree': 'আমি সম্মত',
  'intake.title': 'আপনার লক্ষণগুলি বলুন',
  'intake.tap_to_speak': 'কথা বলতে ট্যাপ করুন',
  'summary.submit': 'ডাক্তারের কাছে পাঠান',
  'complete.title': 'চেক-ইন সম্পূর্ণ!',
};

// ─── Tamil ──────────────────────────────────────────────────────────
const ta: TranslationDict = {
  'app.name': 'MediKiosk',
  'welcome.title': 'MediKiosk-க்கு வரவேற்கிறோம்',
  'welcome.tap_to_start': 'தொடங்க தொடவும்',
  'language.title': 'உங்கள் மொழியை தேர்ந்தெடுக்கவும்',
  'nav.back': 'பின்செல்',
  'nav.next': 'அடுத்து',
  'nav.confirm': 'உறுதிப்படுத்து',
  'consent.agree': 'நான் ஒப்புக்கொள்கிறேன்',
  'intake.title': 'உங்கள் அறிகுறிகளைக் கூறுங்கள்',
  'intake.tap_to_speak': 'பேச தொடவும்',
  'summary.submit': 'மருத்துவருக்கு அனுப்பு',
  'complete.title': 'சோதனை முடிந்தது!',
};

// ─── Telugu ─────────────────────────────────────────────────────────
const te: TranslationDict = {
  'app.name': 'MediKiosk',
  'welcome.title': 'MediKiosk కు స్వాగతం',
  'welcome.tap_to_start': 'ప్రారంభించడానికి నొక్కండి',
  'language.title': 'మీ భాషను ఎంచుకోండి',
  'nav.back': 'వెనుకకు',
  'nav.next': 'తదుపరి',
  'nav.confirm': 'నిర్ధారించు',
  'consent.agree': 'నేను అంగీకరిస్తున్నాను',
  'intake.title': 'మీ లక్షణాలు చెప్పండి',
  'intake.tap_to_speak': 'మాట్లాడటానికి నొక్కండి',
  'summary.submit': 'డాక్టర్‌కు పంపండి',
  'complete.title': 'చెక్-ఇన్ పూర్తయింది!',
};

// ─── Dictionary Map ─────────────────────────────────────────────────
const dictionaries: Record<LanguageCode, TranslationDict> = {
  en,
  hi,
  mr,
  bn,
  ta,
  te,
};

/**
 * Get a translated string for the given key and language.
 * Falls back to English if the key doesn't exist in the target language.
 */
export function t(key: string, lang: LanguageCode = 'en'): string {
  return dictionaries[lang]?.[key] || dictionaries.en[key] || key;
}

/**
 * Get the full dictionary for a language (useful for React context).
 */
export function getDictionary(lang: LanguageCode): TranslationDict {
  return { ...en, ...dictionaries[lang] };
}
