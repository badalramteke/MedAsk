/**
 * MediKiosk — Digitized Records Review & Timeline (/documents/timeline)
 * Screen 09: Chronological medical timeline of digitized prescriptions and lab tests,
 * highlighting out-of-range abnormal values and current active medications.
 */

'use client';

import { useRouter } from 'next/navigation';
import KioskHeader from '@/components/layout/KioskHeader';
import KioskFooter from '@/components/layout/KioskFooter';
import StepProgressBar from '@/components/layout/StepProgressBar';
import { useSessionStore } from '@/stores/useSessionStore';
import { useFlowStore } from '@/stores/useFlowStore';
import { useIntakeStore } from '@/stores/useIntakeStore';
import { t } from '@/lib/i18n';
import { Calendar, Pill, AlertTriangle, CheckCircle2, FileText } from 'lucide-react';

export default function DocumentTimelinePage() {
  const router = useRouter();
  const { language } = useSessionStore();
  const { setCurrentScreen } = useFlowStore();
  const { uploadedDocuments } = useIntakeStore();

  const handleProceed = () => {
    setCurrentScreen('patient_summary');
    router.push('/summary');
  };

  const handleBack = () => {
    router.back();
  };

  return (
    <div className="h-screen w-screen flex flex-col bg-[#f8fafa] overflow-hidden">
      <KioskHeader onBack={handleBack} />
      <StepProgressBar />

      <main className="flex-1 max-w-4xl w-full mx-auto p-4 md:p-8 flex flex-col justify-between overflow-y-auto">
        <div className="text-center mb-4">
          <h1 className="text-2xl md:text-3xl font-black text-[#191c1d] tracking-tight">
            {t('timeline.title', language)}
          </h1>
          <p className="text-xs md:text-sm text-[#3e4946] mt-1">
            {t('timeline.subtitle', language)}
          </p>
        </div>

        {/* Chronological Medical Timeline Cards */}
        <div className="my-auto space-y-4 max-w-2xl mx-auto w-full">
          {/* Timeline Item 1: Extracted Prescription */}
          <div className="bg-white p-5 rounded-3xl border border-[#bdc9c5]/60 shadow-sm relative pl-12">
            <div className="absolute left-4 top-6 w-5 h-5 rounded-full bg-[#005f53] flex items-center justify-center text-white">
              <Pill className="w-3 h-3" />
            </div>

            <div className="flex justify-between items-center mb-2">
              <span className="text-xs font-bold uppercase tracking-wider text-[#005f53]">
                Prescription (Cardiology OPD)
              </span>
              <span className="text-xs text-[#3e4946] flex items-center gap-1">
                <Calendar className="w-3.5 h-3.5" />
                <span>12 June 2024</span>
              </span>
            </div>

            <h4 className="font-bold text-base text-[#191c1d] mb-2">
              Extracted Active Medications:
            </h4>
            <div className="flex flex-wrap gap-2">
              <span className="px-3 py-1 rounded-full bg-[#f2f4f4] text-xs font-bold text-[#191c1d] border border-[#bdc9c5]/50">
                💊 Metformin 500mg (1-0-1)
              </span>
              <span className="px-3 py-1 rounded-full bg-[#f2f4f4] text-xs font-bold text-[#191c1d] border border-[#bdc9c5]/50">
                💊 Telmisartan 40mg (1-0-0)
              </span>
              <span className="px-3 py-1 rounded-full bg-[#f2f4f4] text-xs font-bold text-[#191c1d] border border-[#bdc9c5]/50">
                💊 Atorvastatin 10mg (0-0-1)
              </span>
            </div>
          </div>

          {/* Timeline Item 2: Extracted Lab Report with Out-of-Range warning */}
          <div className="bg-white p-5 rounded-3xl border border-[#bdc9c5]/60 shadow-sm relative pl-12">
            <div className="absolute left-4 top-6 w-5 h-5 rounded-full bg-[#aa0a17] flex items-center justify-center text-white">
              <AlertTriangle className="w-3 h-3" />
            </div>

            <div className="flex justify-between items-center mb-2">
              <span className="text-xs font-bold uppercase tracking-wider text-[#aa0a17]">
                Diagnostic Lab Report
              </span>
              <span className="text-xs text-[#3e4946] flex items-center gap-1">
                <Calendar className="w-3.5 h-3.5" />
                <span>18 July 2024</span>
              </span>
            </div>

            <h4 className="font-bold text-base text-[#191c1d] mb-2">
              Extracted Diagnostic Biomarkers:
            </h4>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              <div className="p-2.5 rounded-xl bg-[#006e1c]/5 border border-[#006e1c]/20 flex items-center justify-between text-xs">
                <span className="font-semibold text-[#191c1d]">Hemoglobin (Hb)</span>
                <span className="font-bold text-[#006e1c]">13.8 g/dL [Normal]</span>
              </div>
              <div className="p-2.5 rounded-xl bg-[#aa0a17]/10 border border-[#aa0a17]/30 flex items-center justify-between text-xs">
                <span className="font-semibold text-[#191c1d]">HbA1c (Glycated Hb)</span>
                <span className="font-bold text-[#aa0a17] flex items-center gap-1">
                  <span>8.2%</span>
                  <span className="text-[10px] uppercase">[HIGH]</span>
                </span>
              </div>
            </div>
          </div>
        </div>

        <div className="text-center text-xs text-[#3e4946]">
          These records will be linked to your consultation history draft.
        </div>
      </main>

      <KioskFooter
        onNext={handleProceed}
        onBack={handleBack}
        nextText="Proceed to Summary Confirmation"
      />
    </div>
  );
}
