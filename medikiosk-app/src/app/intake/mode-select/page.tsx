/**
 * MediKiosk — Clinical Intake Mode Selector (/intake/mode-select)
 * Screen 05: Switches between Allopathic General OPD and Ayurvedic OPD (AYUSH - AIIA New Delhi).
 */

'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import KioskHeader from '@/components/layout/KioskHeader';
import KioskFooter from '@/components/layout/KioskFooter';
import StepProgressBar from '@/components/layout/StepProgressBar';
import OptionCard from '@/components/interactive/OptionCard';
import { useSessionStore } from '@/stores/useSessionStore';
import { useFlowStore } from '@/stores/useFlowStore';
import { useTTS } from '@/hooks/useTTS';
import { t } from '@/lib/i18n';
import type { IntakeMode } from '@/lib/constants';
import { Stethoscope, Flower2, ShieldAlert } from 'lucide-react';

export default function ModeSelectPage() {
  const router = useRouter();
  const { language, sessionId, intakeMode, setIntakeMode } = useSessionStore();
  const { setCurrentScreen } = useFlowStore();
  const { speak, stop } = useTTS();

  // Auto-speak mode selection guidance on screen entry
  useEffect(() => {
    const promptMsg = language === 'hi'
      ? 'कृपया अपनी परामर्श पद्धति चुनें: सामान्य एलोपैथिक या आयुर्वेदिक आयुष।'
      : 'Please choose your consultation mode: General Allopathic medicine or Ayurvedic AYUSH.';
    speak(promptMsg, language);

    return () => {
      stop();
    };
  }, []); // Run once on mount

  const handleSelectMode = (mode: IntakeMode) => {
    setIntakeMode(mode);
    if (sessionId) {
      import('@/services/intakeService').then(({ intakeService }) => {
        intakeService.setIntakeMode(sessionId, mode).catch(() => {});
      });
    }
  };

  const handleProceed = () => {
    stop();
    if (sessionId) {
      import('@/services/intakeService').then(({ intakeService }) => {
        intakeService.setIntakeMode(sessionId, intakeMode).catch(() => {});
      });
    }
    setCurrentScreen('patient_identification');
    router.push('/auth');
  };

  const handleBack = () => {
    stop();
    setCurrentScreen('language_picker');
    router.push('/language');
  };

  return (
    <div className="h-screen w-screen flex flex-col bg-[#f8fafa] overflow-hidden">
      <KioskHeader onBack={handleBack} />
      <StepProgressBar />

      <main className="flex-1 max-w-5xl w-full mx-auto p-6 md:p-10 flex flex-col justify-between overflow-y-auto">
        <div className="text-center mb-6">
          <span className="inline-block px-4 py-1.5 rounded-full bg-[#005f53]/10 text-[#005f53] font-bold text-xs uppercase tracking-wider mb-2">
            Clinical Protocol Selection
          </span>
          <h1 className="text-3xl md:text-4xl font-black text-[#191c1d] tracking-tight">
            {t('mode.title', language)}
          </h1>
          <p className="text-base text-[#3e4946] mt-2">
            Choose your hospital department for tailored symptom inquiry.
          </p>
        </div>

        {/* 2 High-Impact Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 my-auto">
          <OptionCard
            id="mode-allopathic-card"
            title="General OPD (Allopathic)"
            subtitle="Modern Medicine — SOCRATES symptom assessment, Review of Systems, Drug and Allergy profiling."
            selected={intakeMode === 'ALLOPATHIC'}
            badge={intakeMode === 'ALLOPATHIC' ? 'Active' : undefined}
            dataElement="mode-allopathic-card"
            dataVoiceAction="select-allopathic"
            dataVoiceParam="Allopathic"
            onSelect={() => handleSelectMode('ALLOPATHIC')}
            icon={<Stethoscope className="w-8 h-8" />}
          />

          <OptionCard
            id="mode-ayush-card"
            title="Ayurvedic OPD (AYUSH)"
            subtitle="All India Institute of Ayurveda — Dashavidha Pariksha, Prakriti, Vikriti, Agni, and Ahara-Vihara assessment."
            selected={intakeMode === 'AYUSH'}
            badge={intakeMode === 'AYUSH' ? 'Active' : undefined}
            dataElement="mode-ayush-card"
            dataVoiceAction="select-ayush"
            dataVoiceParam="Ayurvedic AYUSH"
            onSelect={() => handleSelectMode('AYUSH')}
            icon={<Flower2 className="w-8 h-8" />}
          />
        </div>

        {/* Informational Disclaimer */}
        <div className="p-4 rounded-2xl bg-white border border-[#bdc9c5]/40 text-center text-xs text-[#3e4946] max-w-2xl mx-auto shadow-xs">
          Selected pathway configures the automated question sequence and clinical ontology.
        </div>
      </main>

      <KioskFooter
        onNext={handleProceed}
        onBack={handleBack}
        nextText={t('nav.continue', language)}
      />
    </div>
  );
}
