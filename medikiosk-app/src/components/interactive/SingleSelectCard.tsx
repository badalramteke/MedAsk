/**
 * MediKiosk — SingleSelectCard Component
 * Kiosk-optimized responsive grid of selectable options with touch & voice highlight states.
 */

'use client';

import React from 'react';
import type { QuestionOption } from '@/lib/types';
import { CheckCircle2, Circle } from 'lucide-react';

interface SingleSelectCardProps {
  options?: QuestionOption[];
  selectedValue: string | null;
  matchedVoiceOption?: string | null;
  onSelect: (code: string) => void;
  disabled?: boolean;
}

export default function SingleSelectCard({
  options = [],
  selectedValue,
  matchedVoiceOption,
  onSelect,
  disabled = false,
}: SingleSelectCardProps) {
  if (!options || options.length === 0) return null;

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 w-full">
      {options.map((option) => {
        const isSelected = selectedValue === option.value_code;
        const isVoiceMatched = matchedVoiceOption === option.value_code;

        return (
          <button
            key={option.value_code || option.option_id}
            type="button"
            disabled={disabled}
            onClick={() => onSelect(option.value_code)}
            data-element={`option-${option.value_code}`}
            data-voice-action="select"
            data-voice-param={option.value_code}
            className={`min-h-[90px] p-5 rounded-2xl text-left flex items-center justify-between transition-all duration-200 cursor-pointer active:scale-98 ${
              isSelected
                ? 'bg-[#0f7a6b] text-white shadow-lg ring-2 ring-[#005f53]'
                : isVoiceMatched
                ? 'bg-[#abffed] text-[#005f53] ring-2 ring-[#005f53] animate-pulse'
                : 'bg-white hover:bg-[#f8fafa] text-[#191c1d] border border-[#bdc9c5]/60 hover:border-[#005f53]/50 shadow-sm'
            } ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            <div className="flex flex-col pr-3">
              <span className="text-lg font-bold leading-tight">{option.text}</span>
              {option.value_code && (
                <span className={`text-xs mt-1 ${isSelected ? 'text-white/80' : 'text-[#6e7976]'}`}>
                  {option.value_code}
                </span>
              )}
            </div>

            <div className="shrink-0">
              {isSelected ? (
                <CheckCircle2 className="w-7 h-7 text-white" />
              ) : (
                <Circle className="w-7 h-7 text-[#bdc9c5]" />
              )}
            </div>
          </button>
        );
      })}
    </div>
  );
}
