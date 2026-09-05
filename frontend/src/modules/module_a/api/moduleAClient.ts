/**
 * REST and WebSocket API Client for Module A: Conversational Multimodal History Engine.
 * Interacts with /api/v1/module-a endpoints.
 */

export interface QuestionOption {
  id: string;
  text: string;
  value: string;
  icon?: string;
}

export interface QuestionItem {
  question_id: string;
  phase: string;
  text: string;
  input_type: 'mcq' | 'multi_mcq' | 'text' | 'scale' | 'body_map' | 'summary' | 'none';
  options: QuestionOption[];
  socrates_dimension?: string;
  helper_text?: string;
}

export interface RedFlagAlert {
  alert_id: string;
  severity: string;
  reason: string;
  matched_symptom: string;
  action_required: string;
  detected_at: string;
}

export interface SessionStartResponse {
  session_id: string;
  first_question: QuestionItem;
  audio_b64?: string;
  current_phase: string;
  mode: string;
  language: string;
  message: string;
}

export interface AnswerResponse {
  is_valid: boolean;
  validation_message?: string;
  next_question?: QuestionItem;
  audio_b64?: string;
  phase: string;
  progress_percent: number;
  red_flag_detected: boolean;
  red_flag_alert?: RedFlagAlert;
  is_complete: boolean;
}

export interface SessionStateResponse {
  session_id: string;
  phase: string;
  language: string;
  mode: string;
  chief_complaint?: string;
  answered_fields: Record<string, any>;
  red_flag_active: boolean;
  progress_percent: number;
}

export interface HpiStructuredSummary {
  schema_version: string;
  session_id: string;
  patient_id?: string;
  chief_complaint: string;
  interview_mode: string;
  language: string;
  socrates: {
    site?: string;
    onset?: string;
    character?: string;
    radiation?: string;
    associations?: string[];
    time_course?: string;
    exacerbating_relieving?: string;
    severity?: string;
  };
  review_of_systems: {
    cardiovascular?: string[];
    respiratory?: string[];
    gastrointestinal?: string[];
    neurological?: string[];
    musculoskeletal?: string[];
    pertinent_negatives?: string[];
  };
  ayush_pariksha?: {
    dashavidha: Record<string, any>;
    ashtavidha: Record<string, any>;
    dosha_predominance?: string;
    recommendations?: string[];
  };
  red_flags: Array<{
    alert_id: string;
    symptom: string;
    reason: string;
    severity: string;
    timestamp: string;
  }>;
  raw_transcript: Array<{
    speaker: string;
    message: string;
    timestamp: string;
    audio_confidence?: number;
  }>;
  generated_at: string;
  clinician_notes_ready: boolean;
}

const RAW_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
const API_BASE = RAW_BASE.endsWith('/module-a') ? RAW_BASE : `${RAW_BASE}/module-a`;

export const moduleAClient = {
  /**
   * Starts a new Module A conversational history session
   */
  async startSession(params: {
    patientId?: string;
    language?: string;
    chiefComplaint?: string;
    mode?: 'allopathic' | 'ayush' | 'both';
  }): Promise<SessionStartResponse> {
    const res = await fetch(`${API_BASE_URL}/module-a/session/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        patient_id: params.patientId || null,
        language: params.language || 'en',
        chief_complaint: params.chiefComplaint || null,
        mode: params.mode || 'allopathic',
      }),
    });
    if (!res.ok) {
      throw new Error(`Failed to start Module A session: ${res.status} ${res.statusText}`);
    }
    return res.json();
  },

  /**
   * Submits an answer (text, touch option, or audio b64)
   */
  async submitAnswer(
    sessionId: string,
    params: {
      answerText?: string;
      optionId?: string;
      optionIds?: string[];
      audioB64?: string;
      confidence?: number;
    }
  ): Promise<AnswerResponse> {
    const res = await fetch(`${API_BASE_URL}/module-a/session/${sessionId}/answer`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: sessionId,
        answer_text: params.answerText || null,
        option_id: params.optionId || null,
        option_ids: params.optionIds || null,
        audio_b64: params.audioB64 || null,
        confidence: params.confidence || null,
      }),
    });
    if (!res.ok) {
      throw new Error(`Failed to submit answer: ${res.status} ${res.statusText}`);
    }
    return res.json();
  },

  /**
   * Switches clinical mode (allopathic, ayush, both)
   */
  async switchMode(sessionId: string, mode: 'allopathic' | 'ayush' | 'both'): Promise<any> {
    const res = await fetch(`${API_BASE_URL}/module-a/session/${sessionId}/mode`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ mode }),
    });
    if (!res.ok) {
      throw new Error(`Failed to switch mode: ${res.status}`);
    }
    return res.json();
  },

  /**
   * Retrieves active session state
   */
  async getSessionState(sessionId: string): Promise<SessionStateResponse> {
    const res = await fetch(`${API_BASE_URL}/module-a/session/${sessionId}/state`);
    if (!res.ok) {
      throw new Error(`Failed to fetch session state: ${res.status}`);
    }
    return res.json();
  },

  /**
   * Requests completion and generates physician-ready summary
   */
  async completeSession(sessionId: string): Promise<HpiStructuredSummary> {
    const res = await fetch(`${API_BASE_URL}/module-a/session/${sessionId}/complete`, {
      method: 'POST',
    });
    if (!res.ok) {
      throw new Error(`Failed to complete session: ${res.status}`);
    }
    return res.json();
  },

  /**
   * Fetches the generated HPI summary
   */
  async getSessionSummary(sessionId: string): Promise<HpiStructuredSummary> {
    const res = await fetch(`${API_BASE_URL}/module-a/session/${sessionId}/summary`);
    if (!res.ok) {
      throw new Error(`Failed to retrieve summary: ${res.status}`);
    }
    return res.json();
  },

  /**
   * Returns WebSocket URL for the session
   */
  getWebSocketUrl(sessionId: string): string {
    const wsProto = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = process.env.NEXT_PUBLIC_API_URL
      ? process.env.NEXT_PUBLIC_API_URL.replace(/^http(s)?:\/\//, '').replace(/\/api\/v1$/, '')
      : 'localhost:8000';
    return `${wsProto}//${host}/api/v1/module-a/ws/${sessionId}`;
  },
};
