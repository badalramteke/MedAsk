/**
 * MediKiosk — TypeScript Types
 * Mirrors the backend Pydantic models (PatientDataObject, Interview, Speech, etc.)
 */

// ─── Identity Context ────────────────────────────────────────────────
export interface IdentityContext {
  session_id: string;
  patient_reference?: string | null;
  external_identifier?: string | null;  // ABHA address
  preferred_language?: string;
  language?: string;
  facility_id: string;
  gender?: 'MALE' | 'FEMALE' | 'OTHER' | null;
  age?: number | null;
}

// ─── Consent Context ─────────────────────────────────────────────────
export interface GranularScope {
  granted: boolean;
  granted_at?: string;
  interaction_mode?: 'TOUCH_SCREEN' | 'VOICE_CONFIRMED';
}

export interface ConsentContext {
  status: 'PENDING' | 'GRANTED' | 'DENIED' | 'REVOKED';
  scope: string;
  granted_at?: string;
  scopes: Record<string, GranularScope>;
}

// ─── Patient History ─────────────────────────────────────────────────
export interface PatientHistory {
  chief_complaint?: string;
  hpi?: Record<string, string>;
  past_medical?: string[];
  past_surgical?: string[];
  medications?: string[];
  allergies?: string[];
  family_history?: Record<string, boolean>;
  personal_history?: Record<string, string>;
  review_of_systems?: Record<string, boolean>;
}

// ─── AYUSH History ───────────────────────────────────────────────────
export interface AyushHistory {
  prakriti?: string;
  vikriti?: string;
  agni?: string;
  koshtha?: string;
  ahara_vihara?: Record<string, string>;
  dashavidha?: Record<string, string>;
}

// ─── PatientDataObject (Core Contract) ───────────────────────────────
export interface PatientDataObject {
  version: string;
  last_updated: string;
  identity: IdentityContext;
  consent: ConsentContext;
  history?: PatientHistory;
  ayush?: AyushHistory;
  documents: Record<string, unknown>;
  summary: Record<string, unknown>;
  alerts: Record<string, unknown>;
  integration_status: Record<string, unknown>;
  plugin_outputs: Record<string, unknown>;
}

// ─── Interview / Question Engine ─────────────────────────────────────
export interface QuestionOption {
  option_id: string;
  value_code: string;
  text: string;
  id?: string; // alias
  icon?: string;
}

export interface QuestionResponse {
  question_id: string;
  question_text: string;
  input_type: 'single_select' | 'multi_select' | 'free_text' | 'numeric' | string;
  question_type?: 'SINGLE_SELECT' | 'MULTI_SELECT' | 'FREE_TEXT' | 'NUMERIC' | 'BODY_MAP' | 'PAIN_SCALE';
  options?: QuestionOption[];
  data_element?: string | null;
  phase?: string;
  section?: string;
  progress_percent?: number | null;
  allows_unknown?: boolean;
  allows_refused?: boolean;
  is_completed?: boolean;
  audio_prompt_text?: string;
  metadata?: Record<string, unknown>;
}

export interface AnswerSubmission {
  question_id: string;
  selected_value_codes?: string[];
  selected_option_ids?: string[]; // alias
  free_text?: string | null;
  answer_state?: 'ANSWERED' | 'UNKNOWN' | 'REFUSED';
  answer_type?: 'SELECTED_OPTION' | 'FREE_TEXT' | 'NUMERIC' | 'BODY_MAP_TAP' | 'PAIN_SCALE';
  numeric_value?: number;
  body_region?: string;
  interaction_mode?: 'TOUCH_SCREEN' | 'VOICE_CONFIRMED';
}

export interface RedFlagAlert {
  rule_id: string;
  category?: string;
  urgency_level?: 'EMERGENCY_CRITICAL' | 'URGENT_PRIORITY' | string;
  severity?: 'CRITICAL' | 'HIGH'; // alias
  alert_message: string;
  message?: string; // alias
  action_code?: string;
  triggered_at?: string;
  evidence_summary?: string | null;
  acknowledged?: boolean;
  alert_id?: string;
}

