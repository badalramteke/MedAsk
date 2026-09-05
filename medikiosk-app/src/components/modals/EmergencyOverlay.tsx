/**
 * MediKiosk — Emergency Red-Flag Triage Overlay
 * High-urgency flashing warning triggered when severe clinical symptoms are detected
 * (e.g. acute crushing chest pain, acute respiratory distress, stroke signs).
 */

'use client';

import { useSessionStore } from '@/stores/useSessionStore';
import { AlertOctagon, PhoneCall, CheckCircle, ArrowRight } from 'lucide-react';

interface EmergencyOverlayProps {
  reason?: string;
  onStaffCalled?: () => void;
  onDismiss?: () => void;
}

export default function EmergencyOverlay({
  reason,
  onStaffCalled,
  onDismiss,
}: EmergencyOverlayProps) {
  const { isEmergency, emergencyReason, clearEmergency } = useSessionStore();

  if (!isEmergency) return null;

  const displayReason =
    reason ||
    emergencyReason ||
    'Critical symptom reported: immediate clinical assessment required.';

  const handleDismiss = () => {
    clearEmergency();
    if (onDismiss) onDismiss();
  };

  return (
    <div
      id="emergency-triage-modal"
      data-element="emergency-triage-overlay"
      data-testid="emergency-triage-overlay"
      className="fixed inset-0 z-50 bg-[#aa0a17]/90 backdrop-blur-md flex items-center justify-center p-6"
    >
      <div className="bg-white rounded-3xl max-w-2xl w-full p-8 md:p-12 shadow-2xl border-4 border-[#aa0a17] text-center flex flex-col items-center gap-6 animate-emergency-flash">
        {/* Pulsing Emergency Icon */}
        <div className="w-24 h-24 rounded-full bg-[#ce2b2c]/15 flex items-center justify-center">
          <AlertOctagon className="w-14 h-14 text-[#aa0a17] animate-pulse" />
        </div>

        <div>
          <h2 className="text-3xl md:text-4xl font-black text-[#aa0a17] tracking-tight">
            EMERGENCY SYMPTOM DETECTED
          </h2>
          <p className="text-xl md:text-2xl font-bold text-[#191c1d] mt-2">
            आपातकालीन लक्षण पहचाने गए
          </p>
        </div>

        {/* Reason Card */}
        <div className="w-full p-4 rounded-2xl bg-[#ffdad6]/60 border border-[#ba1a1a]/30 text-left">
          <span className="text-xs font-bold uppercase tracking-wider text-[#93000a]">
            Clinical Red-Flag Trigger:
          </span>
          <p className="text-base font-semibold text-[#410003] mt-1">
            {displayReason}
          </p>
        </div>

        {/* Action Instructions */}
        <div className="text-left w-full space-y-3 bg-[#f8fafa] p-5 rounded-2xl border border-[#bdc9c5]/40">
          <div className="flex items-start gap-3">
            <div className="w-7 h-7 rounded-full bg-[#005f53] text-white flex items-center justify-center font-bold text-sm flex-shrink-0 mt-0.5">
              1
            </div>
            <p className="text-base font-medium text-[#191c1d]">
              Please proceed immediately to the <strong>Emergency Room / Triage Desk</strong>.
            </p>
          </div>
          <div className="flex items-start gap-3">
            <div className="w-7 h-7 rounded-full bg-[#005f53] text-white flex items-center justify-center font-bold text-sm flex-shrink-0 mt-0.5">
              2
            </div>
            <p className="text-base font-medium text-[#191c1d]">
              An automated high-priority alert has been dispatched to the nursing triage station.
            </p>
          </div>
        </div>

        {/* Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 w-full mt-2">
          <button
            type="button"
            id="triage-call-nurse-btn"
            data-element="triage-call-nurse-btn"
            data-voice-action="call-nurse"
            data-testid="triage-call-nurse-btn"
            onClick={onStaffCalled}
            className="flex-1 h-16 rounded-full bg-[#aa0a17] hover:bg-[#8e0813] text-white font-bold text-lg flex items-center justify-center gap-3 shadow-lg active:scale-95 transition-all cursor-pointer"
          >
            <PhoneCall className="w-6 h-6 animate-bounce" />
            <span>Call Floor Nurse</span>
          </button>

          <button
            type="button"
            id="triage-dismiss-btn"
            data-element="triage-exit-btn"
            data-voice-action="dismiss-alert"
            data-testid="triage-dismiss-btn"
            onClick={handleDismiss}
            className="h-16 px-8 rounded-full border-2 border-[#bdc9c5] hover:bg-[#eceeee] text-[#3e4946] font-bold text-base flex items-center justify-center active:scale-95 transition-all cursor-pointer"
          >
            <span>Acknowledge & Exit</span>
          </button>
        </div>
      </div>
    </div>
  );
}
