/**
 * MediKiosk — Session Store (Zustand)
 * Manages kiosk session lifecycle, language preference, identity, and clinical mode.
 */

import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import type { LanguageCode, IntakeMode } from '@/lib/constants';

export interface SessionState {
  sessionId: string | null;
  language: LanguageCode;
  intakeMode: IntakeMode;
  patientName: string;
  patientAge: number | null;
  patientGender: 'MALE' | 'FEMALE' | 'OTHER' | null;
  abhaNumber: string | null;
  abhaAddress: string | null;
  authMode: 'ABHA' | 'AADHAAR' | 'QR' | 'GUEST' | null;
  consentGranted: boolean;
  consentTimestamp: string | null;
  isEmergency: boolean;
  emergencyReason: string | null;
  returnPath?: string | null;
  tokenNumber: string | null;
  assignedRoom: string | null;

  // Actions
  startSession: (language?: LanguageCode) => string;
  ensureBackendSession: (language?: LanguageCode) => Promise<string>;
  setLanguage: (lang: LanguageCode) => void;
  setIntakeMode: (mode: IntakeMode) => void;
  setIdentity: (data: {
    name?: string;
    age?: number;
    gender?: 'MALE' | 'FEMALE' | 'OTHER';
    abhaNumber?: string;
    abhaAddress?: string;
    authMode?: 'ABHA' | 'AADHAAR' | 'QR' | 'GUEST';
  }) => void;
  setConsent: (granted: boolean) => void;
  triggerEmergency: (reason: string, returnPath?: string) => void;
  clearEmergency: () => void;
  setCompletedToken: (token: string, room: string) => void;
  resetSession: () => void;
}

export const useSessionStore = create<SessionState>()(
  persist(
    (set, get) => ({
      sessionId: null,
      language: 'en',
      intakeMode: 'ALLOPATHIC',
      patientName: '',
      patientAge: null,
      patientGender: null,
      abhaNumber: null,
      abhaAddress: null,
      authMode: null,
      consentGranted: false,
      consentTimestamp: null,
      isEmergency: false,
      emergencyReason: null,
      returnPath: null,
      tokenNumber: null,
      assignedRoom: null,

      startSession: (language = 'en') => {
        const newSessionId = `SESS_${Date.now()}_${Math.random().toString(36).substring(2, 7).toUpperCase()}`;
        set({
          sessionId: newSessionId,
          language,
          intakeMode: 'ALLOPATHIC',
          patientName: '',
          patientAge: null,
          patientGender: null,
          abhaNumber: null,
          abhaAddress: null,
          authMode: null,
          consentGranted: false,
          consentTimestamp: null,
          isEmergency: false,
          emergencyReason: null,
          returnPath: null,
          tokenNumber: null,
          assignedRoom: null,
        });

        return newSessionId;
      },

      ensureBackendSession: async (language) => {
        const state = get();
        const activeLang = language || state.language || 'en';
        let sid = state.sessionId;
        if (!sid) {
          sid = state.startSession(activeLang);
        }
        try {
          const { sessionService } = await import('@/services/sessionService');
          await sessionService.createSession({
            session_id: sid,
            preferred_language: activeLang,
            facility_id: 'AIIA_NEW_DELHI_01',
          });
        } catch (err: any) {
          // If 409 SESSION_CONFLICT, it was already created on the backend
          if (err?.response?.status !== 409) {
            console.warn('Backend session initialization note:', err?.message);
          }
        }
        return sid;
      },

      setLanguage: (language: LanguageCode) => set({ language }),

      setIntakeMode: (intakeMode: IntakeMode) => set({ intakeMode }),

      setIdentity: (data) =>
        set((state) => ({
          patientName: data.name ?? state.patientName,
          patientAge: data.age ?? state.patientAge,
          patientGender: data.gender ?? state.patientGender,
          abhaNumber: data.abhaNumber ?? state.abhaNumber,
          abhaAddress: data.abhaAddress ?? state.abhaAddress,
          authMode: data.authMode ?? state.authMode,
        })),

      setConsent: (granted: boolean) =>
        set({
          consentGranted: granted,
          consentTimestamp: granted ? new Date().toISOString() : null,
        }),

      triggerEmergency: (reason: string, returnPath?: string) =>
        set({
          isEmergency: true,
          emergencyReason: reason,
          returnPath: returnPath ?? null,
        }),

      clearEmergency: () =>
        set({
          isEmergency: false,
          emergencyReason: null,
          returnPath: null,
        }),

      setCompletedToken: (tokenNumber: string, assignedRoom: string) =>
        set({
          tokenNumber,
          assignedRoom,
        }),

      resetSession: () =>
        set({
          sessionId: null,
          language: 'en',
          intakeMode: 'ALLOPATHIC',
          patientName: '',
          patientAge: null,
          patientGender: null,
          abhaNumber: null,
          abhaAddress: null,
          authMode: null,
          consentGranted: false,
          consentTimestamp: null,
          isEmergency: false,
          emergencyReason: null,
          returnPath: null,
          tokenNumber: null,
          assignedRoom: null,
        }),
    }),
    {
      name: 'medikiosk-session-storage',
      storage: createJSONStorage(() => sessionStorage),
    }
  )
);
