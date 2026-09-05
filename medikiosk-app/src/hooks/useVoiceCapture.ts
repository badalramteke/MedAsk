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

export function useVoiceCapture() {
  const { language, sessionId } = useSessionStore();
  const {
    isListening,
    setListening,
    setAudioLevel,
    setTranscript,
    setInterimTranscript,
    setVoiceAction,
    setError,
  } = useVoiceStore();

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const animFrameRef = useRef<number | null>(null);

  // Web Speech API recognition fallback for real-time live interim feedback
  const recognitionRef = useRef<any>(null);

  useEffect(() => {
    if (typeof window !== 'undefined' && ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)) {
      const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
      const recognition = new SpeechRecognition();
      recognition.continuous = true;
      recognition.interimResults = true;

      // Map language code to BCP 47
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

      recognition.onerror = (event: any) => {
        console.warn('Speech recognition warning:', event.error);
      };

      recognitionRef.current = recognition;
    }

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.abort();
      }
    };
  }, [language, setInterimTranscript, setTranscript]);

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
    setAudioLevel(normalized);

    animFrameRef.current = requestAnimationFrame(updateAudioMeter);
  }, [setAudioLevel]);

  const startListening = useCallback(async () => {
    try {
      setError(null);
      audioChunksRef.current = [];

      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          channelCount: 1,
          sampleRate: 16000,
          echoCancellation: true,
          noiseSuppression: true,
        },
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

      mediaRecorderRef.current = mediaRecorder;
      mediaRecorder.start(250); // 250ms chunks

      // Start Web Speech recognition if supported
      if (recognitionRef.current) {
        try {
          recognitionRef.current.start();
        } catch {
          // Ignore already started error
        }
      }

      setListening(true);
    } catch (err: any) {
      console.error('Microphone access failed:', err);
      setError(err.message || 'Microphone access denied. Please use touch screen.');
      setListening(false);
    }
  }, [setError, setListening, updateAudioMeter]);

  const stopListening = useCallback(async (): Promise<Blob | null> => {
    return new Promise((resolve) => {
      if (!mediaRecorderRef.current || mediaRecorderRef.current.state === 'inactive') {
        setListening(false);
        resolve(null);
        return;
      }

      if (recognitionRef.current) {
        try {
          recognitionRef.current.stop();
        } catch {
          // Ignore
        }
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
        }

        resolve(audioBlob);
      };

      mediaRecorderRef.current.stop();
    });
  }, [language, sessionId, setAudioLevel, setListening, setTranscript, setVoiceAction]);

  return {
    isListening,
    startListening,
    stopListening,
  };
}
