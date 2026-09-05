/**
 * MediKiosk — Text-to-Speech (TTS) Hook
 * Plays vernacular voice guidance prompts via backend Bhashini TTS
 * with browser SpeechSynthesis fallback for offline / low-latency response.
 */

'use client';

import { useState, useCallback, useRef } from 'react';
import { useVoiceStore } from '@/stores/useVoiceStore';
import { useSessionStore } from '@/stores/useSessionStore';
import { voiceService } from '@/services/voiceService';

let isBackendTTSAvailable = true;
let lastBackendCheckTime = 0;

export function useTTS() {
  const language = useSessionStore((s) => s.language);
  const isSpeaking = useVoiceStore((s) => s.isSpeaking);
  const setSpeaking = useVoiceStore((s) => s.setSpeaking);
  const audioPlayerRef = useRef<HTMLAudioElement | null>(null);

  const speak = useCallback(
    async (text: string, langOverride?: string, onEnd?: () => void) => {
      const targetLang = langOverride || language;
      if (!text || typeof window === 'undefined') return;

      // Stop any ongoing speech
      stop();

      try {
        setSpeaking(true);

        // 1. Try backend synthesis via Bhashini if online and available
        const now = Date.now();
        const shouldTryBackend = isBackendTTSAvailable || (now - lastBackendCheckTime > 30000);

        if (shouldTryBackend) {
          try {
            const res = await voiceService.synthesize({
              text,
              language: targetLang,
              audio_format: 'wav',
            });

            // STRICT CHECK: Only play actual cloud/AI synthesized speech (Bhashini or Gemini).
            // NEVER play mock audio, cached fallback tones, or synthetic wave bytes.
            const provider = (res.provider_used || '').toUpperCase();
            const isMockOrFallback =
              provider.includes('MOCK') ||
              provider.includes('FALLBACK') ||
              provider.includes('CACHE') ||
              provider === 'NONE' ||
              provider === '';

            const isRealCloudAudio =
              Boolean(res.audio_base64) &&
              !isMockOrFallback &&
              (provider === 'BHASHINI' || provider === 'GEMINI_AUDIO' || provider === 'GEMINI_TTS');

            if (isRealCloudAudio) {
              isBackendTTSAvailable = true;
              const audioSrc = `data:audio/wav;base64,${res.audio_base64}`;
              const audio = new Audio(audioSrc);
              audioPlayerRef.current = audio;

              audio.onended = () => {
                setSpeaking(false);
                onEnd?.();
              };
              audio.onerror = () => {
                fallbackBrowserSpeech(text, targetLang, onEnd);
              };

              await audio.play();
              return;
            }
          } catch {
            // Backend offline or unreachable — fall back to browser Web Speech API instantly
            isBackendTTSAvailable = false;
            lastBackendCheckTime = now;
          }
        }

        // When cloud TTS is unavailable or in mock mode, use browser native SpeechSynthesis
        fallbackBrowserSpeech(text, targetLang, onEnd);
      } catch (err) {
        console.error('Speech synthesis error:', err);
        setSpeaking(false);
      }
    },
    [language, setSpeaking]
  );

  const fallbackBrowserSpeech = (text: string, lang: string, onEnd?: () => void) => {
    if (typeof window === 'undefined' || !('speechSynthesis' in window)) {
      setSpeaking(false);
      onEnd?.();
      return;
    }

    try {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      const langMap: Record<string, string> = {
        en: 'en-IN',
        hi: 'hi-IN',
        mr: 'mr-IN',
        bn: 'bn-IN',
        ta: 'ta-IN',
        te: 'te-IN',
      };
      utterance.lang = langMap[lang] || 'en-IN';
      utterance.rate = 0.95;

      utterance.onend = () => {
        setSpeaking(false);
        onEnd?.();
      };
      utterance.onerror = () => {
        setSpeaking(false);
        onEnd?.();
      };

      window.speechSynthesis.speak(utterance);
    } catch {
      setSpeaking(false);
      onEnd?.();
    }
  };

  const stop = useCallback(() => {
    if (audioPlayerRef.current) {
      audioPlayerRef.current.pause();
      audioPlayerRef.current = null;
    }
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      window.speechSynthesis.cancel();
    }
    setSpeaking(false);
  }, [setSpeaking]);

  return {
    isSpeaking,
    speak,
    stop,
  };
}
