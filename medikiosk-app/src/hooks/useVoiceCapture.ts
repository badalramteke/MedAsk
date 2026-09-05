/**
 * MediKiosk — Voice Capture Hook
 * Captures microphone audio using standard Web Audio API / MediaRecorder,
 * streams levels for waveform visualization, and submits to FastAPI speech endpoints.
 */

'use client';

import { useState, useRef, useCallback, useEffect } from 'react';
import { useVoiceStore } from '@/stores/useVoiceStore';
import { useSessionStore } from '@/stores/useSessionStore';
import { voiceService } from '@/services/voiceService';
import { geminiLiveClient } from '@/lib/audio/geminiLiveClient';
import { noiseSuppressor } from '@/lib/audio/rnnoiseSuppressor';

export function useVoiceCapture() {
  const { language, sessionId } = useSessionStore();
  const {
    isListening,
    setListening,
    isProcessing,
    setProcessing,
    setAudioLevel,
    setTranscript,
    setInterimTranscript,
    setVoiceAction,
    setError,
    clearTranscript,
  } = useVoiceStore();

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const animFrameRef = useRef<number | null>(null);
  const lastLevelRef = useRef<number>(0);
  const lastUpdateRef = useRef<number>(0);
  const silenceTimerRef = useRef<NodeJS.Timeout | null>(null);
  const processingTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Web Speech API recognition fallback for real-time live interim feedback
  const recognitionRef = useRef<any>(null);

  useEffect(() => {
    return () => {
      if (recognitionRef.current) {
        try {
          recognitionRef.current.onresult = null;
          recognitionRef.current.onerror = null;
          recognitionRef.current.abort();
        } catch {
          // Ignore
        }
        recognitionRef.current = null;
      }
      if (silenceTimerRef.current) clearTimeout(silenceTimerRef.current);
      if (processingTimeoutRef.current) clearTimeout(processingTimeoutRef.current);
      noiseSuppressor.destroy();
      geminiLiveClient.stopASRSession();
    };
  }, []);

  const updateAudioMeter = useCallback(() => {
    if (!analyserRef.current) return;
    const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount);
    analyserRef.current.getByteFrequencyData(dataArray);

    let sum = 0;
    for (let i = 0; i < dataArray.length; i++) {
      sum += dataArray[i];
    }
    const average = sum / dataArray.length;
    const normalized = Math.min(1, average / 128);

    // Throttle Zustand updates: max ~20 FPS (every 50ms) and only if change is notable (>0.03)
    const now = performance.now();
    if (now - lastUpdateRef.current > 50 && Math.abs(normalized - lastLevelRef.current) > 0.03) {
      lastUpdateRef.current = now;
      lastLevelRef.current = normalized;
      setAudioLevel(normalized);
    }

    animFrameRef.current = requestAnimationFrame(updateAudioMeter);
  }, [setAudioLevel]);

  const startListening = useCallback(async () => {
    try {
      setError(null);
      clearTranscript();
      audioChunksRef.current = [];

      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          channelCount: 1,
          sampleRate: 16000,
          echoCancellation: true,
          noiseSuppression: true,
        },
      });

      // 1. RNNoise / Web Audio noise suppression pipeline
      await noiseSuppressor.initialize(stream, (cleanPcmChunk) => {
        geminiLiveClient.sendAudioChunk(cleanPcmChunk);
      });

      // 2. Open Gemini Live ASR WebSocket (gemini-3.5-transcribe-live)
      geminiLiveClient.startASRSession({
        languageCode: language,
        onInterim: (text) => setInterimTranscript(text),
        onFinal: (text) => setTranscript(text),
        onError: (err) => console.warn('Gemini Live ASR note:', err),
        onClose: (code, reason) => console.log('Gemini Live ASR closed:', code, reason),
      });

      // Audio analysis for visualizer
      const audioCtx = new (window.AudioContext || (window as any).webkitAudioContext)();
      const analyser = audioCtx.createAnalyser();
      analyser.fftSize = 256;
      const source = audioCtx.createMediaStreamSource(stream);
      source.connect(analyser);

      audioContextRef.current = audioCtx;
      analyserRef.current = analyser;
      updateAudioMeter();

      // MediaRecorder for backend transcription
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
          ? 'audio/webm;codecs=opus'
          : undefined,
      });

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onerror = (e: any) => {
        console.error('MediaRecorder error event:', e);
        setError('Audio recording failed. Please try again.');
        setListening(false);
      };

      mediaRecorderRef.current = mediaRecorder;
      mediaRecorder.start(250); // 250ms chunks

      // Silence detection: check after 4.5s if patient hasn't spoken
      if (silenceTimerRef.current) clearTimeout(silenceTimerRef.current);
      silenceTimerRef.current = setTimeout(() => {
        if (lastLevelRef.current < 0.02 && isListening) {
          console.log('Silence detected; auto-stopping recording to conserve bandwidth');
          stopListening();
        }
      }, 4500);

      // Start Web Speech recognition if supported for live interim transcripts
      if (typeof window !== 'undefined' && ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)) {
        try {
          const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
          const recognition = new SpeechRecognition();
          recognition.continuous = true;
          recognition.interimResults = true;

          const langMap: Record<string, string> = {
            en: 'en-IN',
            hi: 'hi-IN',
            mr: 'mr-IN',
            bn: 'bn-IN',
            ta: 'ta-IN',
            te: 'te-IN',
          };
          recognition.lang = langMap[language] || 'en-IN';

          recognition.onresult = (event: any) => {
            let interim = '';
            let final = '';
            for (let i = event.resultIndex; i < event.results.length; ++i) {
              if (event.results[i].isFinal) {
                final += event.results[i][0].transcript;
              } else {
                interim += event.results[i][0].transcript;
              }
            }
            if (interim) setInterimTranscript(interim);
            if (final) setTranscript(final);
          };

          recognition.onerror = (recErr: any) => {
            console.warn('WebSpeech recognition event note:', recErr);
          };
          recognitionRef.current = recognition;
          recognition.start();
        } catch (e) {
          console.warn('WebSpeech init notice:', e);
        }
      }

      setListening(true);
    } catch (err: any) {
      console.error('Microphone access failed:', err);
      setError(err.message || 'Microphone access denied. Please use touch screen.');
      setListening(false);
    }
  }, [language, setError, setInterimTranscript, setListening, setTranscript, updateAudioMeter]);

  const stopListening = useCallback(async (): Promise<Blob | null> => {
    return new Promise((resolve) => {
      // Stop Gemini Live ASR session & reset noise suppressor
      geminiLiveClient.stopASRSession();
      noiseSuppressor.reset();

      if (silenceTimerRef.current) {
        clearTimeout(silenceTimerRef.current);
        silenceTimerRef.current = null;
      }

      if (!mediaRecorderRef.current || mediaRecorderRef.current.state === 'inactive') {
        setListening(false);
        resolve(null);
        return;
      }

      if (recognitionRef.current) {
        try {
          recognitionRef.current.onresult = null;
          recognitionRef.current.onerror = null;
          recognitionRef.current.stop();
        } catch {
          // Ignore
        }
        recognitionRef.current = null;
      }

      if (animFrameRef.current) {
        cancelAnimationFrame(animFrameRef.current);
      }
      if (audioContextRef.current) {
        audioContextRef.current.close().catch(() => {});
      }
      setAudioLevel(0);

      mediaRecorderRef.current.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });

        // Stop all tracks
        mediaRecorderRef.current?.stream.getTracks().forEach((track) => track.stop());
        setListening(false);
        setProcessing(true);

        // Safety hard timeout: clear processing state if backend takes > 8 seconds
        if (processingTimeoutRef.current) clearTimeout(processingTimeoutRef.current);
        processingTimeoutRef.current = setTimeout(() => {
          console.warn('Transcription timeout reached (8s); releasing processing lock');
          setProcessing(false);
        }, 8000);

        // Try backend transcription
        try {
          const res = await voiceService.transcribe(
            audioBlob,
            language,
            'webm',
            sessionId || undefined
          );
          if (res.transcript) {
            setTranscript(res.transcript);
          }
          if (res.detected_voice_action) {
            setVoiceAction(res.detected_voice_action);
          }
        } catch (err) {
          console.warn('Backend transcription fallback to local transcript:', err);
        } finally {
          if (processingTimeoutRef.current) clearTimeout(processingTimeoutRef.current);
          setProcessing(false);
        }

        resolve(audioBlob);
      };

      mediaRecorderRef.current.stop();
    });
  }, [language, sessionId, setAudioLevel, setListening, setProcessing, setTranscript, setVoiceAction]);

  return {
    isListening,
    isProcessing,
    startListening,
    stopListening,
  };
}
