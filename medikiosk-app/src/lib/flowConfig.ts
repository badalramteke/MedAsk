/**
 * MediKiosk — Clinical Flow Configuration
 * TypeScript port of flow_data.js with route mappings for Next.js App Router.
 * Defines the sequential patient journey through all clinical stages.
 */

export interface FlowScreen {
  id: string;
  title: string;
  route: string;
  description: string;
  voicePromptKey?: string;  // i18n key for audio prompt
}

export interface FlowStage {
  key: string;
  name: string;
  step: number;
  screens: FlowScreen[];
}

/**
 * Complete patient flow definition — maps 1:1 with PATHS.md routes
 * and FRONTEND_PAGES_AND_COMPONENTS_SPEC.md screens.
 */
export const PATIENT_FLOW: FlowStage[] = [
  {
    key: 'STAGE_0',
    name: 'Welcome & Attract',
    step: 0,
    screens: [
      {
        id: 'welcome_gate',
        title: 'Welcome',
        route: '/',
        description: 'Initial kiosk attract screen with tap-to-start.',
        voicePromptKey: 'welcome.audio_greeting',
      },
    ],
  },
  {
    key: 'STAGE_1',
    name: 'Language, Mode & Identification',
    step: 1,
    screens: [
      {
        id: 'language_picker',
        title: 'Language Selection',
        route: '/language',
        description: 'Choose from 6 supported Indian languages.',
        voicePromptKey: 'language.title',
      },
      {
        id: 'mode_selection',
        title: 'Consultation Mode',
        route: '/intake/mode-select',
        description: 'Select Allopathic or AYUSH intake pathway.',
        voicePromptKey: 'mode.title',
      },
      {
        id: 'patient_identification',
        title: 'Patient Identity',
        route: '/auth',
        description: 'ABHA, Aadhaar OTP, QR scan, or guest walk-in.',
        voicePromptKey: 'auth.title',
      },
    ],
  },
  {
    key: 'STAGE_2',
    name: 'Consent',
    step: 2,
    screens: [
      {
        id: 'consent_capture',
        title: 'Privacy & Consent',
        route: '/consent',
        description: 'DPDP Act 2023 granular consent with audio guidance.',
        voicePromptKey: 'consent.title',
      },
    ],
  },
  {
    key: 'STAGE_3',
    name: 'Clinical Intake',
    step: 3,
    screens: [
      {
        id: 'chief_complaint',
        title: 'Symptom Intake',
        route: '/intake/symptoms',
        description: 'Voice/touch chief complaint capture with body map and pain scale.',
        voicePromptKey: 'intake.chief_complaint',
      },
      {
        id: 'ayush_assessment',
        title: 'Ayurvedic Assessment',
        route: '/intake/ayush',
        description: 'Dashavidha Pariksha, Prakriti, Vikriti, Agni assessment (AYUSH mode only).',
        voicePromptKey: 'intake.title',
      },
    ],
  },
  {
    key: 'STAGE_4',
    name: 'Document Capture',
    step: 4,
    screens: [
      {
        id: 'document_scanner',
        title: 'Document Scanner',
        route: '/documents/scan',
        description: 'Camera/upload for prescriptions, lab reports, discharge summaries.',
        voicePromptKey: 'documents.title',
      },
      {
        id: 'document_timeline',
        title: 'Records Timeline',
        route: '/documents/timeline',
        description: 'Review extracted medications, lab values, and chronological timeline.',
        voicePromptKey: 'timeline.title',
      },
    ],
  },
  {
    key: 'STAGE_5',
    name: 'Summary & Confirmation',
    step: 5,
    screens: [
      {
        id: 'patient_summary',
        title: 'Review Summary',
        route: '/summary',
        description: 'Audio confirmation of captured history in selected language.',
        voicePromptKey: 'summary.title',
      },
    ],
  },
  {
    key: 'STAGE_6',
    name: 'Complete',
    step: 6,
    screens: [
      {
        id: 'opd_token',
        title: 'OPD Token & Exit',
        route: '/complete',
        description: 'Queue token display and session purge countdown.',
        voicePromptKey: 'complete.title',
      },
    ],
  },
];

/**
 * Get all screens as a flat ordered list for sequential navigation.
 */
export function getAllScreensFlat(): FlowScreen[] {
  return PATIENT_FLOW.flatMap((stage) => stage.screens);
}

/**
 * Find the stage containing a given screen ID.
 */
export function getStageForScreen(screenId: string): FlowStage | undefined {
  return PATIENT_FLOW.find((stage) =>
    stage.screens.some((s) => s.id === screenId)
  );
}

/**
 * Get the next screen in the flow after the given screen ID.
 */
export function getNextScreen(currentScreenId: string): FlowScreen | null {
  const allScreens = getAllScreensFlat();
  const idx = allScreens.findIndex((s) => s.id === currentScreenId);
  return idx >= 0 && idx < allScreens.length - 1 ? allScreens[idx + 1] : null;
}

/**
 * Get the previous screen in the flow before the given screen ID.
 */
export function getPreviousScreen(currentScreenId: string): FlowScreen | null {
  const allScreens = getAllScreensFlat();
  const idx = allScreens.findIndex((s) => s.id === currentScreenId);
  return idx > 0 ? allScreens[idx - 1] : null;
}
