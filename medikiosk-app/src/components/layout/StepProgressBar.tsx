/**
 * MediKiosk — Clinical Step Progress Bar
 * Displays the 7-stage sequential clinical journey with active stage highlighting.
 */

'use client';

import { CLINICAL_STAGES } from '@/lib/constants';
import { useFlowStore } from '@/stores/useFlowStore';

export default function StepProgressBar() {
  const { currentStageIndex } = useFlowStore();

  return (
    <div
      id="kiosk-progress-bar"
      data-element="step-progress-bar"
      data-testid="step-progress-bar"
      className="w-full bg-[#f2f4f4] px-6 md:px-12 py-3 border-b border-[#bdc9c5]/20 flex-shrink-0"
    >
      <div className="max-w-5xl mx-auto flex items-center justify-between gap-1">
        {CLINICAL_STAGES.map((stage, idx) => {
          const isCompleted = idx < currentStageIndex;
          const isCurrent = idx === currentStageIndex;

          return (
            <div key={stage.key} className="flex-1 flex flex-col items-center">
              <div className="w-full flex items-center">
                <div
                  className={`h-2 w-full rounded-full transition-all duration-300 ${
                    isCompleted
                      ? 'bg-[#005f53]'
                      : isCurrent
                      ? 'bg-[#0f7a6b] shadow-sm'
                      : 'bg-[#bdc9c5]/40'
                  }`}
                />
              </div>
              <span
                className={`text-[11px] md:text-xs mt-1 font-semibold truncate transition-colors ${
                  isCurrent
                    ? 'text-[#005f53] font-bold'
                    : isCompleted
                    ? 'text-[#191c1d]'
                    : 'text-[#3e4946]/50'
                }`}
              >
                {stage.label}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
