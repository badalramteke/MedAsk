/**
 * MediKiosk — Patient Summary Confirmation (/summary)
 * Screen 10: Comprehensive visual intake summary with vernacular audio confirmation.
 * Final review before submission to physician EMR desk.
 */

'use client';

import { useState, useEffect } from 'react';
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
import { Volume2, CheckCircle2, User, FileText } from 'lucide-react';
import { Person as HealthPerson, HealthStethoscope, Positive } from '@/components/icons/ClinicalIcon';

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
    recordsTimeline,
  } = useIntakeStore();
  const { speak, isSpeaking, stop } = useTTS();

  useEffect(() => {
    setCurrentScreen('patient_summary');
  }, [setCurrentScreen]);

  const [isSubmitting, setIsSubmitting] = useState(false);
  const summarySpeechTexts: Record<string, string> = {
    en: `Summary of your visit: Chief complaint is ${chiefComplaint || 'general check-up'}, with pain severity rated at ${painSeverity} out of 10. Tap submit to send your draft to the doctor.`,
    hi: `आपके दौरे का सारांश: मुख्य लक्षण ${chiefComplaint || 'सामान्य जांच'} है, और दर्द की तीव्रता 10 में से ${painSeverity} है। डॉक्टर को भेजने के लिए सबमिट पर टैप करें।`,
    mr: `आपल्या तपासणीचा सारांश: मुख्य लक्षण ${chiefComplaint || 'सामान्य तपासणी'} आहे, आणि वेदनेची तीव्रता १० पैकी ${painSeverity} आहे. डॉक्टरांकडे पाठवण्यासाठी सबमिट टॅप करा.`,
    bn: `আপনার পরিদর্শনের সারাংশ: প্রধান লক্ষণ ${chiefComplaint || 'সাধারণ স্বাস্থ্য পরীক্ষা'}, এবং ব্যথার তীব্রতা ১০ এ ${painSeverity}। ডাক্তারের কাছে পাঠাতে জমা দিন চাপুন।`,
    ta: `உங்கள் வருகையின் சுருக்கம்: முக்கிய பிரச்சனை ${chiefComplaint || 'பொது பரிசோதனை'}, மற்றும் வலி அளவு 10-க்கு ${painSeverity}. மருத்துவருக்கு அனுப்ப சமர்ப்பிக்கவும்.`,
    te: `మీ సందర్శన సారాంశం: ప్రధాన సమస్య ${chiefComplaint || 'సాధారణ తనిఖీ'}, మరియు నొప్పి తీవ్రత 10 కి ${painSeverity}. డాక్టర్‌కు పంపడానికి సమర్పించు నొక్కండి.`,
  };

  const handleListenSummary = () => {
    const text = summarySpeechTexts[language] || summarySpeechTexts.en;
    speak(text, language);
  };

  const handleSubmitToDoctor = () => {
    setIsSubmitting(true);
    const token = `A-${Math.floor(100 + Math.random() * 900)}`;
    const room =
      intakeMode === 'AYUSH'
        ? 'Room 204 — Dr. Sunita Vaidya (AIIA OPD)'
        : 'Room 106 — Dr. Arvind Kumar (Cardiology OPD)';

    setCompletedToken(token, room);
    setCurrentScreen('opd_token');
    router.push('/complete');

    if (sessionId) {
      intakeService
        .generateSummary(sessionId)
        .then(() => intakeService.submitDelivery(sessionId, 'MOCK'))
        .catch((err) => {
          console.warn('Backend final submission sync note:', err);
        });
    }
  };

  const handleBack = () => {
    stop();
    if (recordsTimeline && recordsTimeline.length > 0) {
      setCurrentScreen('document_timeline');
      router.push('/documents/timeline');
    } else {
      setCurrentScreen('document_scanner');
      router.push('/documents/scan');
    }
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
            <span>{isSpeaking ? t('summary.reading', language) : t('summary.listen', language)}</span>
          </button>
        </div>

        {/* Structured Summary Cards */}
        <div className="my-auto space-y-3 max-w-2xl mx-auto w-full">
          {/* Section 1: Patient Demographics */}
          <div className="bg-white p-4 rounded-2xl border border-[#bdc9c5]/60 shadow-xs flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-[#005f53]/10 text-[#005f53] flex items-center justify-center">
                <HealthPerson className="w-6 h-6" />
              </div>
              <div>
                <h4 className="font-bold text-sm text-[#191c1d]">
                  {patientName || t('complete.walkin_guest', language)}
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
                <HealthStethoscope className="w-4 h-4 text-[#005f53]" />
                <span>{t('summary.presenting_symptoms', language)}</span>
              </h4>
              <button
                type="button"
                onClick={() => {
                  setCurrentScreen('chief_complaint');
                  router.push('/intake/symptoms');
                }}
                className="text-xs text-[#005f53] font-bold hover:underline cursor-pointer"
              >
                {t('summary.edit', language)}
              </button>
            </div>
            <div className="p-3 rounded-xl bg-[#f2f4f4] text-xs space-y-1">
              <div className="flex justify-between">
                <span className="text-[#3e4946]">{t('summary.chief_complaint', language)}:</span>
                <span className="font-bold text-[#191c1d]">{chiefComplaint || t('summary.general_checkup', language)}</span>
              </div>
              {bodyRegion && (
                <div className="flex justify-between">
                  <span className="text-[#3e4946]">{t('summary.body_region', language)}:</span>
                  <span className="font-bold text-[#191c1d] uppercase">{t(`body.${bodyRegion.toLowerCase()}`, language) || bodyRegion}</span>
                </div>
              )}
              <div className="flex justify-between">
                <span className="text-[#3e4946]">{t('summary.pain_severity', language)}:</span>
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
            <Positive className="w-4 h-4 flex-shrink-0" />
            <span>
              {t('summary.docs_attached', language)}
            </span>
          </div>
        </div>
      </main>

      <KioskFooter
        onNext={handleSubmitToDoctor}
        onBack={handleBack}
        nextText={isSubmitting ? t('summary.submitting', language) : t('summary.submit', language)}
      />
    </div>
  );
}
