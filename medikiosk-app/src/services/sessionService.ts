/**
 * MediKiosk — Session Service
 * Maps to: POST /sessions, GET /sessions/{id}, DELETE /sessions/{id}
 * Also: ABHA auth initiate/confirm
 */

import api from './api';
import type {
  PatientDataObject,
  IdentityContext,
  AbhaAuthInitRequest,
  AbhaAuthInitResponse,
  AbhaAuthConfirmRequest,
  AbhaAuthConfirmResponse,
} from '@/lib/types';

export const sessionService = {
  /**
   * Create a new clinical intake session.
   * POST /api/v1/sessions
   */
  async createSession(identity: Partial<IdentityContext> & { session_id: string }): Promise<PatientDataObject> {
    const fullIdentity = {
      session_id: identity.session_id,
      patient_reference: identity.patient_reference || null,
      external_identifier: identity.external_identifier || null,
      preferred_language: identity.preferred_language || identity.language || 'en',
      facility_id: identity.facility_id || 'AIIA_NEW_DELHI_01',
      gender: identity.gender || null,
      age: identity.age || null,
    };
    const payload = {
      version: '1.0.0',
      identity: fullIdentity,
      consent: {
        status: 'GRANTED',
        scope: 'INTAKE_AND_SUMMARY',
        scopes: {},
      },
      documents: {},
      summary: {},
      alerts: {},
      integration_status: {},
      plugin_outputs: {},
    };
    const { data } = await api.post<PatientDataObject>('/sessions', payload);
    return data;
  },

  /**
   * Retrieve an active session.
   * GET /api/v1/sessions/{sessionId}
   */
  async getSession(sessionId: string): Promise<PatientDataObject> {
    const { data } = await api.get<PatientDataObject>(`/sessions/${sessionId}`);
    return data;
  },

  /**
   * Terminate and purge session (DPDP compliance).
   * DELETE /api/v1/sessions/{sessionId}
   */
  async deleteSession(sessionId: string): Promise<void> {
    await api.delete(`/sessions/${sessionId}`);
  },

  /**
   * Initiate ABHA verification via Mobile OTP or Aadhaar OTP.
   * POST /api/v1/sessions/{sessionId}/abha/initiate
   */
  async initiateAbhaAuth(
    sessionId: string,
    req: AbhaAuthInitRequest
  ): Promise<AbhaAuthInitResponse> {
    const { data } = await api.post<AbhaAuthInitResponse>(
      `/sessions/${sessionId}/abha/initiate`,
      req
    );
    return data;
  },

  /**
   * Confirm ABHA OTP and link identity to session.
   * POST /api/v1/sessions/{sessionId}/abha/confirm
   */
  async confirmAbhaAuth(
    sessionId: string,
    req: AbhaAuthConfirmRequest
  ): Promise<AbhaAuthConfirmResponse> {
    const { data } = await api.post<AbhaAuthConfirmResponse>(
      `/sessions/${sessionId}/abha/confirm`,
      req
    );
    return data;
  },
};
