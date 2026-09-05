'use client';

import React, { useEffect, useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import VoiceOrb from './VoiceOrb';
import QuestionCard from './QuestionCard';
import RedFlagAlert from './RedFlagAlert';
import ProgressTracker from './ProgressTracker';
import { useDialogue } from '../hooks/useDialogue';
import { useVoiceSession } from '../hooks/useVoiceSession';
import { QuestionOption } from '../api/moduleAClient';
import {
  Volume2,
  Mic,
  MicOff,
  Globe,
  Sparkles,
  ArrowRight,
  ShieldCheck,
  RotateCcw,
  FileText,
} from 'lucide-react';

interface ModuleAEntryProps {
  initialLanguage?: string;
  initialMode?: 'allopathic' | 'ayush' | 'both';
  patientId?: string;
  onFinished?: (summary: any) => void;
}

export const ModuleAEntry: React.FC<ModuleAEntryProps> = ({
  initialLanguage = 'en',
  initialMode = 'allopathic',
  patientId,
  onFinished,
}) => {
  const router = useRouter();

  const {
    sessionId,
    currentQuestion,
    setCurrentQuestion,
    phase,
    progressPercent,
    setProgressPercent,
    mode,
    changeMode,
    language,
    activeAlert,
    setActiveAlert,
    summary,
    isLoading,
    errorMessage,
    initSession,
    submitAnswer,
    finishSession,
  } = useDialogue();

  const handleQuestionAdvanced = useCallback(
    (nextQ: any, nextPhase: string, progress: number) => {
      setCurrentQuestion(nextQ);
      setProgressPercent(progress);
    },
    [setCurrentQuestion, setProgressPercent]
  );

  const handleRedFlagDetected = useCallback(
    (alert: any) => {
      setActiveAlert(alert);
    },
    [setActiveAlert]
  );

  const {
    orbState,
    setOrbState,
    isMicActive,
    interimTranscript,
    silenceAlert,
    startListening,
    stopListening,
    sendTouchOption,
  } = useVoiceSession({
    sessionId,
    language,
    onQuestionAdvanced: handleQuestionAdvanced,
    onRedFlagDetected: handleRedFlagDetected,
  });

  // Auto-start session on mount
  useEffect(() => {
    initSession({
      patientId,
      language: initialLanguage,
      mode: initialMode,
    }).then((res) => {
      // Auto-initiate microphone for voice-first kiosk experience
      startListening();
    }).catch((err) => {
      console.error('Failed to init Module A session:', err);
    });

    return () => {
      stopListening();
    };
  }, []);

  // Option touch selection handler
  const handleSelectOption = async (option: QuestionOption) => {
    sendTouchOption(option.id, option.text);
    await submitAnswer({
      optionId: option.id,
      answerText: option.text,
    });
  };

  // Multi-option selection handler
  const handleSelectMulti = async (options: QuestionOption[]) => {
    const ids = options.map((o) => o.id);
    const text = options.map((o) => o.text).join(', ');
    sendTouchOption(ids[0], text);
    await submitAnswer({
      optionIds: ids,
      answerText: text,
    });
  };

  const handleToggleMic = () => {
    if (isMicActive) {
      stopListening();
    } else {
      startListening();
    }
  };

  const handleFinish = async () => {
    const sum = await finishSession();
    if (onFinished && sum) {
      onFinished(sum);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col justify-between p-4 sm:p-6 lg:p-8 select-none">
      {/* Red-Flag Emergency Overlay */}
      <RedFlagAlert
        alert={activeAlert}
        onAcknowledge={() => {
          router.push('/triage/alert');
        }}
      />

      {/* Top Navigation & Clinical Mode Bar */}
      <header className="max-w-6xl w-full mx-auto flex flex-col sm:flex-row items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-teal-500 to-emerald-400 flex items-center justify-center text-slate-950 font-black shadow-lg shadow-teal-500/30">
            M
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
              MediKiosk <span className="text-teal-400 text-xs font-mono px-2 py-0.5 rounded-md bg-teal-950 border border-teal-800">MODULE A</span>
            </h1>
            <p className="text-xs text-slate-400">Conversational Multimodal History Engine</p>
          </div>
        </div>

        {/* Mode Selector Chips */}
        <div className="flex items-center gap-1.5 p-1 bg-slate-900 border border-slate-800 rounded-2xl">
          <button
            type="button"
            onClick={() => changeMode('allopathic')}
            className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all cursor-pointer ${
              mode === 'allopathic'
                ? 'bg-teal-500 text-slate-950 shadow-md shadow-teal-500/30'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Allopathic
          </button>
          <button
            type="button"
            onClick={() => changeMode('ayush')}
            className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all cursor-pointer ${
              mode === 'ayush'
                ? 'bg-amber-500 text-slate-950 shadow-md shadow-amber-500/30'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            AYUSH
          </button>
          <button
            type="button"
            onClick={() => changeMode('both')}
            className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all cursor-pointer ${
              mode === 'both'
                ? 'bg-gradient-to-r from-teal-500 to-amber-500 text-slate-950 shadow-md'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Integrated (Both)
          </button>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="max-w-6xl w-full mx-auto my-6 flex-1 flex flex-col justify-center">
        {/* Step Progress Tracker */}
        <div className="mb-6">
          <ProgressTracker
            currentPhase={phase}
            progressPercent={progressPercent}
            mode={mode}
            socratesDimension={currentQuestion?.socrates_dimension}
          />
        </div>

        {/* Silence Warning Alert Banner */}
        {silenceAlert && (
          <div className="mb-4 p-4 rounded-2xl bg-amber-950/70 border border-amber-500/50 text-amber-200 flex items-center justify-between animate-fade-in">
            <div className="flex items-center gap-3">
              <Sparkles className="w-5 h-5 text-amber-400 animate-pulse" />
              <p className="text-sm font-medium">{silenceAlert}</p>
            </div>
            <button
              onClick={() => setOrbState('listening')}
              className="px-3 py-1 text-xs font-bold rounded-lg bg-amber-500 text-slate-950 cursor-pointer"
            >
              I am ready
            </button>
          </div>
        )}

        {/* Completion View: HPI Summary Ready */}
        {phase === 'complete' && summary ? (
          <div className="bg-slate-900/90 border border-emerald-500/40 rounded-3xl p-8 shadow-2xl animate-fade-in text-left">
            <div className="flex items-center justify-between pb-4 mb-6 border-b border-slate-800">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-2xl bg-emerald-500/20 text-emerald-400 flex items-center justify-center border border-emerald-500/30">
                  <ShieldCheck className="w-6 h-6" />
                </div>
                <div>
                  <h2 className="text-2xl font-black text-white">Clinical Intake Complete</h2>
                  <p className="text-xs text-slate-400">
                    Schema v{summary.schema_version} • Session: {summary.session_id}
                  </p>
                </div>
              </div>
              <span className="px-3 py-1 text-xs font-bold rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">
                DOCTOR READY
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
              {/* Chief Complaint & SOCRATES Breakdown */}
              <div className="bg-slate-800/60 p-5 rounded-2xl border border-slate-700/60">
                <h3 className="text-sm font-bold text-teal-300 uppercase tracking-wider mb-3">
                  SOCRATES 8-Dimension Profile
                </h3>
                <div className="space-y-2 text-sm">
                  <p><strong className="text-slate-400">Chief Complaint:</strong> {summary.chief_complaint}</p>
                  <p><strong className="text-slate-400">Site:</strong> {summary.socrates.site || 'N/A'}</p>
                  <p><strong className="text-slate-400">Onset:</strong> {summary.socrates.onset || 'N/A'}</p>
                  <p><strong className="text-slate-400">Character:</strong> {summary.socrates.character || 'N/A'}</p>
                  <p><strong className="text-slate-400">Radiation:</strong> {summary.socrates.radiation || 'N/A'}</p>
                  <p><strong className="text-slate-400">Associations:</strong> {summary.socrates.associations?.join(', ') || 'None'}</p>
                  <p><strong className="text-slate-400">Time Course:</strong> {summary.socrates.time_course || 'N/A'}</p>
                  <p><strong className="text-slate-400">Exacerbating:</strong> {summary.socrates.exacerbating_relieving || 'N/A'}</p>
                  <p><strong className="text-slate-400">Severity:</strong> {summary.socrates.severity || 'N/A'}</p>
                </div>
              </div>

              {/* Review of Systems & AYUSH */}
              <div className="bg-slate-800/60 p-5 rounded-2xl border border-slate-700/60">
                <h3 className="text-sm font-bold text-amber-300 uppercase tracking-wider mb-3">
                  ROS & Holistic Findings
                </h3>
                <div className="space-y-2 text-sm">
                  <p><strong className="text-slate-400">Cardiovascular:</strong> {summary.review_of_systems.cardiovascular?.join(', ') || 'Normal'}</p>
                  <p><strong className="text-slate-400">Respiratory:</strong> {summary.review_of_systems.respiratory?.join(', ') || 'Normal'}</p>
                  <p><strong className="text-slate-400">Gastrointestinal:</strong> {summary.review_of_systems.gastrointestinal?.join(', ') || 'Normal'}</p>
                  {summary.ayush_pariksha && (
                    <div className="mt-3 pt-3 border-t border-slate-700">
                      <p><strong className="text-amber-300">Prakriti / Dosha:</strong> {summary.ayush_pariksha.dosha_predominance}</p>
                      <p><strong className="text-amber-300">Ahara Shakti:</strong> {summary.ayush_pariksha.dashavidha?.['Ahara-shakti']}</p>
                    </div>
                  )}
                </div>
              </div>
            </div>

            <div className="flex justify-end gap-4">
              <button
                type="button"
                onClick={() => router.push('/summary')}
                className="flex items-center gap-2 px-8 py-4 rounded-2xl font-bold bg-gradient-to-r from-teal-500 to-emerald-500 text-slate-950 shadow-xl shadow-teal-500/20 hover:scale-105 transition-all cursor-pointer"
              >
                <span>Proceed to Doctor Summary & FHIR Bundle</span>
                <ArrowRight className="w-5 h-5" />
              </button>
            </div>
          </div>
        ) : (
          /* Dual-Column Voice Orb & Question Card Layout */
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
            {/* Left Column: Voice Orb */}
            <div className="lg:col-span-4 flex flex-col items-center justify-center">
              <VoiceOrb
                state={orbState}
                onToggleMic={handleToggleMic}
                isMicActive={isMicActive}
                size="lg"
              />

              {/* Live Speech Recognition Feedback */}
              {interimTranscript && (
                <div className="mt-4 px-4 py-2 bg-slate-900/90 border border-teal-500/30 rounded-xl text-xs text-teal-300 max-w-xs text-center animate-pulse">
                  "{interimTranscript}"
                </div>
              )}
            </div>

            {/* Right Column: Question Card */}
            <div className="lg:col-span-8">
              <QuestionCard
                question={currentQuestion}
                onSelectOption={handleSelectOption}
                onSubmitMultiOptions={handleSelectMulti}
                spokenTranscript={interimTranscript}
                disabled={isLoading}
              />
            </div>
          </div>
        )}
      </main>

      {/* Bottom Voice Navigation Command Guide */}
      <footer className="max-w-6xl w-full mx-auto pt-4 border-t border-slate-800/80 flex flex-wrap items-center justify-between gap-3 text-xs text-slate-400">
        <div className="flex items-center gap-2">
          <Volume2 className="w-4 h-4 text-teal-400" />
          <span className="font-semibold text-slate-300">Voice Navigation Commands:</span>
          <span className="text-slate-400">"Next" • "Back" • "Repeat" • "Help" • "Stop" • "Options"</span>
        </div>
        <div className="flex items-center gap-2 text-slate-500">
          <span>ABDM & DPDP Compliant</span>
          <span>•</span>
          <span>MediKiosk v1.0</span>
        </div>
      </footer>
    </div>
  );
};

export default ModuleAEntry;
