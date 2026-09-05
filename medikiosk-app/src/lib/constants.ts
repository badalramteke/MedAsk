/**
 * MediKiosk — Application Constants
 * Central source of truth for all app-wide configuration values.
 */

// ─── API Configuration ───────────────────────────────────────────────
export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
export const WS_BASE_URL =
  process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws';
export const APP_NAME = process.env.NEXT_PUBLIC_APP_NAME || 'MediKiosk';
export const APP_VERSION = '1.0.0';

// ─── Supported Languages (Bhashini / AI4Bharat) ─────────────────────
export const SUPPORTED_LANGUAGES = [
  { code: 'en', label: 'English', nativeLabel: 'English', icon: '🇬🇧' },
  { code: 'hi', label: 'Hindi', nativeLabel: 'हिन्दी', icon: '🇮🇳' },
  { code: 'mr', label: 'Marathi', nativeLabel: 'मराठी', icon: '🇮🇳' },
  { code: 'bn', label: 'Bengali', nativeLabel: 'বাংলা', icon: '🇮🇳' },
  { code: 'ta', label: 'Tamil', nativeLabel: 'தமிழ்', icon: '🇮🇳' },
  { code: 'te', label: 'Telugu', nativeLabel: 'తెలుగు', icon: '🇮🇳' },
] as const;

export type LanguageCode = (typeof SUPPORTED_LANGUAGES)[number]['code'];

// ─── Clinical Flow Stages ────────────────────────────────────────────
export const CLINICAL_STAGES = [
  { key: 'WELCOME', label: 'Welcome', step: 0 },
  { key: 'IDENTIFICATION', label: 'Identification', step: 1 },
  { key: 'CONSENT', label: 'Consent', step: 2 },
  { key: 'INTAKE', label: 'Clinical Intake', step: 3 },
  { key: 'DOCUMENTS', label: 'Documents', step: 4 },
  { key: 'SUMMARY', label: 'Summary', step: 5 },
  { key: 'COMPLETE', label: 'Complete', step: 6 },
] as const;

export type ClinicalStageKey = (typeof CLINICAL_STAGES)[number]['key'];

// ─── Intake Modes ────────────────────────────────────────────────────
export const INTAKE_MODES = {
  ALLOPATHIC: 'ALLOPATHIC',
  AYUSH: 'AYUSH',
} as const;

export type IntakeMode = keyof typeof INTAKE_MODES;

// ─── Consent Scopes (DPDP Act 2023) ─────────────────────────────────
export const CONSENT_SCOPES = [
  'INTAKE',
  'DOCUMENTS',
  'SUMMARY',
  'HIS_SHARE',
] as const;

export type ConsentScope = (typeof CONSENT_SCOPES)[number];

// ─── Session Config ──────────────────────────────────────────────────
export const SESSION_TIMEOUT_MS = 10 * 60 * 1000; // 10 minutes
export const SESSION_WARNING_MS = 8 * 60 * 1000;  // Warning at 8 min
export const SESSION_PURGE_COUNTDOWN_S = 30;       // 30 second countdown

// ─── Voice Config ────────────────────────────────────────────────────
export const VOICE_SAMPLE_RATE = 16000;
export const VOICE_CHANNELS = 1;
export const VOICE_MIME_TYPE = 'audio/webm;codecs=opus';

// ─── Touch Target Sizes (WCAG + Kiosk) ──────────────────────────────
export const TOUCH_MIN_PX = 48;
export const TOUCH_KIOSK_PX = 64;

// ─── Design Tokens (from Stitch Design System) ──────────────────────
export const COLORS = {
  primary: '#005f53',
  primaryContainer: '#0f7a6b',
  onPrimary: '#ffffff',
  onPrimaryContainer: '#abffed',
  secondary: '#006e1c',
  secondaryContainer: '#91f78e',
  tertiary: '#aa0a17',
  tertiaryContainer: '#ce2b2c',
  surface: '#f8fafa',
  surfaceContainer: '#eceeee',
  surfaceContainerLow: '#f2f4f4',
  surfaceContainerHigh: '#e6e8e9',
  onSurface: '#191c1d',
  onSurfaceVariant: '#3e4946',
  outline: '#6e7976',
  outlineVariant: '#bdc9c5',
  error: '#ba1a1a',
  errorContainer: '#ffdad6',
  inverseSurface: '#2e3131',
  inverseOnSurface: '#eff1f1',
} as const;
