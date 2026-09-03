/**
 * MediKiosk — Patient Summary Confirmation (/summary)
 * Screen 10: Comprehensive visual intake summary with vernacular audio confirmation.
 * Final review before submission to physician EMR desk.
 */

'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import KioskHeader from '@/components/layout/KioskHeader';
import KioskFooter from '@/components/layout/KioskFooter';
import StepProgressBar from '@/components/layout/StepProgressBar';
import { useSessionStore } from '@/stores/useSessionStore';
import { useFlowStore } from '@/stores/useFlowStore';
import { useIntakeStore } from '@/stores/useIntakeStore';
import { useTTS } from '@/hooks/useTTS';
import { intakeService } from '@/services/intakeService';
import { t } from '@/lib/i18n';
import { Volume2, CheckCircle2, User, FileText, Pill, AlertCircle, RefreshCw } from 'lucide-react';

export default function SummaryPage() {
  const router = useRouter();
  const {
    language,
    sessionId,
    patientName,
    patientAge,
    patientGender,
    abhaAddress,
    intakeMode,
    setCompletedToken,
  } = useSessionStore();
  const { setCurrentScreen } = useFlowStore();
  const {
    chiefComplaint,
    bodyRegion,
    painSeverity,
    ayushAnswers,
  } = useIntakeStore();
  const { speak, isSpeaking } = useTTS();

  const [isSubmitting, setIsSubmitting] = useState(false);

  const summarySpeechText = `Summary of your visit: Chief complaint is ${
    chiefComplaint || 'general check-up'
  }, with pain severity rated at ${painSeverity} out of 10. Tap submit to send your draft to the doctor.`;

  const handleListenSummary = () => {
    speak(summarySpeechText, language);
  };

  const handleSubmitToDoctor = async () => {
    setIsSubmitting(true);
    const token = `A-${Math.floor(100 + Math.random() * 900)}`;
    const room =
      intakeMode === 'AYUSH'
        ? 'Room 204 — Dr. Sunita Vaidya (AIIA OPD)'
        : 'Room 106 — Dr. Arvind Kumar (Cardiology OPD)';

    if (sessionId) {
      try {
        await intakeService.generateSummary(sessionId);
        await intakeService.submitDelivery(sessionId, 'MOCK');
      } catch (err) {
        console.warn('Backend final submission sync error:', err);
      }
    }

    setCompletedToken(token, room);
    setCurrentScreen('opd_token');
    router.push('/complete');
  };

  const handleBack = () => {
    router.back();
  };

  return (
    <div className="h-screen w-screen flex flex-col bg-[#f8fafa] overflow-hidden">
      <KioskHeader onBack={handleBack} />
      <StepProgressBar />

      <main className="flex-1 max-w-4xl w-full mx-auto p-4 md:p-8 flex flex-col justify-between overflow-y-auto">
        {/* Title */}
        <div className="text-center mb-4">
          <h1 className="text-2xl md:text-3xl font-black text-[#191c1d] tracking-tight">
            {t('summary.title', language)}
          </h1>
          <p className="text-xs md:text-sm text-[#3e4946] mt-1">
            {t('summary.subtitle', language)}
          </p>

          {/* Spoken Vernacular Summary Button */}
          <button
            type="button"
            onClick={handleListenSummary}
            className="inline-flex items-center gap-2 mt-3 px-5 py-2 rounded-full bg-[#eceeee] hover:bg-[#e1e3e3] text-[#005f53] font-bold text-xs md:text-sm transition-all cursor-pointer shadow-xs active:scale-95"
          >
            <Volume2 className={`w-4 h-4 ${isSpeaking ? 'animate-bounce text-[#aa0a17]' : ''}`} />
            <span>{isSpeaking ? 'Reading Aloud...' : t('summary.listen', language)}</span>
          </button>
        </div>

        {/* Structured Summary Cards */}
        <div className="my-auto space-y-3 max-w-2xl mx-auto w-full">
          {/* Section 1: Patient Demographics */}
          <div className="bg-white p-4 rounded-2xl border border-[#bdc9c5]/60 shadow-xs flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-[#005f53]/10 text-[#005f53] flex items-center justify-center">
                <User className="w-5 h-5" />
              </div>
              <div>
                <h4 className="font-bold text-sm text-[#191c1d]">
                  {patientName || 'Walk-in Guest'}
                </h4>
                <p className="text-xs text-[#3e4946]">
                  {patientAge || 45} Yrs • {patientGender || 'MALE'} • ABHA: {abhaAddress || 'Unlinked'}
                </p>
              </div>
            </div>
            <span className="text-xs font-bold px-2.5 py-1 rounded-full bg-[#005f53]/10 text-[#005f53]">
              {intakeMode}
            </span>
          </div>

          {/* Section 2: Chief Complaint & Pain */}
          <div className="bg-white p-4 rounded-2xl border border-[#bdc9c5]/60 shadow-xs">
            <div className="flex items-center justify-between mb-2">
              <h4 className="font-bold text-sm text-[#191c1d] flex items-center gap-2">
                <FileText className="w-4 h-4 text-[#005f53]" />
                <span>Presenting Symptoms</span>
              </h4>
              <button
                type="button"
                onClick={() => router.push('/intake/symptoms')}
                className="text-xs text-[#005f53] font-bold hover:underline cursor-pointer"
              >
                Edit
              </button>
            </div>
            <div className="p-3 rounded-xl bg-[#f2f4f4] text-xs space-y-1">
              <div className="flex justify-between">
                <span className="text-[#3e4946]">Chief Complaint:</span>
                <span className="font-bold text-[#191c1d]">{chiefComplaint || 'General OPD Consultation'}</span>
              </div>
              {bodyRegion && (
                <div className="flex justify-between">
                  <span className="text-[#3e4946]">Localized Body Area:</span>
                  <span className="font-bold text-[#191c1d] uppercase">{bodyRegion}</span>
                </div>
              )}
              <div className="flex justify-between">
                <span className="text-[#3e4946]">Pain Severity Score:</span>
                <span className="font-bold text-[#aa0a17]">{painSeverity} / 10</span>
              </div>
            </div>
          </div>

          {/* Section 3: AYUSH Parameters (if AYUSH mode) */}
          {intakeMode === 'AYUSH' && (
            <div className="bg-white p-4 rounded-2xl border border-[#bdc9c5]/60 shadow-xs">
              <h4 className="font-bold text-sm text-[#191c1d] mb-2">
                Ayurvedic Assessment (Dashavidha)
              </h4>
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div className="p-2 rounded-lg bg-[#f2f4f4]">
                  <span className="text-[#3e4946]">Prakriti:</span>
                  <span className="font-bold ml-1 text-[#005f53]">{ayushAnswers.prakriti || 'Vata-Pitta'}</span>
                </div>
                <div className="p-2 rounded-lg bg-[#f2f4f4]">
                  <span className="text-[#3e4946]">Agni:</span>
                  <span className="font-bold ml-1 text-[#005f53]">{ayushAnswers.agni || 'Samagni'}</span>
                </div>
              </div>
            </div>
          )}

          {/* Clinical Safety Draft Banner */}
          <div className="p-3 rounded-xl bg-[#005f53]/5 border border-[#005f53]/20 flex items-center gap-2 text-xs text-[#005f53]">
            <CheckCircle2 className="w-4 h-4 flex-shrink-0" />
            <span>
              This information will be compiled as an editable draft for your attending physician.
            </span>
          </div>
        </div>
      </main>

      <KioskFooter
        onNext={handleSubmitToDoctor}
        onBack={handleBack}
        nextText={isSubmitting ? 'Sending to Doctor...' : t('summary.submit', language)}
      />
    </div>
  );
}
