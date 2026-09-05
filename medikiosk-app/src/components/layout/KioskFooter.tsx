/**
 * MediKiosk — Kiosk Footer Component
 * Streamlined navigation bar (≤ 64px) with prominent center-bottom floating action
 * microphone button (56–72px), clear visual feedback states (Idle/Recording/Processing),
 * and minimal essential navigation controls.
 */

'use client';

import { useSessionStore } from '@/stores/useSessionStore';
import { useVoiceStore } from '@/stores/useVoiceStore';
import { useVoiceCapture } from '@/hooks/useVoiceCapture';
import { t } from '@/lib/i18n';
import { ArrowLeft, ArrowRight, Mic, MicOff, Loader2 } from 'lucide-react';

interface KioskFooterProps {
  onNext?: () => void;
  onBack?: () => void;
  nextText?: string;
  backText?: string;
  nextDisabled?: boolean;
  hideBack?: boolean;
  hideNext?: boolean;
  showMic?: boolean;
  onTranscriptReady?: (transcript: string) => void;
}

export default function KioskFooter({
  onNext,
  onBack,
  nextText,
  backText,
  nextDisabled = false,
  hideBack = false,
  hideNext = false,
  showMic = true,
  onTranscriptReady,
}: KioskFooterProps) {
  const language = useSessionStore((s) => s.language);
  const { isListening, isProcessing, transcript } = useVoiceStore();
  const { startListening, stopListening } = useVoiceCapture();

  const handleToggleMic = async () => {
    if (isProcessing) return;
    if (isListening) {
      const blob = await stopListening();
      if (transcript && onTranscriptReady) {
        onTranscriptReady(transcript);
      }
    } else {
      await startListening();
    }
  };

  return (
    <footer
      id="kiosk-footer"
      data-element="kiosk-footer"
      data-testid="kiosk-footer"
      className="relative h-16 w-full bg-white/95 backdrop-blur-md border-t border-[#bdc9c5]/40 px-4 md:px-8 flex items-center justify-between flex-shrink-0 z-40"
    >
      {/* Left: Back Button */}
      <div className="z-10">
        {!hideBack && (
          <button
            id="kiosk-footer-back-btn"
            data-element="kiosk-footer-back-btn"
            data-voice-action="navigate-back"
            data-testid="kiosk-footer-back-btn"
            aria-label="Go to previous screen"
            onClick={onBack}
            className="h-10 px-4 md:px-5 rounded-full border border-[#bdc9c5] hover:bg-[#eceeee] text-[#191c1d] font-bold text-xs md:text-sm flex items-center gap-2 active:scale-95 transition-all cursor-pointer"
          >
            <ArrowLeft className="w-4 h-4 text-[#3e4946]" />
            <span>{backText || t('nav.back', language)}</span>
          </button>
        )}
      </div>

      {/* Center: Prominent Floating Action Microphone Button (64px diameter, z-50) */}
      {showMic && (
        <div className="absolute left-1/2 -top-5 -translate-x-1/2 z-50 flex flex-col items-center pointer-events-auto">
          <div className="relative flex items-center justify-center">
            {/* Pulsing outer ring animation while recording */}
            {isListening && (
              <span className="absolute -inset-2 rounded-full bg-[#aa0a17]/30 animate-ping pointer-events-none" />
            )}

            <button
              id="kiosk-floating-mic-btn"
              data-element="floating-mic-btn"
              data-voice-action={isListening ? 'stop-recording' : 'start-recording'}
              data-testid="floating-mic-btn"
              aria-label={
                isProcessing
                  ? 'Processing Speech...'
                  : isListening
                  ? 'Stop Recording'
                  : 'Tap to Speak'
              }
              disabled={isProcessing}
              onClick={handleToggleMic}
              className={`w-16 h-16 rounded-full flex items-center justify-center shadow-xl active:scale-95 transition-all cursor-pointer ${
                isProcessing
                  ? 'bg-[#0f7a6b] text-white ring-4 ring-[#0f7a6b]/30 cursor-wait'
                  : isListening
                  ? 'bg-[#aa0a17] text-white ring-4 ring-[#aa0a17]/40 animate-pulse shadow-[#aa0a17]/40'
                  : 'bg-[#005f53] hover:bg-[#0c6b5e] text-white ring-4 ring-white shadow-[#005f53]/30 hover:scale-105'
              }`}
            >
              {isProcessing ? (
                <Loader2 className="w-7 h-7 text-white animate-spin" />
              ) : isListening ? (
                <MicOff className="w-7 h-7 text-white" />
              ) : (
                <Mic className="w-7 h-7 text-white" />
              )}
            </button>
          </div>

          {/* Micro-label beneath the mic button */}
          <span className="text-[10px] font-bold text-[#3e4946] bg-white/95 px-2 py-0.5 rounded-full shadow-xs mt-0.5 whitespace-nowrap border border-[#bdc9c5]/30">
            {isProcessing
              ? (language === 'hi' ? 'प्रोसेसिंग...' : 'Processing...')
              : isListening
              ? (language === 'hi' ? 'सुन रहे हैं...' : 'Listening...')
              : (language === 'hi' ? 'बोलने के लिए दबाएं' : 'Tap to speak')}
          </span>
        </div>
      )}

      {/* Right: Next / Proceed Button */}
      <div className="z-10">
        {!hideNext && (
          <button
            id="kiosk-footer-next-btn"
            data-element="kiosk-footer-next-btn"
            data-voice-action="navigate-next"
            data-testid="kiosk-footer-next-btn"
            aria-label="Proceed to next step"
            onClick={onNext}
            disabled={nextDisabled}
            className={`h-10 px-5 md:px-7 rounded-full font-bold text-xs md:text-sm flex items-center gap-2 shadow-md active:scale-95 transition-all cursor-pointer ${
              nextDisabled
                ? 'bg-[#e1e3e3] text-[#3e4946]/50 cursor-not-allowed shadow-none'
                : 'bg-[#005f53] hover:bg-[#0c6b5e] text-white shadow-[#005f53]/25 hover:shadow-[#005f53]/35'
            }`}
          >
            <span>{nextText || t('nav.continue', language)}</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        )}
      </div>
    </footer>
  );
}
