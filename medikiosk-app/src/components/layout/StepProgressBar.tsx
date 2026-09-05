/**
 * MediKiosk — Clinical Step Progress Bar
 * Displays the 7-stage sequential clinical journey with active stage highlighting.
 */

'use client';

import { CLINICAL_STAGES } from '@/lib/constants';
import { useFlowStore } from '@/stores/useFlowStore';
import { useSessionStore } from '@/stores/useSessionStore';
import { t } from '@/lib/i18n';
import {
  HospitalSymbol,
  HealthCreditCard,
  SecurityWorker,
  HealthStethoscope,
  PrescriptionDocument,
  MedicalRecords,
  Positive,
} from '@/components/icons/ClinicalIcon';

function getStageIcon(key: string, className: string) {
  switch (key) {
    case 'WELCOME':
      return <HospitalSymbol className={className} />;
    case 'IDENTIFICATION':
      return <HealthCreditCard className={className} />;
    case 'CONSENT':
      return <SecurityWorker className={className} />;
    case 'INTAKE':
      return <HealthStethoscope className={className} />;
    case 'DOCUMENTS':
      return <PrescriptionDocument className={className} />;
    case 'SUMMARY':
      return <MedicalRecords className={className} />;
    case 'COMPLETE':
      return <Positive className={className} />;
    default:
      return null;
  }
}

export default function StepProgressBar() {
  const { currentStageIndex } = useFlowStore();
  const language = useSessionStore((s) => s.language);

  return (
    <div
      id="kiosk-progress-bar"
      data-element="step-progress-bar"
      data-testid="step-progress-bar"
      className="w-full bg-[#f2f4f4] px-6 md:px-12 py-2.5 border-b border-[#bdc9c5]/20 flex-shrink-0"
    >
      <div className="max-w-5xl mx-auto flex items-center justify-between gap-1">
        {CLINICAL_STAGES.map((stage, idx) => {
          const isCompleted = idx < currentStageIndex;
          const isCurrent = idx === currentStageIndex;
          const iconColor = isCurrent
            ? 'text-[#005f53]'
            : isCompleted
            ? 'text-[#0f7a6b]'
            : 'text-[#3e4946]/40';

          return (
            <div key={stage.key} className="flex-1 flex flex-col items-center">
              <div className="w-full flex items-center mb-1">
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
              <div className="flex items-center gap-1">
                {getStageIcon(stage.key, `w-3.5 h-3.5 flex-shrink-0 ${iconColor}`)}
                <span
                  className={`text-[10px] md:text-xs font-semibold truncate transition-colors ${
                    isCurrent
                      ? 'text-[#005f53] font-bold'
                      : isCompleted
                      ? 'text-[#191c1d]'
                      : 'text-[#3e4946]/50'
                  }`}
                >
                  {t(`stage.${stage.key.toLowerCase()}`, language) || stage.label}
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
