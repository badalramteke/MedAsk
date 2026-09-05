'use client';

import React from 'react';
import { Check, Activity, HeartPulse, Stethoscope, Sparkles } from 'lucide-react';

interface ProgressTrackerProps {
  currentPhase: string;
  progressPercent: number;
  mode?: 'allopathic' | 'ayush' | 'both';
  socratesDimension?: string;
}

export const ProgressTracker: React.FC<ProgressTrackerProps> = ({
  currentPhase,
  progressPercent,
  mode = 'allopathic',
  socratesDimension,
}) => {
  const steps = [
    {
      id: 'chief_complaint',
      label: 'Chief Complaint',
      icon: <Activity className="w-4 h-4" />,
    },
    {
      id: 'socrates',
      label: socratesDimension ? `SOCRATES (${socratesDimension.toUpperCase()})` : 'SOCRATES 8-Step',
      icon: <Stethoscope className="w-4 h-4" />,
    },
    {
      id: 'ros',
      label: 'Review of Systems',
      icon: <HeartPulse className="w-4 h-4" />,
    },
    ...(mode in ['ayush', 'both'] || mode === 'ayush' || mode === 'both'
      ? [
          {
            id: 'ayush',
            label: 'AYUSH Pariksha',
            icon: <Sparkles className="w-4 h-4" />,
          },
        ]
      : []),
    {
      id: 'complete',
      label: 'Doctor Summary',
      icon: <Check className="w-4 h-4" />,
    },
  ];

  const getStepStatus = (stepId: string) => {
    const phaseOrder = ['chief_complaint', 'socrates', 'ros', 'ayush', 'complete'];
    const currIdx = phaseOrder.indexOf(currentPhase);
    const stepIdx = phaseOrder.indexOf(stepId);

    if (currentPhase === 'complete') return 'completed';
    if (currIdx > stepIdx) return 'completed';
    if (currIdx === stepIdx) return 'current';
    return 'upcoming';
  };

  return (
    <div className="w-full bg-slate-900/60 backdrop-blur-md border border-slate-800 rounded-2xl p-4 sm:p-5">
      {/* Top Bar with Percentage */}
      <div className="flex items-center justify-between mb-3 text-xs sm:text-sm font-semibold">
        <span className="text-slate-300">Clinical History Progress</span>
        <span className="text-teal-400 font-mono font-bold">{progressPercent}%</span>
      </div>

      {/* Progress Bar Line */}
      <div className="w-full h-2 bg-slate-800 rounded-full overflow-hidden mb-4">
        <div
          className="h-full bg-gradient-to-r from-teal-400 via-emerald-500 to-cyan-400 transition-all duration-500 rounded-full"
          style={{ width: `${Math.min(Math.max(progressPercent, 5), 100)}%` }}
        />
      </div>

      {/* Stepper Dots & Labels */}
      <div className="flex items-center justify-between gap-2 overflow-x-auto py-1">
        {steps.map((step, idx) => {
          const status = getStepStatus(step.id);

          return (
            <div
              key={step.id}
              className={`flex items-center gap-2 min-w-max transition-colors ${
                status === 'current'
                  ? 'text-teal-300 font-bold'
                  : status === 'completed'
                  ? 'text-emerald-400 font-medium'
                  : 'text-slate-500'
              }`}
            >
              <div
                className={`w-7 h-7 rounded-full flex items-center justify-center border text-xs transition-all ${
                  status === 'current'
                    ? 'bg-teal-500/20 border-teal-400 text-teal-300 shadow-md shadow-teal-500/20'
                    : status === 'completed'
                    ? 'bg-emerald-500 border-emerald-400 text-white'
                    : 'bg-slate-800 border-slate-700 text-slate-500'
                }`}
              >
                {status === 'completed' ? <Check className="w-3.5 h-3.5 stroke-[3]" /> : step.icon}
              </div>
              <span className="text-xs tracking-tight hidden md:inline">{step.label}</span>
              {idx < steps.length - 1 && (
                <div
                  className={`w-4 h-0.5 hidden sm:block ${
                    status === 'completed' ? 'bg-emerald-500/50' : 'bg-slate-800'
                  }`}
                />
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default ProgressTracker;
