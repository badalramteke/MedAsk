/**
 * MediKiosk — Landing & Attractor Screen (/)
 * Stage 0: Welcome Gate
 * Compliant with PATHS.md and FRONTEND_PAGES_AND_COMPONENTS_SPEC.md Screen 01.
 */

'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import KioskHeader from '@/components/layout/KioskHeader';
import { useSessionStore } from '@/stores/useSessionStore';
import { useFlowStore } from '@/stores/useFlowStore';
import { useTTS } from '@/hooks/useTTS';
import { SUPPORTED_LANGUAGES, LanguageCode } from '@/lib/constants';
import { t } from '@/lib/i18n';
import { ArrowRight, Touchpad, Volume2, ShieldCheck, HeartPulse, Clock, Sparkles } from 'lucide-react';

export default function LandingPage() {
  const router = useRouter();
  const { language, setLanguage, startSession, ensureBackendSession } = useSessionStore();
  const { setCurrentScreen } = useFlowStore();
  const { speak, isSpeaking } = useTTS();
  const [activeLang, setActiveLang] = useState<LanguageCode>(language);

  const [isLoading, setIsLoading] = useState(false);

  const handleStart = async (chosenLang?: LanguageCode) => {
    if (isLoading) return;
    setIsLoading(true);
    try {
      const selected = chosenLang || activeLang;
      setLanguage(selected);
      await ensureBackendSession(selected);
      setCurrentScreen('language_picker');
      router.push('/language');
    } catch (err) {
      console.error('Failed to start session', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAudioWelcome = () => {
    const welcomeMsg = t('welcome.audio_greeting', activeLang);
    speak(welcomeMsg, activeLang);
  };

  return (
    <div className="h-screen w-screen flex flex-col bg-[#f8fafa] overflow-hidden">
      {/* Header */}
      <KioskHeader showBack={false} />

      {/* Main Split Layout */}
      <main className="flex-1 w-full flex flex-col md:flex-row overflow-hidden">
        {/* Left Hero Area: Hospital Visual & Value Proposition */}
        <div className="flex-1 relative bg-gradient-to-br from-[#005f53] via-[#0f7a6b] to-[#003d33] p-8 md:p-14 flex flex-col justify-between text-white overflow-hidden">
          {/* Subtle decorative background circles */}
          <div className="absolute -top-24 -left-24 w-96 h-96 rounded-full bg-white/5 blur-3xl pointer-events-none" />
          <div className="absolute -bottom-24 -right-24 w-96 h-96 rounded-full bg-[#99f3e0]/10 blur-3xl pointer-events-none" />

          {/* Top Tagline */}
          <div className="relative z-10 flex items-center gap-2">
            <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-white/10 backdrop-blur-md border border-white/20 text-xs font-bold uppercase tracking-wider text-[#abffed]">
              <Sparkles className="w-4 h-4 text-[#99f3e0]" />
              <span>Ministry of Ayush & AIIA Smart OPD</span>
            </div>
          </div>

          {/* Center Headline */}
          <div className="relative z-10 max-w-xl my-auto py-6">
            <h1 className="text-4xl sm:text-5xl md:text-6xl font-black tracking-tight leading-tight mb-4">
              Your Health, <br />
              <span className="text-[#99f3e0]">Our Priority.</span>
            </h1>
            <p className="text-lg md:text-xl text-white/85 font-medium leading-relaxed mb-6">
              Complete your clinical intake and prescription scan in minutes before meeting your doctor.
            </p>

            {/* Key badges */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2">
              <div className="flex items-center gap-3 p-3 rounded-2xl bg-white/10 backdrop-blur-xs border border-white/10">
                <HeartPulse className="w-6 h-6 text-[#99f3e0] flex-shrink-0" />
                <span className="text-sm font-semibold">Dual-Mode Voice & Touch</span>
              </div>
              <div className="flex items-center gap-3 p-3 rounded-2xl bg-white/10 backdrop-blur-xs border border-white/10">
                <ShieldCheck className="w-6 h-6 text-[#99f3e0] flex-shrink-0" />
                <span className="text-sm font-semibold">ABDM & DPDP Act 2023</span>
              </div>
            </div>
          </div>

          {/* Bottom Hospital Trust */}
          <div className="relative z-10 flex items-center gap-4 text-xs text-white/70 border-t border-white/10 pt-4">
            <Clock className="w-4 h-4" />
            <span>Average intake time: 2–3 minutes • Zero technical skills required</span>
          </div>
        </div>

        {/* Right Interaction Zone: Language Switcher & Massive Start Button */}
        <div className="w-full md:w-[480px] lg:w-[540px] bg-white p-8 md:p-12 flex flex-col justify-between items-center border-l border-[#bdc9c5]/30 shadow-xl overflow-y-auto">
          {/* Top Info */}
          <div className="w-full flex flex-col items-center text-center">
            <div className="w-20 h-20 rounded-3xl bg-[#005f53]/10 text-[#005f53] flex items-center justify-center mb-5 shadow-xs">
              <Touchpad className="w-10 h-10" />
            </div>

            <h2 className="text-2xl md:text-3xl font-black text-[#191c1d] tracking-tight">
              Ready to check in?
            </h2>
            <p className="text-base text-[#3e4946] mt-2 max-w-sm">
              Tap the screen below to begin in your preferred language.
            </p>

            {/* Quick Language Chips */}
            <div
              id="kiosk-lang-quick-select"
              data-element="language-quick-select"
              className="flex flex-wrap justify-center gap-2 mt-6"
            >
              {SUPPORTED_LANGUAGES.map((lang) => {
                const isSelected = activeLang === lang.code;
                return (
                  <button
                    key={lang.code}
                    type="button"
                    disabled={isLoading}
                    onClick={() => {
                      setActiveLang(lang.code);
                      setLanguage(lang.code);
                    }}
                    className={`px-4 py-2 rounded-full font-bold text-sm transition-all cursor-pointer border ${
                      isSelected
                        ? 'bg-[#005f53] text-white border-transparent shadow-md scale-105'
                        : 'bg-[#f2f4f4] hover:bg-[#eceeee] text-[#191c1d] border-[#bdc9c5]/40'
                    } ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
                  >
                    <span>{lang.nativeLabel}</span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Center: Massive Pulsing Action Button */}
          <div className="w-full my-6">
            <button
              id="kiosk-start-btn"
              data-element="welcome-start-btn"
              data-voice-action="start-intake"
              data-testid="welcome-start-btn"
              aria-label="Tap to start patient check-in"
              onClick={() => handleStart()}
              disabled={isLoading}
              className={`w-full h-24 md:h-28 rounded-3xl bg-[#005f53] hover:bg-[#0c6b5e] text-white flex items-center justify-between px-8 shadow-2xl transition-all group ${
                isLoading ? 'opacity-80 cursor-wait' : 'animate-pulse-glow active:scale-98 cursor-pointer'
              }`}
            >
              <div className="flex flex-col items-start text-left">
                <span className="text-2xl md:text-3xl font-black tracking-tight">
                  {isLoading ? 'Starting...' : t('welcome.tap_to_start', activeLang)}
                </span>
                <span className="text-sm font-medium text-white/80">
                  {isLoading ? 'Please wait a moment' : 'Touch anywhere to begin'}
                </span>
              </div>
              <div className={`w-14 h-14 rounded-full bg-white/20 flex items-center justify-center transition-transform ${isLoading ? 'animate-spin' : 'group-hover:translate-x-2'}`}>
                {isLoading ? (
                  <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                ) : (
                  <ArrowRight className="w-8 h-8 text-white" />
                )}
              </div>
            </button>
          </div>

          {/* Bottom Audio Guidance Trigger */}
          <div className="w-full flex flex-col items-center gap-4">
            <button
              id="kiosk-audio-welcome-btn"
              data-element="help-audio-btn"
              data-voice-action="play-welcome-audio"
              data-testid="help-audio-btn"
              aria-label="Listen to audio greeting"
              onClick={handleAudioWelcome}
              disabled={isLoading}
              className={`flex items-center gap-2 px-5 py-3 rounded-full bg-[#eceeee] hover:bg-[#e1e3e3] text-[#005f53] text-sm font-bold transition-colors active:scale-95 ${
                isLoading ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'
              }`}
            >
              <Volume2 className={`w-5 h-5 ${isSpeaking ? 'animate-bounce text-[#aa0a17]' : ''}`} />
              <span>{isSpeaking ? 'Playing guidance...' : 'Listen in vernacular audio'}</span>
            </button>

            <span className="text-xs text-[#3e4946]">
              Press red SOS button at top-right for urgent clinical care
            </span>
          </div>
        </div>
      </main>
    </div>
  );
}
