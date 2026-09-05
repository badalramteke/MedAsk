'use client';

import React from 'react';
import { AlertOctagon, PhoneCall, ShieldAlert, ArrowRight } from 'lucide-react';
import { RedFlagAlert as RedFlagAlertType } from '../api/moduleAClient';

interface RedFlagAlertProps {
  alert: RedFlagAlertType | null;
  onAcknowledge?: () => void;
}

export const RedFlagAlert: React.FC<RedFlagAlertProps> = ({ alert, onAcknowledge }) => {
  if (!alert) return null;

  return (
    <div
      role="alertdialog"
      aria-modal="true"
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/85 backdrop-blur-md animate-fade-in"
    >
      <div className="relative w-full max-w-2xl bg-gradient-to-b from-red-950 via-slate-900 to-black border-2 border-red-500 rounded-3xl p-8 shadow-2xl shadow-red-600/50 text-white text-center">
        {/* Top Emergency Pulse Beacon */}
        <div className="mx-auto mb-6 flex items-center justify-center w-24 h-24 rounded-full bg-red-600/30 border-2 border-red-500 animate-pulse">
          <AlertOctagon className="w-14 h-14 text-red-400 animate-bounce" />
        </div>

        {/* Header Alert Title */}
        <span className="inline-block px-4 py-1 mb-3 text-xs font-black uppercase tracking-widest bg-red-600 text-white rounded-full">
          CRITICAL CLINICAL ALERT (PRIORITY 1)
        </span>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-red-400 tracking-tight leading-tight mb-4">
          EMERGENCY TRIAGE BYPASS REQUIRED
        </h1>

        {/* Clinical Reason Details */}
        <div className="bg-red-950/60 border border-red-800/80 rounded-2xl p-5 mb-6 text-left">
          <p className="text-xs uppercase tracking-wider text-red-300 font-bold mb-1">
            Condition Detected
          </p>
          <p className="text-lg font-bold text-white mb-2">{alert.reason}</p>
          <p className="text-sm text-red-200">
            Reported Symptom: <span className="font-semibold text-white">{alert.matched_symptom}</span>
          </p>
          <p className="text-xs text-red-400 mt-2">
            Reference ID: {alert.alert_id} • Action: {alert.action_required}
          </p>
        </div>

        {/* Urgent Patient Instructions */}
        <div className="bg-slate-800/80 rounded-2xl p-4 mb-8 text-slate-200 text-sm sm:text-base leading-relaxed">
          <p className="font-semibold text-white mb-1">Please Do Not Wait in Queue:</p>
          <p>
            An attending nurse and doctor have been notified via the emergency triage dashboard.
            Please step immediately to <strong>Emergency Counter #1 / Trauma Triage</strong> for immediate clinical attention.
          </p>
        </div>

        {/* Action Button */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <button
            type="button"
            onClick={onAcknowledge}
            className="flex items-center justify-center gap-3 px-8 py-4 rounded-2xl font-extrabold text-lg bg-red-600 hover:bg-red-500 active:scale-95 text-white shadow-xl shadow-red-900/50 transition-all cursor-pointer"
          >
            <ShieldAlert className="w-6 h-6" />
            <span>Proceed to Emergency Desk</span>
            <ArrowRight className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default RedFlagAlert;
