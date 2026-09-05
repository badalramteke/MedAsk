/**
 * MediKiosk — In-Place Language Selector Popover
 * Allows instantaneous language switching from the header without route navigation.
 */

'use client';

import React, { useState, useRef, useEffect } from 'react';
import { useSessionStore } from '@/stores/useSessionStore';
import type { LanguageCode } from '@/lib/constants';
import { Globe, Check, ChevronDown } from 'lucide-react';

export const SUPPORTED_LANGUAGES: Array<{ code: LanguageCode; label: string; native: string }> = [
  { code: 'en', label: 'English', native: 'English' },
  { code: 'hi', label: 'Hindi', native: 'हिंदी' },
  { code: 'mr', label: 'Marathi', native: 'मराठी' },
  { code: 'bn', label: 'Bengali', native: 'বাংলা' },
  { code: 'ta', label: 'Tamil', native: 'தமிழ்' },
  { code: 'te', label: 'Telugu', native: 'తెలుగు' },
];

export default function LanguageSelectorPopover() {
  const { language, setLanguage } = useSessionStore();
  const [isOpen, setIsOpen] = useState(false);
  const popoverRef = useRef<HTMLDivElement>(null);

  const currentLang = SUPPORTED_LANGUAGES.find((l) => l.code === language) || SUPPORTED_LANGUAGES[0];

  // Close on click outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (popoverRef.current && !popoverRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen]);

  const handleSelectLanguage = (code: LanguageCode) => {
    setLanguage(code);
    setIsOpen(false);
  };

  return (
    <div className="relative inline-block text-left" ref={popoverRef}>
      <button
        type="button"
        id="kiosk-lang-indicator"
        data-element="kiosk-lang-indicator"
        data-testid="kiosk-lang-indicator"
        onClick={() => setIsOpen(!isOpen)}
        aria-expanded={isOpen}
        aria-haspopup="true"
        aria-label="Select Language"
        className="h-8 px-2.5 rounded-full bg-[#eceeee] hover:bg-[#e1e3e3] text-xs font-bold text-[#005f53] flex items-center gap-1.5 transition-all cursor-pointer border border-[#bdc9c5]/40"
      >
        <Globe className="w-3.5 h-3.5 text-[#005f53]" />
        <span className="uppercase">{currentLang.code}</span>
        <ChevronDown className={`w-3 h-3 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-1.5 w-44 rounded-xl bg-white shadow-xl border border-[#bdc9c5]/60 py-1.5 z-50 animate-in fade-in zoom-in-95 duration-100">
          <div className="px-3 py-1 text-[10px] uppercase font-bold text-[#6e7976] tracking-wider border-b border-[#bdc9c5]/30 mb-1">
            Select Language
          </div>
          {SUPPORTED_LANGUAGES.map((lang) => {
            const isSelected = language === lang.code;
            return (
              <button
                key={lang.code}
                type="button"
                onClick={() => handleSelectLanguage(lang.code)}
                className={`w-full px-3 py-2 text-left text-xs flex items-center justify-between transition-colors cursor-pointer ${
                  isSelected
                    ? 'bg-[#005f53]/10 text-[#005f53] font-bold'
                    : 'text-[#191c1d] hover:bg-[#f2f4f4]'
                }`}
              >
                <div className="flex flex-col">
                  <span className="font-semibold">{lang.native}</span>
                  <span className="text-[10px] text-[#6e7976]">{lang.label}</span>
                </div>
                {isSelected && <Check className="w-4 h-4 text-[#005f53]" />}
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}
