/**
 * MediKiosk — Voice & Speech Service
 * Connects to:
 * - POST /voice/transcribe
 * - POST /voice/synthesize
 * - GET /voice/actions
 * - GET /voice/health
 */

import api from './api';
import type {
  SpeechRecognitionResult,
  SpeechSynthesisRequest,
  SpeechSynthesisResult,
} from '@/lib/types';

export const voiceService = {
  /**
   * Transcribe recorded audio chunk or speech sample.
   */
  async transcribe(
    audioBlob: Blob,
    language = 'hi',
    audioFormat = 'webm',
    sessionId?: string
  ): Promise<SpeechRecognitionResult> {
    const formData = new FormData();
    formData.append('file', audioBlob, `recording.${audioFormat}`);
    formData.append('language', language);
    formData.append('audio_format', audioFormat);
    if (sessionId) {
      formData.append('session_id', sessionId);
    }

    const { data } = await api.post<SpeechRecognitionResult>(
      '/voice/transcribe',
      formData
    );
    return data;
  },

  /**
   * Synthesize text to speech audio via Bhashini TTS.
   */
  async synthesize(
    req: SpeechSynthesisRequest
  ): Promise<SpeechSynthesisResult> {
    const { data } = await api.post<SpeechSynthesisResult>(
      '/voice/synthesize',
      req
    );
    return data;
  },

  /**
   * Fetch allow-listed Module E voice actions catalog.
   */
  async getVoiceActions() {
    const { data } = await api.get('/voice/actions');
    return data;
  },

  /**
   * Health status of speech adapters.
   */
  async getHealth() {
    const { data } = await api.get('/voice/health');
    return data;
  },
};
