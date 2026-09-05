/**
 * MediKiosk — Digitized Records Review & Timeline (/documents/timeline)
 * Screen 09: Chronological medical timeline of digitized prescriptions and lab tests,
 * highlighting out-of-range abnormal values and current active medications.
 */

'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import KioskHeader from '@/components/layout/KioskHeader';
import KioskFooter from '@/components/layout/KioskFooter';
import StepProgressBar from '@/components/layout/StepProgressBar';
import { useSessionStore } from '@/stores/useSessionStore';
import { useFlowStore } from '@/stores/useFlowStore';
import { useIntakeStore } from '@/stores/useIntakeStore';
import { useTTS } from '@/hooks/useTTS';
import { t } from '@/lib/i18n';
import { Calendar, Pill, AlertTriangle, CheckCircle2, FileText } from 'lucide-react';
import { Medicines, BloodBag } from '@/components/icons/ClinicalIcon';

export default function DocumentTimelinePage() {
  const router = useRouter();
  const { language } = useSessionStore();
  const { setCurrentScreen } = useFlowStore();
  const { uploadedDocuments } = useIntakeStore();
  const { speak, stop } = useTTS();

  useEffect(() => {
    setCurrentScreen('document_timeline');
  }, [setCurrentScreen]);

  // Auto-speak guidance prompt on screen load
  useEffect(() => {
    const prompt = t('timeline.audio_prompt', language) || 'Here is your medical timeline from your documents. Tap continue to review summary.';
    speak(prompt, language);
    return () => {
      stop();
    };
  }, [language, speak, stop]);

  const handleProceed = () => {
    stop();
    setCurrentScreen('patient_summary');
    router.push('/summary');
  };

  const handleBack = () => {
    stop();
    setCurrentScreen('document_scanner');
    router.push('/documents/scan');
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
            <div className="absolute left-4 top-6 w-6 h-6 rounded-full bg-[#005f53] flex items-center justify-center text-white">
              <Medicines className="w-4 h-4" />
            </div>

            <div className="flex justify-between items-center mb-2">
              <span className="text-xs font-bold uppercase tracking-wider text-[#005f53]">
                {t('timeline.rx_heading', language)}
              </span>
              <span className="text-xs text-[#3e4946] flex items-center gap-1">
                <Calendar className="w-3.5 h-3.5" />
                <span>{t('timeline.date_rx', language)}</span>
              </span>
            </div>

            <h4 className="font-bold text-base text-[#191c1d] mb-2">
              {t('timeline.active_meds', language)}
            </h4>
            <div className="flex flex-wrap gap-2">
              <span className="px-3 py-1 rounded-full bg-[#f2f4f4] text-xs font-bold text-[#191c1d] border border-[#bdc9c5]/50 flex items-center gap-1">
                <Medicines className="w-3.5 h-3.5 text-[#005f53]" /> Metformin 500mg (1-0-1)
              </span>
              <span className="px-3 py-1 rounded-full bg-[#f2f4f4] text-xs font-bold text-[#191c1d] border border-[#bdc9c5]/50 flex items-center gap-1">
                <Medicines className="w-3.5 h-3.5 text-[#005f53]" /> Telmisartan 40mg (1-0-0)
              </span>
              <span className="px-3 py-1 rounded-full bg-[#f2f4f4] text-xs font-bold text-[#191c1d] border border-[#bdc9c5]/50 flex items-center gap-1">
                <Medicines className="w-3.5 h-3.5 text-[#005f53]" /> Atorvastatin 10mg (0-0-1)
              </span>
            </div>
          </div>

          {/* Timeline Item 2: Extracted Lab Report with Out-of-Range warning */}
          <div className="bg-white p-5 rounded-3xl border border-[#bdc9c5]/60 shadow-sm relative pl-12">
            <div className="absolute left-4 top-6 w-6 h-6 rounded-full bg-[#aa0a17] flex items-center justify-center text-white">
              <BloodBag className="w-4 h-4" />
            </div>

            <div className="flex justify-between items-center mb-2">
              <span className="text-xs font-bold uppercase tracking-wider text-[#aa0a17]">
                {t('timeline.lab_heading', language)}
              </span>
              <span className="text-xs text-[#3e4946] flex items-center gap-1">
                <Calendar className="w-3.5 h-3.5" />
                <span>{t('timeline.date_lab', language)}</span>
              </span>
            </div>

            <h4 className="font-bold text-base text-[#191c1d] mb-2">
              {t('timeline.biomarkers', language)}
            </h4>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              <div className="p-2.5 rounded-xl bg-[#006e1c]/5 border border-[#006e1c]/20 flex items-center justify-between text-xs">
                <span className="font-semibold text-[#191c1d]">Hemoglobin (Hb)</span>
                <span className="font-bold text-[#006e1c]">13.8 g/dL [{t('timeline.normal', language)}]</span>
              </div>
              <div className="p-2.5 rounded-xl bg-[#aa0a17]/10 border border-[#aa0a17]/30 flex items-center justify-between text-xs">
                <span className="font-semibold text-[#191c1d]">HbA1c (Glycated Hb)</span>
                <span className="font-bold text-[#aa0a17] flex items-center gap-1">
                  <span>8.2%</span>
                  <span className="text-[10px] uppercase">[{t('timeline.high', language)}]</span>
                </span>
              </div>
            </div>
          </div>
        </div>

        <div className="text-center text-xs text-[#3e4946]">
          {t('timeline.disclaimer', language)}
        </div>
      </main>

      <KioskFooter
        onNext={handleProceed}
        onBack={handleBack}
        nextText={t('timeline.proceed_btn', language)}
      />
    </div>
  );
}
