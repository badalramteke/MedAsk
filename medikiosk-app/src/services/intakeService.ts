/**
 * MediKiosk — Clinical Intake & Dialogue Engine Service
 * Connects to:
 * - GET /sessions/{id}/next-question
 * - POST /sessions/{id}/answer
 * - POST /sessions/{id}/voice/answer
 * - POST /sessions/{id}/ai/structure-narration
 * - POST /sessions/{id}/ai/generate-summary
 * - GET /sessions/{id}/summary
 * - POST /sessions/{id}/summary/review
 * - POST /sessions/{id}/integration/prepare
 * - POST /sessions/{id}/integration/submit
 */

import api from './api';
import type {
  QuestionResponse,
  AnswerSubmission,
  AnswerResult,
  ClinicalSummary,
  DeliveryRecord,
} from '@/lib/types';

export const intakeService = {
  /**
   * Fetch the current adaptive question in the clinical dialogue graph.
   */
  async getNextQuestion(sessionId: string): Promise<QuestionResponse> {
    const { data } = await api.get<QuestionResponse>(
      `/sessions/${sessionId}/next-question`
    );
    return data;
  },

  /**
   * Submit an answer to the current question (touch or validated voice).
   */
  async submitAnswer(
    sessionId: string,
    submission: AnswerSubmission
  ): Promise<AnswerResult> {
    const payload = {
      question_id: submission.question_id,
      selected_value_codes: submission.selected_value_codes || submission.selected_option_ids || [],
      free_text: submission.free_text || null,
      answer_state: submission.answer_state || 'ANSWERED',
    };
    const { data } = await api.post<AnswerResult>(
      `/sessions/${sessionId}/answer`,
      payload
    );
    return data;
  },

  /**
   * Submit raw voice audio for transcription and direct question answering.
   */
  async submitVoiceAnswer(
    sessionId: string,
    formData: FormData
  ): Promise<AnswerResult> {
    const { data } = await api.post<AnswerResult>(
      `/sessions/${sessionId}/voice/answer`,
      formData
    );
    return data;
  },

  /**
   * Request MedGemma to structure free-form clinical narration.
   */
  async structureNarration(sessionId: string, rawText: string, language = 'en') {
    const { data } = await api.post(
      `/sessions/${sessionId}/ai/structure-narration`,
      null,
      {
        params: { narration_text: rawText, language },
      }
    );
    return data;
  },

  /**
   * Generate structured clinical history summary (Module C).
   */
  async generateSummary(sessionId: string): Promise<ClinicalSummary> {
    const { data } = await api.post<ClinicalSummary>(
      `/sessions/${sessionId}/ai/generate-summary`
    );
    return data;
  },

  /**
   * Get existing summary draft.
   */
  async getSummary(sessionId: string): Promise<ClinicalSummary> {
    const { data } = await api.get<ClinicalSummary>(
      `/sessions/${sessionId}/summary`
    );
    return data;
  },

  /**
   * Physician/patient review action on summary.
   */
  async reviewSummary(
    sessionId: string,
    action: 'ACCEPT' | 'AMEND' | 'REJECT',
    amendments?: Record<string, string>
  ) {
    const { data } = await api.post(`/sessions/${sessionId}/summary/review`, {
      action,
      amendments,
    });
    return data;
  },

  /**
   * Prepare NRCeS FHIR R4 Bundle for ABDM/HIS delivery.
   */
  async prepareFhirBundle(sessionId: string) {
    const { data } = await api.post(
      `/sessions/${sessionId}/integration/prepare`
    );
    return data;
  },

  /**
   * Deliver consented FHIR R4 Bundle to hospital HIS or ABDM gateway.
   */
  async submitDelivery(
    sessionId: string,
    target: 'MOCK' | 'ABDM_SANDBOX' | 'HOSPITAL_HIS' = 'MOCK'
  ): Promise<DeliveryRecord> {
    const { data } = await api.post<DeliveryRecord>(
      `/sessions/${sessionId}/integration/submit`,
      null,
      {
        params: { target },
      }
    );
    return data;
  },
};
