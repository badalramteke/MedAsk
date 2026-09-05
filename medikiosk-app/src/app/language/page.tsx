/**
 * MediKiosk — Language Selection Screen (/language)
 * Stage 1: Screen 02 per FRONTEND_PAGES_AND_COMPONENTS_SPEC.md.
 * 2x3 Grid of Indian languages with native typography and spoken audio previews.
 */

'use client';

import { useRouter } from 'next/navigation';
import KioskHeader from '@/components/layout/KioskHeader';
import KioskFooter from '@/components/layout/KioskFooter';
import StepProgressBar from '@/components/layout/StepProgressBar';
import OptionCard from '@/components/interactive/OptionCard';
import { useSessionStore } from '@/stores/useSessionStore';
import { useFlowStore } from '@/stores/useFlowStore';
import { useTTS } from '@/hooks/useTTS';
import { SUPPORTED_LANGUAGES, LanguageCode } from '@/lib/constants';
import { t } from '@/lib/i18n';
import { Languages } from 'lucide-react';

const AUDIO_PROMPTS: Record<LanguageCode, string> = {
  en: 'Welcome to MediKiosk. Please tap Next to continue in English.',
  hi: 'MediKiosk में आपका स्वागत है। हिंदी में जारी रखने के लिए आगे टैप करें।',
  mr: 'MediKiosk मध्ये आपले स्वागत आहे. मराठीत सुरू ठेवण्यासाठी पुढे टॅप करा.',
  bn: 'MediKiosk এ আপনাকে স্বাগতম। বাংলায় চালিয়ে যেতে পরবর্তী চাপুন।',
  ta: 'MediKiosk-க்கு வரவேற்கிறோம். தமிழில் தொடர அடுத்து என்பதை அழுத்தவும்.',
  te: 'MediKiosk కు స్వాగతం. తెలుగులో కొనసాగడానికి తదుపరి నొక్కండి.',
};

export default function LanguagePage() {
  const router = useRouter();
  const { language, setLanguage } = useSessionStore();
  const { setCurrentScreen } = useFlowStore();
  const { speak } = useTTS();

  const handleSelect = (code: LanguageCode) => {
    setLanguage(code);
    speak(AUDIO_PROMPTS[code], code);
  };

  const handleProceed = () => {
    setCurrentScreen('mode_selection');
    router.push('/intake/mode-select');
  };

  const handleBack = () => {
    setCurrentScreen('welcome_gate');
    router.push('/');
  };

  return (
    <div className="h-screen w-screen flex flex-col bg-[#f8fafa] overflow-hidden">
      <KioskHeader onBack={handleBack} />
      <StepProgressBar />

      <main className="flex-1 max-w-5xl w-full mx-auto p-6 md:p-10 flex flex-col justify-between overflow-y-auto">
        {/* Title Header */}
        <div className="text-center mb-6">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-[#005f53]/10 text-[#005f53] font-bold text-xs uppercase tracking-wider mb-2">
            <Languages className="w-4 h-4" />
            <span>Multilingual First-Mile Access</span>
          </div>
          <h1 className="text-3xl md:text-4xl font-black text-[#191c1d] tracking-tight">
            {t('language.title', language)}
          </h1>
          <p className="text-base text-[#3e4946] mt-2">
            {t('language.subtitle', language)}
          </p>
        </div>

        {/* 2x3 Language Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4 md:gap-6 my-auto">
          {SUPPORTED_LANGUAGES.map((lang) => {
            const isSelected = language === lang.code;
            return (
              <OptionCard
                key={lang.code}
                id={`lang-card-${lang.code}`}
                title={lang.nativeLabel}
                subtitle={lang.label}
                selected={isSelected}
                badge={isSelected ? t('language.selected', language) : undefined}
                dataElement={`lang-${lang.code}-card`}
                dataVoiceAction={`choose-${lang.code}`}
                onSelect={() => handleSelect(lang.code)}
                onAudioSample={() => speak(AUDIO_PROMPTS[lang.code], lang.code)}
                icon={<span className="text-2xl">{lang.icon}</span>}
              />
            );
          })}
        </div>

        {/* Spacer */}
        <div className="h-4" />
      </main>

      <KioskFooter
        onNext={handleProceed}
        onBack={handleBack}
        nextText={t('nav.continue', language)}
      />
    </div>
  );
}
