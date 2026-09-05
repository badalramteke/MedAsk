/**
 * MediKiosk — Session Timeout & Ephemeral Purge Warning Modal
 * Alerts user before ephemeral kiosk session memory is cleared under DPDP Act.
 */

'use client';

import { AlertCircle, RefreshCw } from 'lucide-react';

interface SessionTimeoutModalProps {
  show: boolean;
  countdown: number;
  onExtend: () => void;
  onExit: () => void;
}

export default function SessionTimeoutModal({
  show,
  countdown,
  onExtend,
  onExit,
}: SessionTimeoutModalProps) {
  if (!show) return null;

  return (
    <div
      id="session-timeout-modal"
      data-element="session-timeout-modal"
      data-testid="session-timeout-modal"
      className="fixed inset-0 z-50 bg-black/70 backdrop-blur-xs flex items-center justify-center p-6"
    >
      <div className="bg-white rounded-3xl max-w-md w-full p-8 text-center flex flex-col items-center gap-6 shadow-2xl border border-[#bdc9c5]">
        <div className="w-16 h-16 rounded-full bg-[#ffdad6] text-[#ba1a1a] flex items-center justify-center">
          <AlertCircle className="w-9 h-9" />
        </div>

        <div>
          <h3 className="text-2xl font-bold text-[#191c1d]">
            Inactivity Notice
          </h3>
          <p className="text-sm text-[#3e4946] mt-2">
            Are you still there? For your medical privacy, this session will automatically clear in:
          </p>
          <div className="text-5xl font-black text-[#aa0a17] my-4">
            {countdown}s
          </div>
        </div>

        <div className="flex flex-col sm:flex-row gap-3 w-full">
          <button
            type="button"
            onClick={onExtend}
            className="flex-1 h-14 rounded-full bg-[#005f53] hover:bg-[#0c6b5e] text-white font-bold text-lg flex items-center justify-center gap-2 active:scale-95 transition-transform cursor-pointer shadow-md"
          >
            <RefreshCw className="w-5 h-5" />
            <span>Continue Check-in</span>
          </button>

          <button
            type="button"
            onClick={onExit}
            className="h-14 px-6 rounded-full border border-[#bdc9c5] hover:bg-[#eceeee] text-[#3e4946] font-semibold text-sm flex items-center justify-center active:scale-95 transition-transform cursor-pointer"
          >
            Exit Now
          </button>
        </div>
      </div>
    </div>
  );
}
