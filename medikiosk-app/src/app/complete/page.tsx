/**
 * MediKiosk — Intake Complete & OPD Queue Token (/complete)
 * Screen 12: Final receipt-style screen with token number, assigned doctor room,
 * and 30-second ephemeral session purge countdown.
 */

'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import KioskHeader from '@/components/layout/KioskHeader';
import { useSessionStore } from '@/stores/useSessionStore';
import { useFlowStore } from '@/stores/useFlowStore';
import { useIntakeStore } from '@/stores/useIntakeStore';
import { t } from '@/lib/i18n';
import { CheckCircle2, Printer, LogOut, QrCode, Clock, ShieldCheck } from 'lucide-react';
import { Positive, HealthQrCode, Doctor, HospitalSymbol } from '@/components/icons/ClinicalIcon';

export default function CompletePage() {
  const router = useRouter();
  const {
    language,
    tokenNumber,
    assignedRoom,
    patientName,
    resetSession,
  } = useSessionStore();
  const { resetFlow, setCurrentScreen } = useFlowStore();
  const { resetIntake } = useIntakeStore();

  useEffect(() => {
    setCurrentScreen('intake_complete');
  }, [setCurrentScreen]);

  const [purgeCountdown, setPurgeCountdown] = useState(30);

  // Auto-purge timer (DPDP Act compliance)
  useEffect(() => {
    const timer = setInterval(() => {
      setPurgeCountdown((prev) => {
        if (prev <= 1) {
          clearInterval(timer);
          handleFinish();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  const handleFinish = () => {
    resetSession();
    resetFlow();
    resetIntake();
    router.push('/');
  };

  const handlePrint = () => {
    if (typeof window !== 'undefined') {
      window.print();
    }
  };

  const activeToken = tokenNumber || 'A-442';
  const activeRoom = assignedRoom || 'Room 106 — Dr. Arvind Kumar (Cardiology OPD)';

  return (
    <div className="h-screen w-screen flex flex-col bg-[#f8fafa] overflow-hidden">
      <KioskHeader showBack={false} />

      <main className="flex-1 max-w-xl w-full mx-auto p-6 md:p-10 flex flex-col justify-between items-center overflow-y-auto">
        {/* Success Header */}
        <div className="text-center">
          <div className="w-16 h-16 rounded-full bg-[#006e1c]/10 text-[#006e1c] flex items-center justify-center mx-auto mb-3">
            <Positive className="w-10 h-10 text-[#006e1c]" />
          </div>
          <h1 className="text-3xl font-black text-[#191c1d] tracking-tight">
            {t('complete.title', language)}
          </h1>
          <p className="text-sm text-[#3e4946] mt-1">
            {t('complete.subtitle', language)}
          </p>
        </div>

        {/* Receipt Token Card */}
        <div className="w-full bg-white rounded-3xl p-6 md:p-8 border-2 border-[#005f53] shadow-xl text-center my-4 space-y-4">
          <div className="text-xs font-bold uppercase tracking-widest text-[#005f53]">
            {t('complete.queue_token', language)}
          </div>

          <div className="text-6xl md:text-7xl font-black text-[#005f53] tracking-tight">
            {activeToken}
          </div>

          <div className="h-px w-full bg-dashed border-t border-[#bdc9c5] my-2" />

          <div className="space-y-1 text-sm">
            <div className="font-bold text-base text-[#191c1d]">
              {activeRoom}
            </div>
            <div className="text-xs text-[#3e4946]">
              {t('complete.patient', language)} {patientName || t('complete.walkin_guest', language)}
            </div>
          </div>

          {/* Rapid QR Scan for Doctor */}
          <div className="p-3 bg-[#f2f4f4] rounded-2xl flex items-center justify-center gap-3">
            <HealthQrCode className="w-10 h-10 text-[#005f53]" />
            <span className="text-xs text-left font-medium text-[#3e4946]">
              {t('complete.show_screen', language)}
            </span>
          </div>
        </div>

        {/* Ephemeral Session Purge Notice */}
        <div className="w-full p-4 rounded-2xl bg-[#005f53]/5 border border-[#005f53]/20 flex items-center justify-between text-xs text-[#005f53]">
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-5 h-5 flex-shrink-0" />
            <span>{t('complete.purge_notice', language)}</span>
          </div>
          <span className="font-black text-sm bg-white px-2.5 py-1 rounded-full shadow-xs">
            {purgeCountdown}s
          </span>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-3 w-full mt-4">
          <button
            type="button"
            onClick={handlePrint}
            className="flex-1 h-14 rounded-full border-2 border-[#005f53] hover:bg-[#005f53]/10 text-[#005f53] font-bold text-sm md:text-base flex items-center justify-center gap-2 active:scale-95 transition-transform cursor-pointer"
          >
            <Printer className="w-5 h-5" />
            <span>{t('complete.print', language)}</span>
          </button>

          <button
            type="button"
            onClick={handleFinish}
            className="flex-1 h-14 rounded-full bg-[#005f53] hover:bg-[#0c6b5e] text-white font-bold text-sm md:text-base flex items-center justify-center gap-2 active:scale-95 transition-transform cursor-pointer shadow-md"
          >
            <LogOut className="w-5 h-5" />
            <span>{t('complete.exit', language)}</span>
          </button>
        </div>
      </main>
    </div>
  );
}
