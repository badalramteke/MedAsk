/**
 * MediKiosk — Consent Service
 * Connects to:
 * - GET /sessions/{id}/consent
 * - POST /sessions/{id}/consent
 * - POST /sessions/{id}/consent/revoke
 * - GET /sessions/{id}/consent/audio-script
 */

import api from './api';
import type {
  ConsentGrantRequest,
  ConsentRevokeRequest,
} from '@/lib/types';

export interface ConsentAudioScriptResponse {
  session_id: string;
  scope: string;
  language: string;
  audio_script: string;
}

export const consentService = {
  /**
   * Get active consent status and scopes.
   */
  async getConsent(sessionId: string) {
    const { data } = await api.get(`/sessions/${sessionId}/consent`);
    return data;
  },

  /**
   * Grant affirmative consent for a scope under DPDP Act 2023.
   */
  async grantConsent(sessionId: string, req: ConsentGrantRequest) {
    const { data } = await api.post(`/sessions/${sessionId}/consent`, req);
    return data;
  },

  /**
   * Revoke consent for a scope.
   */
  async revokeConsent(sessionId: string, req: ConsentRevokeRequest) {
    const { data } = await api.post(`/sessions/${sessionId}/consent/revoke`, req);
    return data;
  },

  /**
   * Get vernacular audio guidance script for TTS playback.
   */
  async getAudioScript(
    sessionId: string,
    scope = 'INTAKE',
    language = 'en'
  ): Promise<ConsentAudioScriptResponse> {
    const { data } = await api.get<ConsentAudioScriptResponse>(
      `/sessions/${sessionId}/consent/audio-script`,
      {
        params: { scope, language },
      }
    );
    return data;
  },
};
