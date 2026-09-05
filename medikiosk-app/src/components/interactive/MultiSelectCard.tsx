/**
 * MediKiosk — MultiSelectCard Component
 * Kiosk-optimized multi-select option grid with clear confirmation action.
 */

'use client';

import React from 'react';
import type { QuestionOption } from '@/lib/types';
import { CheckSquare, Square, ArrowRight } from 'lucide-react';

interface MultiSelectCardProps {
  options?: QuestionOption[];
  selectedValues: string[];
  onToggle: (code: string) => void;
  onConfirm: () => void;
  disabled?: boolean;
}

export default function MultiSelectCard({
  options = [],
  selectedValues = [],
  onToggle,
  onConfirm,
  disabled = false,
}: MultiSelectCardProps) {
  if (!options || options.length === 0) return null;

  return (
    <div className="flex flex-col gap-5 w-full">
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 w-full">
        {options.map((option) => {
          const isSelected = selectedValues.includes(option.value_code);

          return (
            <button
              key={option.value_code || option.option_id}
              type="button"
              disabled={disabled}
              onClick={() => onToggle(option.value_code)}
              data-element={`multi-option-${option.value_code}`}
              data-voice-action="toggle"
              data-voice-param={option.value_code}
              className={`min-h-[90px] p-5 rounded-2xl text-left flex items-center justify-between transition-all duration-200 cursor-pointer active:scale-98 ${
                isSelected
                  ? 'bg-[#0f7a6b] text-white shadow-lg ring-2 ring-[#005f53]'
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
                  <CheckSquare className="w-7 h-7 text-white" />
                ) : (
                  <Square className="w-7 h-7 text-[#bdc9c5]" />
                )}
              </div>
            </button>
          );
        })}
      </div>

      <button
        type="button"
        disabled={disabled || selectedValues.length === 0}
        onClick={onConfirm}
        className="w-full h-16 rounded-2xl bg-[#005f53] hover:bg-[#0f7a6b] text-white font-bold text-lg flex items-center justify-center gap-3 shadow-md active:scale-98 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <span>Confirm Choices ({selectedValues.length} selected)</span>
        <ArrowRight className="w-6 h-6" />
      </button>
    </div>
  );
}
