/**
 * MediKiosk — Option Card Component
 * Touch-optimized choice card with high contrast, icon, title, subtitle,
 * audio preview icon, and selected state.
 */

'use client';

import React from 'react';
import { CheckCircle2, Volume2 } from 'lucide-react';

interface OptionCardProps {
  id: string;
  title: string;
  subtitle?: string;
  icon?: React.ReactNode;
  selected?: boolean;
  onSelect: () => void;
  onAudioSample?: () => void;
  dataElement?: string;
  dataVoiceAction?: string;
  badge?: string;
}

export default function OptionCard({
  id,
  title,
  subtitle,
  icon,
  selected = false,
  onSelect,
  onAudioSample,
  dataElement,
  dataVoiceAction,
  badge,
}: OptionCardProps) {
  return (
    <button
      id={id}
      type="button"
      data-element={dataElement || `option-card-${id}`}
      data-voice-action={dataVoiceAction || `select-${id}`}
      data-testid={`option-card-${id}`}
      aria-pressed={selected}
      onClick={onSelect}
      className={`w-full min-h-[140px] md:min-h-[160px] p-6 rounded-3xl text-left flex flex-col justify-between transition-all duration-200 cursor-pointer active:scale-98 ${
        selected
          ? 'bg-[#0f7a6b] text-white shadow-xl ring-2 ring-[#005f53] scale-[1.02]'
          : 'bg-white hover:bg-[#f8fafa] text-[#191c1d] border border-[#bdc9c5]/60 hover:border-[#005f53]/50 shadow-sm hover:shadow-md'
      }`}
    >
      {/* Top row: Icon + Audio Button / Checkmark */}
      <div className="flex items-center justify-between w-full">
        <div
          className={`w-12 h-12 rounded-2xl flex items-center justify-center transition-colors ${
            selected
              ? 'bg-white/20 text-white'
              : 'bg-[#eceeee] text-[#005f53]'
          }`}
        >
          {icon}
        </div>

        <div className="flex items-center gap-2">
          {onAudioSample && (
            <div
              role="button"
              tabIndex={0}
              aria-label={`Listen to ${title}`}
              onClick={(e) => {
                e.stopPropagation();
                onAudioSample();
              }}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.stopPropagation();
                  onAudioSample();
                }
              }}
              className={`w-10 h-10 rounded-full flex items-center justify-center transition-colors cursor-pointer ${
                selected
                  ? 'hover:bg-white/20 text-white'
                  : 'hover:bg-[#eceeee] text-[#3e4946]'
              }`}
            >
              <Volume2 className="w-5 h-5" />
            </div>
          )}

          {selected && (
            <CheckCircle2 className="w-7 h-7 text-white animate-fade-in-down" />
          )}
        </div>
      </div>

      {/* Bottom: Title + Subtitle + Badge */}
      <div className="mt-4">
        <div className="flex items-center gap-2">
          <span className="text-xl md:text-2xl font-bold tracking-tight">
            {title}
          </span>
          {badge && (
            <span
              className={`text-xs px-2.5 py-0.5 rounded-full font-bold uppercase tracking-wider ${
                selected
                  ? 'bg-white/20 text-white'
                  : 'bg-[#005f53]/10 text-[#005f53]'
              }`}
            >
              {badge}
            </span>
          )}
        </div>
        {subtitle && (
          <p
            className={`text-sm mt-1 line-clamp-2 ${
              selected ? 'text-white/85' : 'text-[#3e4946]'
            }`}
          >
            {subtitle}
          </p>
        )}
      </div>
    </button>
  );
}
