/**
 * MediKiosk — Pain Severity Scale Component
 * 1-to-10 visual slider combined with Wong-Baker facial expressions.
 */

'use client';

import { useSessionStore } from '@/stores/useSessionStore';
import { t } from '@/lib/i18n';

interface PainSeveritySliderProps {
  value: number;
  onChange: (val: number) => void;
}

const PAIN_LEVELS = [
  { val: 0, key: 'none', defaultLabel: 'No Pain', emoji: '😊', color: '#006e1c' },
  { val: 2, key: 'mild', defaultLabel: 'Mild', emoji: '🙂', color: '#0f7a6b' },
  { val: 4, key: 'moderate', defaultLabel: 'Moderate', emoji: '😐', color: '#e69a00' },
  { val: 6, key: 'severe', defaultLabel: 'Severe', emoji: '😣', color: '#e65100' },
  { val: 8, key: 'very_severe', defaultLabel: 'Very Severe', emoji: '😭', color: '#ce2b2c' },
  { val: 10, key: 'worst', defaultLabel: 'Worst Possible', emoji: '😱', color: '#aa0a17' },
];

export default function PainSeveritySlider({
  value,
  onChange,
}: PainSeveritySliderProps) {
  const language = useSessionStore((s) => s.language);

  // Find closest representation
  const activeLevel =
    PAIN_LEVELS.reduce((prev, curr) =>
      Math.abs(curr.val - value) < Math.abs(prev.val - value) ? curr : prev
    );

  const translatedLabel = t(`pain.${activeLevel.key}`, language) || activeLevel.defaultLabel;

  return (
    <div
      id="kiosk-pain-slider-container"
      data-element="severity-slider"
      data-testid="severity-slider"
      className="w-full max-w-3xl mx-auto p-6 bg-white rounded-3xl border border-[#bdc9c5]/60 shadow-sm flex flex-col items-center gap-6"
    >
      {/* Current Emoji & Score Badge */}
      <div className="flex flex-col items-center">
        <span className="text-6xl md:text-7xl animate-pulse-glow" role="img" aria-label="Pain Emoji">
          {activeLevel.emoji}
        </span>
        <div className="flex items-center gap-3 mt-3">
          <span
            className="text-3xl md:text-4xl font-black px-4 py-1 rounded-2xl text-white shadow-sm"
            style={{ backgroundColor: activeLevel.color }}
          >
            {value} / 10
          </span>
          <span className="text-xl font-bold text-[#191c1d]">
            {translatedLabel}
          </span>
        </div>
      </div>

      {/* Touch-Friendly Range Slider */}
      <div className="w-full px-4">
        <input
          type="range"
          min="0"
          max="10"
          step="1"
          value={value}
          onChange={(e) => onChange(parseInt(e.target.value, 10))}
          className="w-full h-5 bg-[#eceeee] rounded-full appearance-none cursor-pointer accent-[#005f53] focus:outline-none"
        />
      </div>

      {/* Discrete 0-10 Number Touch Buttons */}
      <div className="grid grid-cols-6 sm:grid-cols-11 gap-2 w-full">
        {Array.from({ length: 11 }, (_, i) => i).map((num) => {
          const isSelected = value === num;
          return (
            <button
              key={num}
              type="button"
              id={`pain-score-${num}`}
              data-element={`pain-score-${num}`}
              data-voice-action={`pain-level-${num}`}
              data-testid={`pain-score-${num}`}
              onClick={() => onChange(num)}
              className={`h-12 md:h-14 rounded-2xl font-black text-lg md:text-xl flex items-center justify-center transition-all cursor-pointer border ${
                isSelected
                  ? 'bg-[#005f53] text-white border-transparent shadow-md scale-105'
                  : 'bg-[#f8fafa] hover:bg-[#eceeee] text-[#191c1d] border-[#bdc9c5]/60'
              }`}
            >
              {num}
            </button>
          );
        })}
      </div>
    </div>
  );
}
