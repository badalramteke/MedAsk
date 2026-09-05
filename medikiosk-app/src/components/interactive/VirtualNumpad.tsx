/**
 * MediKiosk — Virtual Touch Numpad Component
 * High-contrast on-screen numpad for ABHA numbers, OTP, and phone verification.
 */

'use client';

import { Delete, Check } from 'lucide-react';
import { useSessionStore } from '@/stores/useSessionStore';
import { t } from '@/lib/i18n';

interface VirtualNumpadProps {
  onDigit: (digit: string) => void;
  onBackspace: () => void;
  onClear: () => void;
  onSubmit?: () => void;
  submitDisabled?: boolean;
}

export default function VirtualNumpad({
  onDigit,
  onBackspace,
  onClear,
  onSubmit,
  submitDisabled = false,
}: VirtualNumpadProps) {
  const language = useSessionStore((s) => s.language);
  const keys = ['1', '2', '3', '4', '5', '6', '7', '8', '9', 'C', '0', '⌫'];

  return (
    <div
      id="kiosk-virtual-numpad"
      data-element="virtual-numpad"
      data-testid="virtual-numpad"
      className="w-full max-w-sm mx-auto grid grid-cols-3 gap-3 p-4 bg-white/60 backdrop-blur-xs rounded-3xl border border-[#bdc9c5]/50 shadow-sm"
    >
      {keys.map((key) => {
        if (key === 'C') {
          return (
            <button
              key="clear"
              type="button"
              id="numpad-clear-btn"
              data-element="numpad-clear-btn"
              data-testid="numpad-clear-btn"
              onClick={onClear}
              className="h-16 rounded-2xl bg-[#eceeee] hover:bg-[#e1e3e3] text-[#aa0a17] font-bold text-base md:text-lg flex items-center justify-center active:scale-95 transition-transform cursor-pointer"
            >
              {t('numpad.clear', language) || 'CLEAR'}
            </button>
          );
        }

        if (key === '⌫') {
          return (
            <button
              key="backspace"
              type="button"
              id="numpad-backspace-btn"
              data-element="numpad-backspace-btn"
              data-testid="numpad-backspace-btn"
              onClick={onBackspace}
              className="h-16 rounded-2xl bg-[#eceeee] hover:bg-[#e1e3e3] text-[#191c1d] font-bold flex items-center justify-center active:scale-95 transition-transform cursor-pointer"
            >
              <Delete className="w-6 h-6 text-[#3e4946]" />
            </button>
          );
        }

        return (
          <button
            key={key}
            type="button"
            id={`numpad-key-${key}`}
            data-element={`numpad-key-${key}`}
            data-testid={`numpad-key-${key}`}
            onClick={() => onDigit(key)}
            className="h-16 rounded-2xl bg-[#f8fafa] hover:bg-[#005f53] hover:text-white border border-[#bdc9c5]/40 text-[#191c1d] font-bold text-2xl flex items-center justify-center shadow-xs active:scale-95 transition-all cursor-pointer"
          >
            {key}
          </button>
        );
      })}

      {onSubmit && (
        <button
          type="button"
          id="numpad-submit-btn"
          data-element="numpad-submit-btn"
          data-testid="numpad-submit-btn"
          onClick={onSubmit}
          disabled={submitDisabled}
          className={`col-span-3 h-16 rounded-2xl font-bold text-xl flex items-center justify-center gap-2 transition-all cursor-pointer shadow-md ${
            submitDisabled
              ? 'bg-[#e1e3e3] text-[#3e4946]/40 cursor-not-allowed shadow-none'
              : 'bg-[#005f53] hover:bg-[#0c6b5e] text-white active:scale-98'
          }`}
        >
          <Check className="w-6 h-6" />
          <span>Confirm / Submit</span>
        </button>
      )}
    </div>
  );
}
