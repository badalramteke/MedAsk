'use client';

import React from 'react';
import { Mic, MicOff, AlertOctagon, Volume2, Sparkles } from 'lucide-react';
import { VoiceOrbState } from '../hooks/useVoiceSession';

interface VoiceOrbProps {
  state: VoiceOrbState;
  onToggleMic?: () => void;
  isMicActive?: boolean;
  size?: 'sm' | 'md' | 'lg';
}

export const VoiceOrb: React.FC<VoiceOrbProps> = ({
  state,
  onToggleMic,
  isMicActive = true,
  size = 'lg',
}) => {
  const sizeClasses = {
    sm: 'w-24 h-24',
    md: 'w-36 h-36',
    lg: 'w-48 h-48',
  }[size];

  const ringSizes = {
    sm: 'w-32 h-32',
    md: 'w-48 h-48',
    lg: 'w-64 h-64',
  }[size];

  // Dynamic state styles
  const getStateConfig = () => {
    switch (state) {
      case 'listening':
        return {
          gradient: 'from-emerald-400 via-teal-500 to-cyan-600 shadow-emerald-500/50',
          ringColor: 'border-emerald-400/30',
          pulse: 'animate-ping duration-1000',
          icon: <Mic className="w-12 h-12 text-white animate-pulse" />,
          label: 'Listening...',
          subLabel: 'Speak clearly in your language',
        };
      case 'processing':
        return {
          gradient: 'from-violet-500 via-purple-600 to-indigo-600 shadow-purple-500/50',
          ringColor: 'border-purple-400/40',
          pulse: 'animate-spin duration-3000',
          icon: <Sparkles className="w-12 h-12 text-white animate-spin" />,
          label: 'Processing speech...',
          subLabel: 'Structuring clinical history',
        };
      case 'speaking':
        return {
          gradient: 'from-cyan-400 via-blue-500 to-indigo-500 shadow-blue-500/50',
          ringColor: 'border-cyan-400/30',
          pulse: 'animate-pulse duration-700',
          icon: <Volume2 className="w-12 h-12 text-white animate-bounce" />,
          label: 'MediKiosk is speaking',
          subLabel: 'Listen to the audio question',
        };
      case 'red_flag':
        return {
          gradient: 'from-rose-600 via-red-600 to-amber-600 shadow-red-600/70',
          ringColor: 'border-red-500/50',
          pulse: 'animate-ping duration-700',
          icon: <AlertOctagon className="w-14 h-14 text-white animate-pulse" />,
          label: 'EMERGENCY RED-FLAG',
          subLabel: 'Critical triage condition detected',
        };
      case 'idle':
      default:
        return {
          gradient: 'from-slate-600 via-slate-700 to-slate-800 shadow-slate-900/40',
          ringColor: 'border-slate-500/20',
          pulse: '',
          icon: isMicActive ? (
            <Mic className="w-10 h-10 text-slate-300" />
          ) : (
            <MicOff className="w-10 h-10 text-slate-400" />
          ),
          label: 'Microphone Paused',
          subLabel: 'Tap the orb to speak or use touch',
        };
    }
  };

  const config = getStateConfig();

  return (
    <div className="flex flex-col items-center justify-center p-4">
      <div className="relative flex items-center justify-center">
        {/* Concentric Outer Ripple Rings */}
        {(state === 'listening' || state === 'red_flag' || state === 'speaking') && (
          <>
            <div
              className={`absolute rounded-full border-2 ${config.ringColor} ${ringSizes} animate-ping opacity-40`}
              style={{ animationDuration: state === 'red_flag' ? '0.8s' : '2s' }}
            />
            <div
              className={`absolute rounded-full border ${config.ringColor} ${ringSizes} scale-125 opacity-20`}
            />
          </>
        )}

        {/* Ambient Glow Aura */}
        <div
          className={`absolute rounded-full blur-2xl opacity-60 bg-gradient-to-r ${config.gradient} ${ringSizes}`}
        />

        {/* Central Interactive Orb Button */}
        <button
          onClick={onToggleMic}
          type="button"
          aria-label={config.label}
          className={`relative z-10 flex items-center justify-center rounded-full bg-gradient-to-tr ${config.gradient} ${sizeClasses} shadow-2xl transition-all duration-300 hover:scale-105 active:scale-95 cursor-pointer select-none focus:outline-none focus:ring-4 focus:ring-emerald-400/50`}
        >
          {config.icon}
        </button>
      </div>

      {/* Status Label & Assistive Subtext */}
      <div className="mt-4 text-center">
        <p
          className={`text-lg font-bold tracking-wide transition-colors duration-200 ${
            state === 'red_flag'
              ? 'text-rose-400 font-extrabold tracking-widest'
              : 'text-slate-100'
          }`}
        >
          {config.label}
        </p>
        <p className="text-sm text-slate-400 mt-0.5">{config.subLabel}</p>
      </div>
    </div>
  );
};

export default VoiceOrb;
