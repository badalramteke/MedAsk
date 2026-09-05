/**
 * Module A API Client
 * Connects the Next.js kiosk frontend to the FastAPI Module A backend endpoints.
 */

const RAW_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
const API_BASE = RAW_BASE.endsWith('/module-a') ? RAW_BASE : `${RAW_BASE}/module-a`;

export interface StartSessionParams {
  language?: string;
  is_ayush_mode?: boolean;
  chief_complaint_hint?: string;
}

export interface StartSessionResult {
  session_id: string;
  greeting_text: string;
  greeting_audio_base64?: string;
  language: string;
  is_ayush_mode: boolean;
  current_section: string;
  options?: string[];
}

export interface AnswerSubmissionResult {
  session_id: string;
  accepted: boolean;
  next_question?: string;
  next_question_english?: string;
  next_options?: string[];
  audio_base64?: string;
  current_section: string;
  answered_count: number;
  total_required: number;
  progress_percentage: number;
  is_complete: boolean;
  red_flag_triggered: boolean;
  red_flag_alert?: any;
}

export interface SessionStateResult {
  session_id: string;
  language: string;
  is_ayush_mode: boolean;
  current_section: string;
  chief_complaint?: string;
  socrates: Record<string, any>;
  ros_answers: Record<string, any>;
  ayush_answers: Record<string, any>;
  red_flags_detected: string[];
  current_question?: string;
  current_options?: string[];
  answered_count: number;
  total_required: number;
  progress_percentage: number;
  hpi_complete: boolean;
}

export const moduleAClient = {
  async startSession(params: StartSessionParams = {}): Promise<StartSessionResult> {
    const res = await fetch(`${API_BASE}/session/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        language: params.language || 'hi',
        is_ayush_mode: !!params.is_ayush_mode,
        chief_complaint_hint: params.chief_complaint_hint,
      }),
    });
    if (!res.ok) throw new Error(`Failed to start session: ${res.statusText}`);
    return res.json();
  },

  async submitAnswer(
    sessionId: string,
    answerText: string,
    optionCode?: string,
    source: 'touch' | 'voice' = 'touch'
  ): Promise<AnswerSubmissionResult> {
    const res = await fetch(`${API_BASE}/session/${sessionId}/answer`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        answer_text: answerText,
        option_code: optionCode,
        source,
      }),
    });
    if (!res.ok) throw new Error(`Failed to submit answer: ${res.statusText}`);
    return res.json();
  },

  async getState(sessionId: string): Promise<SessionStateResult> {
    const res = await fetch(`${API_BASE}/session/${sessionId}/state`);
    if (!res.ok) throw new Error(`Failed to get session state: ${res.statusText}`);
    return res.json();
  },

  async switchLanguage(sessionId: string, language: string): Promise<{ language: string; updated_question: string }> {
    const res = await fetch(`${API_BASE}/session/${sessionId}/language`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ language }),
    });
    if (!res.ok) throw new Error(`Failed to switch language: ${res.statusText}`);
    return res.json();
  },

  async getSummary(sessionId: string): Promise<any> {
    const res = await fetch(`${API_BASE}/session/${sessionId}/summary`);
    if (!res.ok) throw new Error(`Failed to get summary: ${res.statusText}`);
    return res.json();
  },

  async endSession(sessionId: string): Promise<void> {
    try {
      await fetch(`${API_BASE}/session/${sessionId}`, { method: 'DELETE' });
    } catch {
      // Best effort cleanup
    }
  },
};
