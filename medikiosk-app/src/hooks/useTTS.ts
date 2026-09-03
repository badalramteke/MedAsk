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

export function useTTS() {
  const { language } = useSessionStore();
  const { isSpeaking, setSpeaking } = useVoiceStore();
  const audioPlayerRef = useRef<HTMLAudioElement | null>(null);

  const speak = useCallback(
    async (text: string, langOverride?: string) => {
      const targetLang = langOverride || language;
      if (!text || typeof window === 'undefined') return;

      // Stop any ongoing speech
      stop();

      try {
        setSpeaking(true);

        // 1. Try backend synthesis via Bhashini
        try {
          const res = await voiceService.synthesize({
            text,
            language: targetLang,
            audio_format: 'wav',
          });

          if (res.audio_base64) {
            const audioSrc = `data:audio/wav;base64,${res.audio_base64}`;
            const audio = new Audio(audioSrc);
            audioPlayerRef.current = audio;

            audio.onended = () => {
              setSpeaking(false);
            };
            audio.onerror = () => {
              fallbackBrowserSpeech(text, targetLang);
            };

            await audio.play();
            return;
          }
        } catch {
          // Backend synthesis failed or unreachable, fall back to browser Web Speech API
        }

        fallbackBrowserSpeech(text, targetLang);
      } catch (err) {
        console.error('Speech synthesis error:', err);
        setSpeaking(false);
      }
    },
    [language, setSpeaking]
  );

  const fallbackBrowserSpeech = (text: string, lang: string) => {
    if (!('speechSynthesis' in window)) {
      setSpeaking(false);
      return;
    }

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
    };
    utterance.onerror = () => {
      setSpeaking(false);
    };

    window.speechSynthesis.speak(utterance);
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
