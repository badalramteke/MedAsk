/**
 * MediKiosk — DPDP & ABDM Granular Consent Screen (/consent)
 * Screen 04: Compliant affirmative consent capture under DPDP Act 2023.
 * Integrated with backend consent engine.
 */

'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import KioskHeader from '@/components/layout/KioskHeader';
import KioskFooter from '@/components/layout/KioskFooter';
import StepProgressBar from '@/components/layout/StepProgressBar';
import { useSessionStore } from '@/stores/useSessionStore';
import { useFlowStore } from '@/stores/useFlowStore';
import { useTTS } from '@/hooks/useTTS';
import { consentService } from '@/services/consentService';
import { t } from '@/lib/i18n';
import { ShieldCheck, Volume2, Check, Lock, FileText, Share2, Sparkles } from 'lucide-react';
import {
  HealthStethoscope,
  PrescriptionDocument,
  MedicalRecords,
  HospitalSymbol,
  SecurityWorker,
} from '@/components/icons/ClinicalIcon';

export default function ConsentPage() {
  const router = useRouter();
  const { language, sessionId, setConsent } = useSessionStore();
  const { setCurrentScreen } = useFlowStore();
  const { speak, isSpeaking } = useTTS();

  useEffect(() => {
    setCurrentScreen('consent_capture');
  }, [setCurrentScreen]);

  const [scopes, setScopes] = useState({
    intake: true,
    documents: true,
    summary: true,
    hisShare: true,
  });

  const toggleScope = (key: keyof typeof scopes) => {
    setScopes((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  const handlePlayAudio = async () => {
    const audioNotice = t('consent.audio_notice', language);
    if (sessionId) {
      try {
        const script = await consentService.getAudioScript(sessionId, 'INTAKE', language);
        speak(script.audio_script || audioNotice);
        return;
      } catch {
        // Fallback
      }
    }
    speak(audioNotice);
  };

  const handleAgree = () => {
    setConsent(true);
    setCurrentScreen('chief_complaint');
    router.push('/intake/symptoms');

    if (sessionId) {
      consentService
        .grantConsent(sessionId, {
          scope: 'FULL_HIS_SHARE',
          interaction_mode: 'TOUCH_SCREEN',
          language,
        })
        .catch((err) => {
          console.warn('Consent background sync note:', err);
        });
    }
  };

  const handleDecline = () => {
    setConsent(false);
    setCurrentScreen('chief_complaint');
    router.push('/intake/symptoms');
  };

  const handleBack = () => {
    setCurrentScreen('patient_identification');
    router.push('/auth');
  };

  return (
    <div className="h-screen w-screen flex flex-col bg-[#f8fafa] overflow-hidden">
      <KioskHeader onBack={handleBack} />
      <StepProgressBar />

      <main className="flex-1 max-w-4xl w-full mx-auto p-6 md:p-8 flex flex-col justify-between overflow-y-auto">
        {/* Title & Trust Badge */}
        <div className="text-center mb-4">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-[#006e1c]/10 text-[#006e1c] font-bold text-xs uppercase tracking-wider mb-2">
            <SecurityWorker className="w-4 h-4" />
            <span>{t('consent.badge', language)}</span>
          </div>
          <h1 className="text-3xl md:text-4xl font-black text-[#191c1d] tracking-tight">
            {t('consent.title', language)}
          </h1>
          <p className="text-sm text-[#3e4946] mt-2 max-w-xl mx-auto">
            {t('consent.subtitle', language)}
          </p>

          {/* Vernacular Audio Guidance Button */}
          <button
            type="button"
            id="kiosk-consent-audio-btn"
            data-element="consent-audio-play-btn"
            data-voice-action="play-consent-audio"
            data-testid="consent-audio-play-btn"
            aria-label="Listen to consent explanation"
            onClick={handlePlayAudio}
            className="inline-flex items-center gap-2 mt-4 px-5 py-2.5 rounded-full bg-[#eceeee] hover:bg-[#e1e3e3] text-[#005f53] font-bold text-sm transition-all cursor-pointer shadow-xs active:scale-95"
          >
            <Volume2 className={`w-4 h-4 ${isSpeaking ? 'animate-bounce text-[#aa0a17]' : ''}`} />
            <span>{isSpeaking ? t('consent.playing_btn', language) : t('consent.listen_btn', language)}</span>
          </button>
        </div>

        {/* 4 Granular Scope Cards */}
        <div className="space-y-3 my-auto">
          {/* Scope 1: Clinical Intake */}
          <div
            onClick={() => toggleScope('intake')}
            className={`p-4 rounded-2xl border flex items-center justify-between transition-all cursor-pointer ${
              scopes.intake
                ? 'bg-white border-[#005f53] shadow-xs'
                : 'bg-[#f2f4f4] border-[#bdc9c5]/60 opacity-60'
            }`}
          >
            <div className="flex items-center gap-4">
              <div className="w-10 h-10 rounded-xl bg-[#005f53]/10 text-[#005f53] flex items-center justify-center">
                <HealthStethoscope className="w-6 h-6" />
              </div>
              <div>
                <h4 className="font-bold text-base text-[#191c1d]">
                  {t('consent.scope1_title', language)}
                </h4>
                <p className="text-xs text-[#3e4946]">
                  {t('consent.scope1_desc', language)}
                </p>
              </div>
            </div>
            <div
              className={`w-7 h-7 rounded-lg flex items-center justify-center border ${
                scopes.intake
                  ? 'bg-[#005f53] border-transparent text-white'
                  : 'border-[#bdc9c5] bg-white'
              }`}
            >
              {scopes.intake && <Check className="w-4 h-4" />}
            </div>
          </div>

          {/* Scope 2: Document Scanning */}
          <div
            onClick={() => toggleScope('documents')}
            className={`p-4 rounded-2xl border flex items-center justify-between transition-all cursor-pointer ${
              scopes.documents
                ? 'bg-white border-[#005f53] shadow-xs'
                : 'bg-[#f2f4f4] border-[#bdc9c5]/60 opacity-60'
            }`}
          >
            <div className="flex items-center gap-4">
              <div className="w-10 h-10 rounded-xl bg-[#005f53]/10 text-[#005f53] flex items-center justify-center">
                <PrescriptionDocument className="w-6 h-6" />
              </div>
              <div>
                <h4 className="font-bold text-base text-[#191c1d]">
                  {t('consent.scope2_title', language)}
                </h4>
                <p className="text-xs text-[#3e4946]">
                  {t('consent.scope2_desc', language)}
                </p>
              </div>
            </div>
            <div
              className={`w-7 h-7 rounded-lg flex items-center justify-center border ${
                scopes.documents
                  ? 'bg-[#005f53] border-transparent text-white'
                  : 'border-[#bdc9c5] bg-white'
              }`}
            >
              {scopes.documents && <Check className="w-4 h-4" />}
            </div>
          </div>

          {/* Scope 3: Summary Synthesis */}
          <div
            onClick={() => toggleScope('summary')}
            className={`p-4 rounded-2xl border flex items-center justify-between transition-all cursor-pointer ${
              scopes.summary
                ? 'bg-white border-[#005f53] shadow-xs'
                : 'bg-[#f2f4f4] border-[#bdc9c5]/60 opacity-60'
            }`}
          >
            <div className="flex items-center gap-4">
              <div className="w-10 h-10 rounded-xl bg-[#005f53]/10 text-[#005f53] flex items-center justify-center">
                <MedicalRecords className="w-6 h-6" />
              </div>
              <div>
                <h4 className="font-bold text-base text-[#191c1d]">
                  {t('consent.scope3_title', language)}
                </h4>
                <p className="text-xs text-[#3e4946]">
                  {t('consent.scope3_desc', language)}
                </p>
              </div>
            </div>
            <div
              className={`w-7 h-7 rounded-lg flex items-center justify-center border ${
                scopes.summary
                  ? 'bg-[#005f53] border-transparent text-white'
                  : 'border-[#bdc9c5] bg-white'
              }`}
            >
              {scopes.summary && <Check className="w-4 h-4" />}
            </div>
          </div>

          {/* Scope 4: ABDM & HIS Sharing */}
          <div
            onClick={() => toggleScope('hisShare')}
            className={`p-4 rounded-2xl border flex items-center justify-between transition-all cursor-pointer ${
              scopes.hisShare
                ? 'bg-white border-[#005f53] shadow-xs'
                : 'bg-[#f2f4f4] border-[#bdc9c5]/60 opacity-60'
            }`}
          >
            <div className="flex items-center gap-4">
              <div className="w-10 h-10 rounded-xl bg-[#005f53]/10 text-[#005f53] flex items-center justify-center">
                <HospitalSymbol className="w-6 h-6" />
              </div>
              <div>
                <h4 className="font-bold text-base text-[#191c1d]">
                  {t('consent.scope4_title', language)}
                </h4>
                <p className="text-xs text-[#3e4946]">
                  {t('consent.scope4_desc', language)}
                </p>
              </div>
            </div>
            <div
              className={`w-7 h-7 rounded-lg flex items-center justify-center border ${
                scopes.hisShare
                  ? 'bg-[#005f53] border-transparent text-white'
                  : 'border-[#bdc9c5] bg-white'
              }`}
            >
              {scopes.hisShare && <Check className="w-4 h-4" />}
            </div>
          </div>
        </div>

        {/* Ephemeral Notice */}
        <div className="p-3 rounded-2xl bg-[#005f53]/5 border border-[#005f53]/20 text-center text-xs text-[#005f53] font-semibold my-2">
          {t('consent.disclaimer', language)}
        </div>
      </main>

      <KioskFooter
        onNext={handleAgree}
        onBack={handleBack}
        nextText={t('consent.agree', language)}
      />
    </div>
  );
}
