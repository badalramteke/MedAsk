/**
 * MediKiosk — Kiosk Footer Component
 * Persistent navigation bar with Back, Voice/Touch Indicator, and Next/Continue.
 */

'use client';

import { useSessionStore } from '@/stores/useSessionStore';
import { useVoiceStore } from '@/stores/useVoiceStore';
import { t } from '@/lib/i18n';
import { ArrowLeft, ArrowRight, Mic, Touchpad } from 'lucide-react';

interface KioskFooterProps {
  onNext?: () => void;
  onBack?: () => void;
  nextText?: string;
  backText?: string;
  nextDisabled?: boolean;
  hideBack?: boolean;
  hideNext?: boolean;
}

export default function KioskFooter({
  onNext,
  onBack,
  nextText,
  backText,
  nextDisabled = false,
  hideBack = false,
  hideNext = false,
}: KioskFooterProps) {
  const { language } = useSessionStore();
  const { isListening } = useVoiceStore();

  return (
    <footer
      id="kiosk-footer"
      data-element="kiosk-footer"
      data-testid="kiosk-footer"
      className="h-24 md:h-28 w-full bg-white/90 backdrop-blur-md border-t border-[#bdc9c5]/30 px-6 md:px-12 flex items-center justify-between flex-shrink-0 z-40"
    >
      {/* Left: Back Button */}
      <div>
        {!hideBack && (
          <button
            id="kiosk-footer-back-btn"
            data-element="kiosk-footer-back-btn"
            data-voice-action="navigate-back"
            data-testid="kiosk-footer-back-btn"
            aria-label="Go to previous screen"
            onClick={onBack}
            className="h-14 md:h-16 px-6 md:px-8 rounded-full border-2 border-[#bdc9c5] hover:bg-[#eceeee] text-[#191c1d] font-bold text-lg flex items-center gap-3 active:scale-95 transition-all cursor-pointer"
          >
            <ArrowLeft className="w-6 h-6 text-[#3e4946]" />
            <span>{backText || t('nav.back', language)}</span>
          </button>
        )}
      </div>

      {/* Center: Dual-Mode Voice & Touch Parity Indicator */}
      <div className="hidden sm:flex items-center gap-2 px-4 py-2 rounded-full bg-[#f2f4f4] border border-[#bdc9c5]/40 text-xs font-semibold text-[#3e4946]">
        <div className="flex items-center gap-1.5">
          <Touchpad className="w-4 h-4 text-[#005f53]" />
          <span>Touch</span>
        </div>
        <span className="text-[#bdc9c5]">•</span>
        <div className="flex items-center gap-1.5">
          <Mic className={`w-4 h-4 ${isListening ? 'text-[#aa0a17] animate-pulse' : 'text-[#005f53]'}`} />
          <span>{isListening ? 'Listening' : 'Voice Active'}</span>
        </div>
      </div>

      {/* Right: Next / Proceed Button */}
      <div>
        {!hideNext && (
          <button
            id="kiosk-footer-next-btn"
            data-element="kiosk-footer-next-btn"
            data-voice-action="navigate-next"
            data-testid="kiosk-footer-next-btn"
            aria-label="Proceed to next step"
            onClick={onNext}
            disabled={nextDisabled}
            className={`h-14 md:h-16 px-8 md:px-12 rounded-full font-bold text-lg md:text-xl flex items-center gap-3 shadow-lg active:scale-95 transition-all cursor-pointer ${
              nextDisabled
                ? 'bg-[#e1e3e3] text-[#3e4946]/50 cursor-not-allowed shadow-none'
                : 'bg-[#005f53] hover:bg-[#0c6b5e] text-white shadow-[#005f53]/30 hover:shadow-[#005f53]/40'
            }`}
          >
            <span>{nextText || t('nav.continue', language)}</span>
            <ArrowRight className="w-6 h-6" />
          </button>
        )}
      </div>
    </footer>
  );
}
