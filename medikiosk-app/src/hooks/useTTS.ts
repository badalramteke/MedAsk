/**
 * MediKiosk — Text-to-Speech (TTS) Hook
 * Implements Gemini Live Native Audio Dialog (gemini-2.5-flash-native-audio-dialog)
 * with AudioContext.decodeAudioData + AudioBufferSourceNode playback (no <audio> tag)
 * for precise queuing, interruption, and multilingual Indian language accents.
 */

'use client';

import { useCallback, useRef, useEffect } from 'react';
import { useVoiceStore } from '@/stores/useVoiceStore';
import { useSessionStore } from '@/stores/useSessionStore';
import { voiceService } from '@/services/voiceService';
import { geminiLiveClient } from '@/lib/audio/geminiLiveClient';

let isBackendTTSAvailable = true;
let lastBackendCheckTime = 0;

export function useTTS() {
  const language = useSessionStore((s) => s.language);
  const isSpeaking = useVoiceStore((s) => s.isSpeaking);
  const setSpeaking = useVoiceStore((s) => s.setSpeaking);

  const audioContextRef = useRef<AudioContext | null>(null);
  const activeSourceRef = useRef<AudioBufferSourceNode | null>(null);

  const getAudioContext = useCallback(() => {
    if (!audioContextRef.current || audioContextRef.current.state === 'closed') {
      const AudioCtx = window.AudioContext || (window as any).webkitAudioContext;
      audioContextRef.current = new AudioCtx();
    }
    if (audioContextRef.current.state === 'suspended') {
      audioContextRef.current.resume().catch(() => {});
    }
    return audioContextRef.current;
  }, []);

  const stop = useCallback(() => {
    geminiLiveClient.stopTTS();

    if (activeSourceRef.current) {
      try {
        activeSourceRef.current.stop();
        activeSourceRef.current.disconnect();
      } catch (e) {
        // Source might have already ended
      }
      activeSourceRef.current = null;
    }

    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      window.speechSynthesis.cancel();
    }
    setSpeaking(false);
  }, [setSpeaking]);

  useEffect(() => {
    return () => {
      stop();
      if (audioContextRef.current && audioContextRef.current.state !== 'closed') {
        audioContextRef.current.close().catch(() => {});
        audioContextRef.current = null;
      }
    };
  }, [stop]);

  const speak = useCallback(
    async (text: string, langOverride?: string, onEnd?: () => void) => {
      const targetLang = langOverride || language;
      if (!text || typeof window === 'undefined') return;

      // 1. Audio interrupt: on new question load or speech command, stop previous audio immediately
      stop();

      try {
        setSpeaking(true);
        const ctx = getAudioContext();

        // 2. Primary: Gemini Live API WebSocket (gemini-2.5-flash-native-audio-dialog)
        if (geminiLiveClient.hasApiKey()) {
          const played = await geminiLiveClient.playTTSDialog(
            {
              languageCode: targetLang,
              text,
              onStart: () => setSpeaking(true),
              onEnd: () => {
                setSpeaking(false);
                onEnd?.();
              },
              onError: () => {
                console.warn('Gemini Live TTS notice, falling back to Web Speech / Bhashini');
              },
            },
            ctx,
            (sourceNode) => {
              activeSourceRef.current = sourceNode;
            }
          );

          if (played) return;
        }

        // 3. Secondary: Backend Bhashini cloud synthesis (decoded via AudioContext, NO <audio> tag)
        const now = Date.now();
        const shouldTryBackend = isBackendTTSAvailable || now - lastBackendCheckTime > 30000;

        if (shouldTryBackend) {
          try {
            const res = await voiceService.synthesize({
              text,
              language: targetLang,
              audio_format: 'wav',
            });

            const provider = (res.provider_used || '').toUpperCase();
            const isRealCloudAudio =
              Boolean(res.audio_base64) &&
              !provider.includes('MOCK') &&
              !provider.includes('FALLBACK') &&
              (provider === 'BHASHINI' || provider === 'GEMINI_AUDIO' || provider === 'GEMINI_TTS');

            if (isRealCloudAudio && res.audio_base64) {
              isBackendTTSAvailable = true;
              const binaryString = atob(res.audio_base64);
              const len = binaryString.length;
              const bytes = new Uint8Array(len);
              for (let i = 0; i < len; i++) {
                bytes[i] = binaryString.charCodeAt(i);
              }

              const audioBuffer = await ctx.decodeAudioData(bytes.buffer);
              const source = ctx.createBufferSource();
              source.buffer = audioBuffer;
              source.connect(ctx.destination);
              activeSourceRef.current = source;

              source.onended = () => {
                setSpeaking(false);
                activeSourceRef.current = null;
                onEnd?.();
              };

              source.start(0);
              return;
            }
          } catch {
            isBackendTTSAvailable = false;
            lastBackendCheckTime = now;
          }
        }

        // 4. Low-latency client Web Speech API fallback
        fallbackBrowserSpeech(text, targetLang, onEnd);
      } catch (err) {
        console.error('Speech synthesis error:', err);
        setSpeaking(false);
      }
    },
    [getAudioContext, language, setSpeaking, stop]
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

  return {
    isSpeaking,
    speak,
    stop,
  };
}
