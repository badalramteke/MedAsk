/**
 * MediKiosk — Emergency Triage & Alert Service
 * Connects to:
 * - GET /alerts
 * - GET /sessions/{session_id}/alerts
 * - POST /alerts/{alert_id}/acknowledge
 */

import api from './api';
import type { TriageAlert } from '@/lib/types';

export const triageService = {
  /**
   * Get red-flag alerts triggered in the current session.
   */
  async getSessionAlerts(sessionId: string): Promise<{
    session_id: string;
    active_alerts_count: number;
    alerts: TriageAlert[];
  }> {
    const { data } = await api.get<{
      session_id: string;
      active_alerts_count: number;
      alerts: TriageAlert[];
    }>(`/sessions/${sessionId}/alerts`);
    return data;
  },

  /**
   * Get global emergency triage queue (for nurse/doctor station).
   */
  async getGlobalQueue(facilityId?: string, status?: string) {
    const { data } = await api.get('/alerts', {
      params: { facility_id: facilityId, status },
    });
    return data;
  },

  /**
   * Nurse or clinical staff acknowledges the emergency alert.
   */
  async acknowledgeAlert(
    alertId: string,
    staffIdOrReq: string | { staff_id: string; triage_action: string; notes?: string },
    triageAction?: string,
    notes?: string
  ) {
    const payload =
      typeof staffIdOrReq === 'object'
        ? staffIdOrReq
        : { staff_id: staffIdOrReq, triage_action: triageAction || 'ACKNOWLEDGED', notes };
    const { data } = await api.post(`/alerts/${alertId}/acknowledge`, payload);
    return data;
  },
};
