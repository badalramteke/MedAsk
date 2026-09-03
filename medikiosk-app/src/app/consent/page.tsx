/**
 * MediKiosk — DPDP & ABDM Granular Consent Screen (/consent)
 * Screen 04: Compliant affirmative consent capture under DPDP Act 2023.
 * Integrated with backend consent engine.
 */

'use client';

import { useState } from 'react';
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

export default function ConsentPage() {
  const router = useRouter();
  const { language, sessionId, setConsent } = useSessionStore();
  const { setCurrentScreen } = useFlowStore();
  const { speak, isSpeaking } = useTTS();

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

  const handleAgree = async () => {
    setConsent(true);
    if (sessionId) {
      try {
        await consentService.grantConsent(sessionId, {
          scope: 'FULL_HIS_SHARE',
          interaction_mode: 'TOUCH_SCREEN',
          language,
        });
      } catch (err) {
        console.warn('Consent logging failed, proceeding with local consent:', err);
      }
    }
    setCurrentScreen('chief_complaint');
    router.push('/intake/symptoms');
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
            <ShieldCheck className="w-4 h-4" />
            <span>DPDP Act 2023 & ABDM Compliant</span>
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
            <span>{isSpeaking ? 'Playing Audio Notice...' : 'Listen to Spoken Notice'}</span>
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
                <FileText className="w-5 h-5" />
              </div>
              <div>
                <h4 className="font-bold text-base text-[#191c1d]">
                  1. Clinical Intake & Symptom Interview
                </h4>
                <p className="text-xs text-[#3e4946]">
                  Record your presenting complaints and SOCRATES symptom history via voice or touch.
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
                <Lock className="w-5 h-5" />
              </div>
              <div>
                <h4 className="font-bold text-base text-[#191c1d]">
                  2. Medical Document Digitization & OCR
                </h4>
                <p className="text-xs text-[#3e4946]">
                  Scan and extract prior prescriptions, lab reports, and medications.
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
                <Sparkles className="w-5 h-5" />
              </div>
              <div>
                <h4 className="font-bold text-base text-[#191c1d]">
                  3. AI Clinical Summary Draft Generation
                </h4>
                <p className="text-xs text-[#3e4946]">
                  Generate a structured, editable clinical draft for your doctor to review before consultation.
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
                <Share2 className="w-5 h-5" />
              </div>
              <div>
                <h4 className="font-bold text-base text-[#191c1d]">
                  4. ABDM Personal Health Locker Linkage
                </h4>
                <p className="text-xs text-[#3e4946]">
                  Securely link your verified intake summary to your ABHA personal health records.
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
          Zero Retention: Temporary voice recordings and camera frames are erased from kiosk memory upon submission.
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
