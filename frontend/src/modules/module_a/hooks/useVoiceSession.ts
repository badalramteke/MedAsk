'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { moduleAClient, RedFlagAlert, QuestionItem } from '../api/moduleAClient';

export type VoiceOrbState = 'idle' | 'listening' | 'processing' | 'speaking' | 'red_flag';

interface UseVoiceSessionProps {
  sessionId: string | null;
  language: string;
  onQuestionAdvanced?: (nextQuestion: QuestionItem, phase: string, progress: number) => void;
  onRedFlagDetected?: (alert: RedFlagAlert) => void;
  onTranscriptInterim?: (transcript: string, confidence: number) => void;
  onSilenceWarning?: (message: string) => void;
}

export function useVoiceSession({
  sessionId,
  language,
  onQuestionAdvanced,
  onRedFlagDetected,
  onTranscriptInterim,
  onSilenceWarning,
}: UseVoiceSessionProps) {
  const [orbState, setOrbState] = useState<VoiceOrbState>('idle');
  const [isConnected, setIsConnected] = useState(false);
  const [isMicActive, setIsMicActive] = useState(false);
  const [interimTranscript, setInterimTranscript] = useState<string>('');
  const [silenceAlert, setSilenceAlert] = useState<string | null>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const mediaStreamRef = useRef<MediaStream | null>(null);
  const silenceTimerRef = useRef<NodeJS.Timeout | null>(null);

  // Reset 30s silence detector
  const resetSilenceTimer = useCallback(() => {
    if (silenceTimerRef.current) {
      clearTimeout(silenceTimerRef.current);
    }
    setSilenceAlert(null);
    silenceTimerRef.current = setTimeout(() => {
      const msg =
        language === 'hi'
          ? 'क्या आप अभी भी यहाँ हैं? कृपया अपना समय लें या स्क्रीन पर दिए गए विकल्प को स्पर्श करें।'
          : 'Are you still there? Please take your time or tap an option on the screen.';
      setSilenceAlert(msg);
      if (onSilenceWarning) onSilenceWarning(msg);
    }, 30000); // 30 seconds
  }, [language, onSilenceWarning]);

  // Connect WebSocket
  useEffect(() => {
    if (!sessionId) return;

    const wsUrl = moduleAClient.getWebSocketUrl(sessionId);
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      setIsConnected(true);
      setOrbState('listening');
      resetSilenceTimer();
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        resetSilenceTimer();

        switch (data.event) {
          case 'CONNECTED':
            setOrbState(data.orb_state || 'listening');
            break;

          case 'ORB_STATE':
            if (data.orb_state) setOrbState(data.orb_state);
            break;

          case 'TRANSCRIPT_INTERIM':
            setInterimTranscript(data.transcript);
            if (onTranscriptInterim) {
              onTranscriptInterim(data.transcript, data.confidence);
            }
            break;

          case 'QUESTION_ADVANCED':
            setInterimTranscript('');
            setOrbState('speaking');
            if (data.next_question && onQuestionAdvanced) {
              onQuestionAdvanced(data.next_question, data.phase, data.progress_percent);
            }
            // Transition back to listening after speech prompt
            setTimeout(() => setOrbState('listening'), 2500);
            break;

          case 'EMERGENCY_RED_FLAG':
            setOrbState('red_flag');
            if (onRedFlagDetected && data.alert) {
              onRedFlagDetected(data.alert);
            }
            break;

          case 'SILENCE_WARNING':
            setSilenceAlert(data.message);
            if (onSilenceWarning) onSilenceWarning(data.message);
            break;

          case 'TRANSCRIPTION_FAILED':
            setOrbState('listening');
            break;

          default:
            break;
        }
      } catch (err) {
        console.error('Error parsing WebSocket message:', err);
      }
    };

    ws.onerror = (err) => {
      console.warn('WebSocket encountered error:', err);
    };

    ws.onclose = () => {
      setIsConnected(false);
      setOrbState('idle');
    };

    return () => {
      ws.close();
      if (silenceTimerRef.current) clearTimeout(silenceTimerRef.current);
    };
  }, [sessionId, resetSilenceTimer, onQuestionAdvanced, onRedFlagDetected, onTranscriptInterim, onSilenceWarning]);

  // Start microphone streaming (250ms chunks)
  const startListening = useCallback(async () => {
    try {
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        console.warn('MediaDevices API not available in this browser environment.');
        return;
      }

      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
          sampleRate: 16000,
        },
      });
      mediaStreamRef.current = stream;

      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
          ? 'audio/webm;codecs=opus'
          : undefined,
      });
      mediaRecorderRef.current = mediaRecorder;

      mediaRecorder.ondataavailable = async (e) => {
        if (e.data.size > 0 && wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
          const buffer = await e.data.arrayBuffer();
          wsRef.current.send(buffer);
          resetSilenceTimer();
        }
      };

      // 250ms chunks as specified in master prompt
      mediaRecorder.start(250);
      setIsMicActive(true);
      setOrbState('listening');
    } catch (err) {
      console.warn('Microphone access denied or unavailable:', err);
      setIsMicActive(false);
    }
  }, [resetSilenceTimer]);

  // Stop microphone streaming
  const stopListening = useCallback(() => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
    }
    if (mediaStreamRef.current) {
      mediaStreamRef.current.getTracks().forEach((track) => track.stop());
    }
    setIsMicActive(false);
    setOrbState('idle');
  }, []);

  // Send Touch Action over WebSocket
  const sendTouchOption = useCallback((optionId: string, optionText: string) => {
    resetSilenceTimer();
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(
        JSON.stringify({
          type: 'ANSWER_TOUCH',
          option_id: optionId,
          option_text: optionText,
        })
      );
      setOrbState('processing');
    }
  }, [resetSilenceTimer]);

  return {
    orbState,
    setOrbState,
    isConnected,
    isMicActive,
    interimTranscript,
    silenceAlert,
    startListening,
    stopListening,
    sendTouchOption,
    resetSilenceTimer,
  };
}