export interface AnswerResult {
  success: boolean;
  accepted?: boolean; // alias
  next_question?: QuestionResponse | null;
  new_alerts?: RedFlagAlert[];
  interview_complete?: boolean;
  question_id?: string;
  next_question_id?: string;
  red_flag_triggered?: boolean;
  red_flag_details?: RedFlagAlert;
  message?: string;
}

// ─── ABHA Authentication ─────────────────────────────────────────────
export interface AbhaAuthInitRequest {
  auth_mode: 'MOBILE_OTP' | 'AADHAAR_OTP';
  abha_address?: string;
  abha_number?: string;
  mobile?: string;
}

export interface AbhaAuthInitResponse {
  transaction_id: string;
  auth_mode: string;
  message: string;
  is_mock_sandbox: boolean;
}

export interface AbhaAuthConfirmRequest {
  transaction_id: string;
  otp: string;
}

export interface AbhaAuthConfirmResponse {
  success: boolean;
  abha_number: string;
  abha_address: string;
  name: string;
  gender: string;
  dob: string;
  mobile: string;
  linked_session_id: string;
  message: string;
}

// ─── Consent API ─────────────────────────────────────────────────────
export interface ConsentGrantRequest {
  scope: string;
  interaction_mode: 'TOUCH_SCREEN' | 'VOICE_CONFIRMED';
  language: string;
  evidence_reference?: string;
}

export interface ConsentRevokeRequest {
  scope: string;
  reason?: string;
}

// ─── Speech / Voice ──────────────────────────────────────────────────
export interface SpeechRecognitionResult {
  success: boolean;
  transcript: string;
  detected_language?: string;
  language?: string;
  confidence: number;
  provider_used: string;
  latency_ms?: number;
  is_voice_action?: boolean;
  matched_action?: string;
  detected_voice_action?: string;
  is_fallback?: boolean;
}

export interface SpeechSynthesisRequest {
  text: string;
  language: string;
  gender?: 'MALE' | 'FEMALE';
  audio_format?: string;
}

export interface SpeechSynthesisResult {
  audio_base64: string;
  audio_format: string;
  duration_ms: number;
  provider_used: string;
}

// ─── Documents ───────────────────────────────────────────────────────
export interface DocumentUploadResult {
  document_id: string;
  document_type: string;
  filename: string;
  status: 'UPLOADED' | 'PROCESSING' | 'EXTRACTED' | 'FAILED';
  extracted_data?: Record<string, unknown>;
}

export interface DocumentTimelineEntry {
  document_id: string;
  document_type: string;
  date?: string;
  extracted_medications?: string[];
  extracted_diagnoses?: string[];
  lab_values?: LabValue[];
  source_thumbnail?: string;
}

export interface LabValue {
  test_name: string;
  value: string;
  unit: string;
  reference_range: string;
  is_abnormal: boolean;
}

// ─── Summary ─────────────────────────────────────────────────────────
export interface ClinicalSummary {
  session_id: string;
  sections: SummarySection[];
  review_status: 'DRAFT' | 'ACCEPTED' | 'AMENDED' | 'REJECTED';
  generated_at: string;
}

export interface SummarySection {
  key: string;
  title: string;
  content: string;
  provenance: string[];
}

// ─── Triage Alerts ───────────────────────────────────────────────────
export interface TriageAlert {
  alert_id: string;
  session_id: string;
  rule_id: string;
  severity: 'CRITICAL' | 'HIGH';
  patient_demographics: string;
  message: string;
  status: 'TRIGGERED' | 'ACKNOWLEDGED' | 'RESOLVED';
  triggered_at: string;
  acknowledged_by?: string;
  acknowledged_at?: string;
  triage_notes?: string;
}

// ─── Integration / FHIR ─────────────────────────────────────────────
export interface DeliveryRecord {
  session_id: string;
  target: string;
  state: string;
  bundle_id?: string;
  is_mock: boolean;
  submitted_at?: string;
}

// ─── API Error Response ──────────────────────────────────────────────
export interface ApiError {
  error_code: string;
  message: string;
  correlation_id?: string;
}
