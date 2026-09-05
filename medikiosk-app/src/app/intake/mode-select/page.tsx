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
import { HealthStethoscope, ExerciseYoga } from '@/components/icons/ClinicalIcon';

export default function ModeSelectPage() {
  const router = useRouter();
  const { language, sessionId, intakeMode, setIntakeMode } = useSessionStore();
  const { setCurrentScreen } = useFlowStore();
  const { speak, stop } = useTTS();

  useEffect(() => {
    setCurrentScreen('mode_selection');
  }, [setCurrentScreen]);

  // Auto-speak mode selection guidance on screen entry
  useEffect(() => {
    const promptPrompts: Record<string, string> = {
      en: 'Please choose your consultation mode: General Allopathic medicine or Ayurvedic AYUSH.',
      hi: 'कृपया अपनी परामर्श पद्धति चुनें: सामान्य एलोपैथिक या आयुर्वेदिक आयुष।',
      mr: 'कृपया आपला सल्लामसलत प्रकार निवडा: सामान्य अ‍ॅलोपॅथिक किंवा आयुर्वेदिक आयुष.',
      bn: 'আপনার পরামর্শের ধরন নির্বাচন করুন: সাধারণ অ্যালোপ্যাথিক বা আয়ুর্বেদিক আয়ুষ।',
      ta: 'உங்கள் ஆலோசனை வகையைத் தேர்ந்தெடுக்கவும்: பொது அலோபதி அல்லது ஆயுர்வேத ஆயுஷ்.',
      te: 'దయచేసి మీ సంప్రదింపు రకాన్ని ఎంచుకోండి: జనరల్ అల్లోపతి లేదా ఆయుర్వేద ఆయుష్.',
    };
    const promptMsg = promptPrompts[language] || promptPrompts.en;
    speak(promptMsg, language);

    return () => {
      stop();
    };
  }, [language, speak, stop]);

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
            {t('mode.badge', language)}
          </span>
          <h1 className="text-3xl md:text-4xl font-black text-[#191c1d] tracking-tight">
            {t('mode.title', language)}
          </h1>
          <p className="text-base text-[#3e4946] mt-2">
            {t('mode.subtitle', language)}
          </p>
        </div>

        {/* 2 High-Impact Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 my-auto">
          <OptionCard
            id="mode-allopathic-card"
            title={t('mode.allopathic', language)}
            subtitle={t('mode.allopathic_desc', language)}
            selected={intakeMode === 'ALLOPATHIC'}
            badge={intakeMode === 'ALLOPATHIC' ? t('mode.active_badge', language) : undefined}
            dataElement="mode-allopathic-card"
            dataVoiceAction="select-allopathic"
            dataVoiceParam="Allopathic"
            onSelect={() => handleSelectMode('ALLOPATHIC')}
            icon={<HealthStethoscope className="w-9 h-9" />}
          />

          <OptionCard
            id="mode-ayush-card"
            title={t('mode.ayush', language)}
            subtitle={t('mode.ayush_desc', language)}
            selected={intakeMode === 'AYUSH'}
            badge={intakeMode === 'AYUSH' ? t('mode.active_badge', language) : undefined}
            dataElement="mode-ayush-card"
            dataVoiceAction="select-ayush"
            dataVoiceParam="Ayurvedic AYUSH"
            onSelect={() => handleSelectMode('AYUSH')}
            icon={<ExerciseYoga className="w-9 h-9" />}
          />
        </div>

        {/* Informational Disclaimer */}
        <div className="p-4 rounded-2xl bg-white border border-[#bdc9c5]/40 text-center text-xs text-[#3e4946] max-w-2xl mx-auto shadow-xs">
          {t('mode.disclaimer', language)}
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
