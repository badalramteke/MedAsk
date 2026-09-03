/**
 * MediKiosk — Kiosk Header Component
 * Persistent top bar with Hospital logo, current time, and Emergency SOS button.
 * Adheres to PATHS.md mandatory data-* attributes.
 */

'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useSessionStore } from '@/stores/useSessionStore';
import { useFlowStore } from '@/stores/useFlowStore';
import { t } from '@/lib/i18n';
import { ArrowLeft, Stethoscope, AlertTriangle, Globe } from 'lucide-react';

interface KioskHeaderProps {
  showBack?: boolean;
  onBack?: () => void;
}

export default function KioskHeader({ showBack = true, onBack }: KioskHeaderProps) {
  const router = useRouter();
  const { language, triggerEmergency } = useSessionStore();
  const { getPreviousRoute, currentScreenId } = useFlowStore();
  const [timeStr, setTimeStr] = useState('');

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setTimeStr(
        now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      );
    };
    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  const handleBack = () => {
    if (onBack) {
      onBack();
    } else {
      const prevRoute = getPreviousRoute();
      router.push(prevRoute);
    }
  };

  const handleSos = () => {
    triggerEmergency('Manual SOS Triggered by Patient at Kiosk');
    router.push('/triage/alert');
  };

  const isLanding = currentScreenId === 'welcome_gate';

  return (
    <header
      id="kiosk-header"
      data-element="kiosk-header"
      data-testid="kiosk-header"
      className="h-20 md:h-24 w-full bg-[#f8fafa] border-b border-[#bdc9c5]/40 px-6 md:px-10 flex items-center justify-between flex-shrink-0 z-40"
    >
      {/* Left: Back button + Brand */}
      <div className="flex items-center gap-4">
        {showBack && !isLanding && (
          <button
            id="kiosk-back-btn"
            data-element="kiosk-back-btn"
            data-voice-action="navigate-back"
            data-testid="kiosk-back-btn"
            aria-label="Go Back"
            onClick={handleBack}
            className="w-12 h-12 rounded-full bg-[#eceeee] hover:bg-[#e1e3e3] active:scale-95 flex items-center justify-center text-[#191c1d] transition-all cursor-pointer"
          >
            <ArrowLeft className="w-6 h-6 text-[#005f53]" />
          </button>
        )}

        <div className="w-12 h-12 rounded-xl bg-[#0f7a6b] flex items-center justify-center shadow-sm">
          <Stethoscope className="w-7 h-7 text-white" />
        </div>

        <div className="flex flex-col">
          <div className="flex items-center gap-2">
            <span className="text-2xl font-bold tracking-tight text-[#005f53]">
              MediKiosk
            </span>
            <span className="text-xs px-2 py-0.5 rounded-full bg-[#005f53]/10 text-[#005f53] font-semibold">
              AI OPD
            </span>
          </div>
          <span className="text-xs text-[#3e4946]">
            {t('header.hospital', language)}
          </span>
        </div>

        <div className="hidden sm:block h-8 w-px bg-[#bdc9c5]/60 mx-2" />
        <span className="hidden sm:inline-block text-lg font-semibold text-[#3e4946]">
          {timeStr}
        </span>
      </div>

      {/* Right: Language Pill + SOS Assist */}
      <div className="flex items-center gap-3">
        <button
          id="kiosk-lang-indicator"
          data-element="kiosk-lang-indicator"
          data-testid="kiosk-lang-indicator"
          onClick={() => router.push('/language')}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-[#eceeee] text-xs font-semibold text-[#005f53] hover:bg-[#e1e3e3] transition-colors cursor-pointer"
        >
          <Globe className="w-3.5 h-3.5" />
          <span className="uppercase">{language}</span>
        </button>

        <button
          id="kiosk-sos-btn"
          data-element="triage-sos-call-btn"
          data-voice-action="call-nurse"
          data-testid="kiosk-sos-btn"
          aria-label="Emergency SOS Staff Assistance"
          onClick={handleSos}
          className="h-12 md:h-14 px-5 md:px-7 rounded-full bg-[#aa0a17] hover:bg-[#8e0813] text-white flex items-center gap-2.5 shadow-md active:scale-95 transition-all cursor-pointer font-bold tracking-wide text-sm md:text-base"
        >
          <AlertTriangle className="w-5 h-5 text-white animate-bounce" />
          <span>{t('header.sos', language)}</span>
        </button>
      </div>
    </header>
  );
}
