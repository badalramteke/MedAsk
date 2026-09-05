/**
 * MediKiosk — Voice Orb & Speech Visualizer Component
 * Massive floating/inline push-to-talk microphone with real-time waveform bars,
 * speech state animations (pure CSS), and live transcript display.
 */

'use client';

import { useVoiceStore } from '@/stores/useVoiceStore';
import { useVoiceCapture } from '@/hooks/useVoiceCapture';
import { useTTS } from '@/hooks/useTTS';
import { Mic, MicOff, Volume2 } from 'lucide-react';

interface VoiceOrbProps {
  promptText?: string;
  onTranscriptReady?: (transcript: string) => void;
  inline?: boolean;
}

export default function VoiceOrb({
  promptText,
  onTranscriptReady,
  inline = false,
}: VoiceOrbProps) {
  const {
    isListening,
    isSpeaking,
    audioLevel,
    transcript,
    interimTranscript,
  } = useVoiceStore();

  const { startListening, stopListening } = useVoiceCapture();
  const { speak } = useTTS();

  const handleToggleMic = async () => {
    if (isListening) {
      const blob = await stopListening();
      if (transcript && onTranscriptReady) {
        onTranscriptReady(transcript);
      }
    } else {
      await startListening();
    }
  };

  const handleReplayPrompt = () => {
    if (promptText) {
      speak(promptText);
    }
  };

  const activeTranscript = interimTranscript || transcript;

  return (
    <div
      id="kiosk-voice-orb-container"
      data-element="voice-orb-container"
      data-testid="voice-orb-container"
      className={`flex flex-col items-center justify-center gap-4 ${
        inline ? 'w-full my-4' : 'w-full'
      }`}
    >
      {/* Transcript or Guidance Bubble */}
      {activeTranscript ? (
        <div className="max-w-xl px-6 py-3 rounded-2xl bg-white/90 border border-[#005f53]/30 shadow-md flex items-center gap-3 animate-fade-in-up">
          <div className="w-2.5 h-2.5 rounded-full bg-[#005f53] animate-ping" />
          <p className="text-base font-medium text-[#191c1d] italic">
            &ldquo;{activeTranscript}&rdquo;
          </p>
        </div>
      ) : promptText ? (
        <div className="flex items-center gap-2">
          <button
            id="kiosk-replay-audio-btn"
            data-element="help-audio-btn"
            data-voice-action="play-question-audio"
            data-testid="replay-audio-btn"
            aria-label="Replay audio prompt"
            onClick={handleReplayPrompt}
            className="flex items-center gap-2 px-4 py-2 rounded-full bg-[#eceeee] hover:bg-[#e1e3e3] text-[#005f53] text-sm font-semibold transition-all cursor-pointer shadow-sm active:scale-95"
          >
            <Volume2 className={`w-4 h-4 ${isSpeaking ? 'animate-bounce text-[#0f7a6b]' : ''}`} />
            <span>{isSpeaking ? 'Speaking...' : 'Listen Again'}</span>
          </button>
        </div>
      ) : null}

      {/* Center: Push-to-Talk Microphone Orb */}
      <div className="relative flex items-center justify-center">
        {/* Glowing pulsing aura when recording */}
        {isListening && (
          <div
            className="absolute inset-0 rounded-full bg-[#0f7a6b]/25 animate-ping"
            style={{ transform: `scale(${1 + audioLevel * 0.8})` }}
          />
        )}

        <button
          id="kiosk-mic-btn"
          data-element="mic-record-btn"
          data-voice-action={isListening ? 'stop-recording' : 'start-recording'}
          data-testid="mic-record-btn"
          aria-label={isListening ? 'Stop Recording' : 'Start Recording — Speak Now'}
          onClick={handleToggleMic}
          className={`relative z-10 w-20 h-20 md:w-24 md:h-24 rounded-full flex items-center justify-center shadow-xl active:scale-95 transition-all cursor-pointer ${
            isListening
              ? 'bg-[#aa0a17] text-white shadow-[#aa0a17]/40 ring-4 ring-[#aa0a17]/30'
              : 'bg-[#0f7a6b] hover:bg-[#005f53] text-white shadow-[#0f7a6b]/40 ring-4 ring-[#0f7a6b]/20 hover:scale-105'
          }`}
        >
          {isListening ? (
            <MicOff className="w-9 h-9 md:w-11 md:h-11 animate-pulse" />
          ) : (
            <Mic className="w-9 h-9 md:w-11 md:h-11" />
          )}
        </button>
      </div>

      {/* Waveform Bars (CSS-animated height according to audioLevel) */}
      <div className="flex items-center justify-center gap-1.5 h-8">
        {[1, 2, 3, 4, 5, 6, 7].map((bar, i) => {
          const height = isListening
            ? Math.max(6, Math.min(32, (audioLevel * 36) * ((i % 3) + 0.6)))
            : 6;

          return (
            <div
              key={bar}
              className={`w-1.5 rounded-full transition-all duration-100 ${
                isListening ? 'bg-[#005f53]' : 'bg-[#bdc9c5]/50'
              }`}
              style={{ height: `${height}px` }}
            />
          );
        })}
      </div>

      <span className="text-xs font-semibold text-[#3e4946]">
        {isListening ? 'Listening... Tap to finish' : 'Tap to speak your answer'}
      </span>
    </div>
  );
}
