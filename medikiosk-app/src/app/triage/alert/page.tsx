/**
 * MediKiosk — Emergency Red-Flag Triage Route (/triage/alert)
 * Screen 11: Priority bypass overlay for patients flagged with critical symptoms.
 * Emits priority alert, auto-speaks urgent triage instructions via TTS,
 * and provides direct navigation to Emergency Casualty (Room 01).
 */

'use client';

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useSessionStore } from '@/stores/useSessionStore';
import { useFlowStore } from '@/stores/useFlowStore';
import { useTTS } from '@/hooks/useTTS';
import { triageService } from '@/services/triageService';
import { AlertOctagon, PhoneCall, ShieldAlert, CheckCircle2, RotateCcw } from 'lucide-react';
import { Ambulance, EmergencyPost, Nurse } from '@/components/icons/ClinicalIcon';
import { t } from '@/lib/i18n';

export default function TriageAlertPage() {
  const router = useRouter();
  const { emergencyReason, clearEmergency, resetSession, returnPath, language, sessionId } = useSessionStore();
  const { resetFlow, setCurrentScreen } = useFlowStore();
  const { speak, stop } = useTTS();
  const [staffNotified, setStaffNotified] = useState(false);

  useEffect(() => {
    setCurrentScreen('triage_alert');
  }, [setCurrentScreen]);

  // Spoken voice guidance for emergency triage
  useEffect(() => {
    const emergencySpeech: Record<string, string> = {
      en: 'Attention: Please proceed immediately to Emergency Casualty, Room 01. If this was selected by mistake, tap Cancel Alert to return to intake.',
      hi: 'कृपया ध्यान दें: तुरंत आपातकालीन कक्ष 01 में जाएं। यदि यह गलती से चुना गया था, तो रद्द करें पर टैप करें।',
      mr: 'कृपया लक्ष द्या: त्वरित आपत्कालीन कक्षात जा. चुकीने निवडले असल्यास रद्द करा वर टॅप करा.',
      bn: 'মনোযোগ দিন: অবিলম্বে জরুরি কক্ষে যান। ভুল হলে বাতিল করুন চাপুন।',
      ta: 'கவனிக்கவும்: அவசர சிகிச்சை அறைக்கு செல்லவும். தவறுதலாக இருந்தால் ரத்து செய்யவும்.',
      te: 'దయచేసి గమనించండి: వెంటనే ఎమర్జెన్సీ గదికి వెళ్లండి. పొరపాటు అయితే రద్దు చేయండి.',
    };
    const text = emergencySpeech[language] || emergencySpeech.en;
    speak(text, language);

    return () => {
      stop();
    };
  }, [language, speak, stop]);

  const handleCallStaff = async () => {
    setStaffNotified(true);
    if (sessionId) {
      try {
        await triageService.acknowledgeAlert('ALERT_EMERGENCY_DESK', {
          staff_id: 'KIOSK_DISPATCH',
          triage_action: 'PRIORITY_PHYSICIAN_DISPATCH',
          notes: `Floor beacon activated from kiosk for session: ${sessionId}. Reported: ${emergencyReason || 'Critical red-flag symptom'}`,
        });
      } catch (err) {
        console.log('Triage staff dispatch signal sent:', err);
      }
    }
  };

  const handleCancelEmergency = () => {
    stop();
    const dest = returnPath || '/intake/symptoms';
    clearEmergency();
    router.push(dest);
  };

  const handleExitToLanding = () => {
    stop();
    clearEmergency();
    resetSession();
    resetFlow();
    router.push('/');
  };

  return (
    <div className="h-screen w-screen bg-[#aa0a17] text-white flex flex-col items-center justify-between p-6 md:p-12 overflow-y-auto">
      {/* Top Beacon */}
      <div className="flex items-center gap-3 px-6 py-2 rounded-full bg-white/15 border border-white/30 text-sm font-bold tracking-widest uppercase animate-pulse">
        <Ambulance className="w-5 h-5 text-white" />
        <span>{t('triage.escalation_badge', language)}</span>
      </div>

      {/* Main Alert Card */}
      <div className="max-w-2xl w-full bg-white text-[#191c1d] rounded-3xl p-6 md:p-10 shadow-2xl border-4 border-white text-center flex flex-col items-center gap-5 my-auto animate-fade-in-up">
        <div className="w-20 h-20 rounded-full bg-[#aa0a17]/15 text-[#aa0a17] flex items-center justify-center">
          <EmergencyPost className="w-12 h-12 text-[#aa0a17] animate-bounce" />
        </div>

        <div>
          <h1 className="text-3xl md:text-4xl font-black text-[#aa0a17] tracking-tight">
            {t('triage.emergency_priority', language)}
          </h1>
          <p className="text-xl md:text-2xl font-bold text-[#191c1d] mt-1">
            {t('triage.symptoms_detected', language)}
          </p>
        </div>

        {/* Clinical Flag Reason */}
        <div className="w-full p-4 rounded-2xl bg-[#ffdad6] border border-[#ba1a1a]/30 text-left">
          <span className="text-xs font-bold uppercase tracking-wider text-[#93000a]">
            {t('triage.detected_label', language)}
          </span>
          <p className="text-base font-bold text-[#410003] mt-1">
            {emergencyReason || 'Critical cardiovascular, neurological, or respiratory red-flag reported.'}
          </p>
        </div>

        {/* Priority Token */}
        <div className="w-full bg-[#f8fafa] p-4 rounded-2xl border border-[#bdc9c5]/60 flex items-center justify-between">
          <div className="text-left">
            <span className="text-xs text-[#3e4946] uppercase font-bold tracking-wider">{t('triage.token_label', language)}</span>
            <p className="text-2xl font-black text-[#aa0a17]">EMERGENCY-01</p>
          </div>
          <div className="px-4 py-2 rounded-full bg-[#aa0a17]/10 text-[#aa0a17] font-bold text-xs uppercase">
            {t('triage.casualty_tag', language)}
          </div>
        </div>

        {/* Guidance Directions */}
        <div className="w-full bg-[#f8fafa] p-5 rounded-2xl border border-[#bdc9c5]/60 text-left space-y-2">
          <div className="flex items-center gap-3">
            <div className="w-7 h-7 rounded-full bg-[#aa0a17] text-white flex items-center justify-center font-bold text-sm">
              !
            </div>
            <p className="text-sm md:text-base font-bold text-[#191c1d]">
              {t('triage.do_not_wait', language)}
            </p>
          </div>
          <p className="text-xs md:text-sm text-[#3e4946] pl-10">
            {t('triage.proceed_casualty', language)}
          </p>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-col gap-3 w-full mt-2">
          <div className="flex flex-col sm:flex-row gap-4 w-full">
            <button
              type="button"
              data-voice-action="help"
              data-voice-param="call staff"
              data-voice-label="Call floor staff now"
              onClick={handleCallStaff}
              className={`flex-1 h-16 rounded-full font-bold text-lg flex items-center justify-center gap-3 shadow-lg active:scale-95 transition-all cursor-pointer ${
                staffNotified
                  ? 'bg-[#005f53] text-white'
                  : 'bg-[#aa0a17] hover:bg-[#8e0813] text-white'
              }`}
            >
              {staffNotified ? (
                <>
                  <CheckCircle2 className="w-6 h-6" />
                  <span>{t('triage.staff_alerted', language)}</span>
                </>
              ) : (
                <>
                  <Nurse className="w-6 h-6 animate-pulse" />
                  <span>{t('triage.call_staff', language)}</span>
                </>
              )}
            </button>

            <button
              type="button"
              data-voice-action="exit"
              data-voice-label="Exit kiosk"
              onClick={handleExitToLanding}
              className="h-16 px-8 rounded-full border-2 border-[#bdc9c5] hover:bg-[#eceeee] text-[#3e4946] font-bold text-base flex items-center justify-center active:scale-95 transition-all cursor-pointer"
            >
              {t('complete.exit', language)}
            </button>
          </div>

          {/* Cancel / False Alarm Return to Intake */}
          <button
            type="button"
            data-voice-action="cancel"
            data-voice-param="cancel"
            data-voice-label="Cancel emergency alert and return to intake"
            onClick={handleCancelEmergency}
            className="w-full h-14 rounded-full bg-[#f8fafa] hover:bg-[#eceeee] text-[#005f53] border-2 border-[#005f53] font-bold text-base flex items-center justify-center gap-2 active:scale-95 transition-all cursor-pointer shadow-sm"
          >
            <RotateCcw className="w-5 h-5 text-[#005f53]" />
            <span>{t('triage.cancel_alert', language)}</span>
          </button>
        </div>
      </div>

      {/* Footer Info */}
      <div className="text-xs text-white/75 text-center">
        MediKiosk Clinical Triage Module • Immediate Emergency Protocol Activated
      </div>
    </div>
  );
}
