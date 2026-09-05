/**
 * Hook: useVoiceSession
 * Manages WebSocket streaming connection, 250ms audio chunking,
 * incoming question dispatch, and audio speech synthesis.
 */

'use client';

import { useState, useEffect, useRef, useCallback } from 'react';

export interface VoiceSessionOptions {
  sessionId?: string;
  language?: string;
  onQuestionReceived?: (data: { text: string; textEnglish?: string; options?: string[]; section?: string; progress?: number }) => void;
  onRedFlagDetected?: (alert: any) => void;
  onTranscript?: (text: string) => void;
  onSessionComplete?: () => void;
}

export function useVoiceSession({
  sessionId,
  language = 'hi',
  onQuestionReceived,
  onRedFlagDetected,
  onTranscript,
  onSessionComplete,
}: VoiceSessionOptions) {
  const [isConnected, setIsConnected] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [audioLevel, setAudioLevel] = useState(0);
  const [orbState, setOrbState] = useState<'idle' | 'listening' | 'processing' | 'speaking' | 'command-matched' | 'command-failed' | 'red_flag' | 'paused'>('idle');

  const wsRef = useRef<WebSocket | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const animFrameRef = useRef<number | null>(null);

  // 1. Connect WebSocket
  useEffect(() => {
    if (!sessionId) return;

    const wsUrl =
      process.env.NEXT_PUBLIC_MODULE_A_WS_URL ||
      `ws://localhost:8000/api/v1/module-a/session/${sessionId}/stream`;
    let ws: WebSocket;

    try {
      ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        setIsConnected(true);
        setOrbState('listening');
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === 'question') {
            setOrbState('speaking');
            if (onQuestionReceived) {
              onQuestionReceived({
                text: data.text,
                textEnglish: data.text_english,
                options: data.options,
                section: data.section,
                progress: data.progress,
              });
            }
            speakText(data.text, language, () => setOrbState('listening'));
          } else if (data.type === 'stt_final') {
            setOrbState('processing');
            if (onTranscript) onTranscript(data.text);
          } else if (data.type === 'red_flag') {
            setOrbState('red_flag');
            if (onRedFlagDetected) onRedFlagDetected(data.alert);
          } else if (data.type === 'session_complete') {
            setOrbState('idle');
            if (onSessionComplete) onSessionComplete();
          }
        } catch {
          // ignore parsing error
        }
      };

      ws.onclose = () => setIsConnected(false);
      ws.onerror = () => setIsConnected(false);
    } catch {
      setIsConnected(false);
    }

    return () => {
      if (wsRef.current) wsRef.current.close();
    };
  }, [sessionId, language]);

  // 2. Synthesize speech via Web Speech API
  const speakText = useCallback((text: string, lang: string, onEnd?: () => void) => {
    if (typeof window === 'undefined' || !window.speechSynthesis || !text) {
      if (onEnd) onEnd();
      return;
    }

    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = lang === 'hi' ? 'hi-IN' : lang === 'mr' ? 'mr-IN' : lang === 'te' ? 'te-IN' : lang === 'ta' ? 'ta-IN' : 'en-IN';
    utterance.rate = 0.92;

    utterance.onend = () => {
      if (onEnd) onEnd();
    };
    utterance.onerror = () => {
      if (onEnd) onEnd();
    };

    window.speechSynthesis.speak(utterance);
  }, []);

  // 3. Audio Streaming (250ms chunks)
  const startRecording = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const audioCtx = new (window.AudioContext || (window as any).webkitAudioContext)();
      audioContextRef.current = audioCtx;
      const source = audioCtx.createMediaStreamSource(stream);
      const analyser = audioCtx.createAnalyser();
      analyser.fftSize = 64;
      source.connect(analyser);
      analyserRef.current = analyser;

      // Monitor volume level
      const updateLevel = () => {
        const dataArr = new Uint8Array(analyser.frequencyBinCount);
        analyser.getByteFrequencyData(dataArr);
        const avg = dataArr.reduce((a, b) => a + b, 0) / dataArr.length;
        setAudioLevel(Math.min(1, avg / 128));
        animFrameRef.current = requestAnimationFrame(updateLevel);
      };
      updateLevel();

      const mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });
      mediaRecorderRef.current = mediaRecorder;

      mediaRecorder.ondataavailable = async (event) => {
        if (event.data && event.data.size > 0 && wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
          const reader = new FileReader();
          reader.onloadend = () => {
            const base64Audio = (reader.result as string).split(',')[1];
            wsRef.current?.send(JSON.stringify({
              type: 'audio_chunk',
              payload: base64Audio,
              mime: 'audio/webm',
            }));
          };
          reader.readAsDataURL(event.data);
        }
      };

      mediaRecorder.start(250); // 250ms interval
      setIsRecording(true);
      setOrbState('listening');
    } catch (e) {
      console.warn('Microphone permission blocked or unavailable:', e);
    }
  }, []);

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
    }
    if (animFrameRef.current) cancelAnimationFrame(animFrameRef.current);
    if (audioContextRef.current) audioContextRef.current.close();
    setIsRecording(false);
    setOrbState('processing');
  }, []);

  return {
    isConnected,
    isRecording,
    audioLevel,
    orbState,
    setOrbState,
    startRecording,
    stopRecording,
    speakText,
  };
}
