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
import { ArrowLeft } from 'lucide-react';
import { HealthStethoscope, Ambulance } from '@/components/icons/ClinicalIcon';
import LanguageSelectorPopover from './LanguageSelectorPopover';

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
      className="h-12 w-full bg-[#f8fafa] border-b border-[#bdc9c5]/40 px-4 md:px-6 flex items-center justify-between flex-shrink-0 z-40"
    >
      {/* Left: Back button + Brand */}
      <div className="flex items-center gap-3">
        {showBack && !isLanding && (
          <button
            id="kiosk-back-btn"
            data-element="kiosk-back-btn"
            data-voice-action="navigate-back"
            data-testid="kiosk-back-btn"
            aria-label="Go Back"
            onClick={handleBack}
            className="w-8 h-8 rounded-full bg-[#eceeee] hover:bg-[#e1e3e3] active:scale-95 flex items-center justify-center text-[#005f53] transition-all cursor-pointer"
          >
            <ArrowLeft className="w-4 h-4" />
          </button>
        )}

        <div className="w-8 h-8 rounded-lg bg-[#005f53] flex items-center justify-center shadow-xs">
          <HealthStethoscope className="w-5 h-5 text-white" />
        </div>

        <div className="flex items-center gap-2">
          <span className="text-lg font-bold tracking-tight text-[#005f53]">
            MediKiosk
          </span>
          <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-[#005f53]/10 text-[#005f53] font-semibold">
            AI OPD
          </span>
        </div>

        <span className="hidden sm:inline-block text-xs font-semibold text-[#6e7976] ml-2">
          {timeStr}
        </span>
      </div>

      {/* Right: In-Place Language Selector Popover + SOS Assist */}
      <div className="flex items-center gap-2.5">
        <LanguageSelectorPopover />

        <button
          id="kiosk-sos-btn"
          data-element="triage-sos-call-btn"
          data-voice-action="call-nurse"
          data-testid="kiosk-sos-btn"
          aria-label="Emergency SOS Staff Assistance"
          onClick={handleSos}
          className="h-8 px-3 rounded-full bg-[#aa0a17] hover:bg-[#8e0813] text-white flex items-center gap-1.5 shadow-sm active:scale-95 transition-all cursor-pointer font-bold text-xs"
        >
          <Ambulance className="w-3.5 h-3.5 text-white animate-bounce" />
          <span>{t('header.sos', language)}</span>
        </button>
      </div>
    </header>
  );
}
