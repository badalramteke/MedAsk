'use client';

import React, { useState, useEffect } from 'react';
import { QuestionItem, QuestionOption } from '../api/moduleAClient';
import { Check, CheckCircle2, ChevronRight, HelpCircle } from 'lucide-react';

interface QuestionCardProps {
  question: QuestionItem | null;
  onSelectOption: (option: QuestionOption) => void;
  onSubmitMultiOptions?: (options: QuestionOption[]) => void;
  spokenTranscript?: string;
  disabled?: boolean;
}

export const QuestionCard: React.FC<QuestionCardProps> = ({
  question,
  onSelectOption,
  onSubmitMultiOptions,
  spokenTranscript = '',
  disabled = false,
}) => {
  const [selectedSingle, setSelectedSingle] = useState<string | null>(null);
  const [selectedMulti, setSelectedMulti] = useState<string[]>([]);

  // Voice-Touch Synchronization: highlight matching option if spoken by patient
  useEffect(() => {
    if (!question || !spokenTranscript) return;
    const lower = spokenTranscript.toLowerCase();

    for (const opt of question.options) {
      if (lower.includes(opt.text.toLowerCase()) || lower.includes(opt.value.toLowerCase())) {
        if (question.input_type === 'multi_mcq') {
          if (!selectedMulti.includes(opt.id)) {
            setSelectedMulti((prev) => [...prev, opt.id]);
          }
        } else {
          setSelectedSingle(opt.id);
        }
        break;
      }
    }
  }, [spokenTranscript, question, selectedMulti]);

  if (!question) {
    return (
      <div className="bg-slate-800/60 backdrop-blur-xl border border-slate-700/60 rounded-3xl p-8 text-center text-slate-400">
        <p>Awaiting next clinical question...</p>
      </div>
    );
  }

  const isMulti = question.input_type === 'multi_mcq';

  const handleOptionClick = (option: QuestionOption) => {
    if (disabled) return;

    if (isMulti) {
      const exists = selectedMulti.includes(option.id);
      const updated = exists
        ? selectedMulti.filter((id) => id !== option.id)
        : [...selectedMulti, option.id];
      setSelectedMulti(updated);
    } else {
      setSelectedSingle(option.id);
      onSelectOption(option);
    }
  };

  const handleConfirmMulti = () => {
    if (!onSubmitMultiOptions) return;
    const selectedObjs = question.options.filter((o) => selectedMulti.includes(o.id));
    onSubmitMultiOptions(selectedObjs);
  };

  return (
    <div className="bg-slate-900/80 backdrop-blur-2xl border border-slate-700/60 rounded-3xl p-6 sm:p-8 shadow-2xl transition-all duration-300">
      {/* Header Badges */}
      <div className="flex items-center justify-between gap-4 mb-4">
        <div className="flex items-center gap-2">
          {question.socrates_dimension && (
            <span className="px-3 py-1 text-xs font-bold tracking-wider uppercase rounded-full bg-teal-500/20 text-teal-300 border border-teal-500/30">
              SOCRATES: {question.socrates_dimension}
            </span>
          )}
          <span className="px-3 py-1 text-xs font-semibold rounded-full bg-slate-800 text-slate-300 border border-slate-700">
            {question.phase.toUpperCase()}
          </span>
        </div>
        <div className="flex items-center gap-1.5 text-xs text-slate-400">
          <HelpCircle className="w-4 h-4 text-slate-500" />
          <span>Touch or Voice</span>
        </div>
      </div>

      {/* Main Clinical Question Text */}
      <h2 className="text-xl sm:text-2xl font-bold text-white tracking-tight leading-snug mb-6">
        {question.text}
      </h2>

      {/* Touch Options Grid */}
      {question.options && question.options.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
          {question.options.map((option) => {
            const isSelected = isMulti
              ? selectedMulti.includes(option.id)
              : selectedSingle === option.id;

            return (
              <button
                key={option.id}
                type="button"
                disabled={disabled}
                onClick={() => handleOptionClick(option)}
                className={`flex items-center justify-between p-4 sm:p-5 rounded-2xl border text-left transition-all duration-200 min-h-[64px] cursor-pointer select-none group focus:outline-none ${
                  isSelected
                    ? 'bg-gradient-to-r from-emerald-600/30 to-teal-600/30 border-emerald-400 text-white shadow-lg shadow-emerald-900/20 scale-[1.01]'
                    : 'bg-slate-800/70 hover:bg-slate-800 border-slate-700 hover:border-slate-500 text-slate-200 active:scale-[0.99]'
                }`}
              >
                <div className="flex items-center gap-3.5 pr-2">
                  <div
                    className={`w-6 h-6 rounded-lg flex items-center justify-center border transition-colors ${
                      isSelected
                        ? 'bg-emerald-500 border-emerald-400 text-white'
                        : 'border-slate-600 group-hover:border-slate-400'
                    }`}
                  >
                    {isSelected && <Check className="w-4 h-4 stroke-[3]" />}
                  </div>
                  <span className="text-base sm:text-lg font-medium leading-tight">
                    {option.text}
                  </span>
                </div>
                <ChevronRight
                  className={`w-5 h-5 transition-transform ${
                    isSelected
                      ? 'text-emerald-400 translate-x-1'
                      : 'text-slate-500 group-hover:translate-x-0.5'
                  }`}
                />
              </button>
            );
          })}
        </div>
      )}

      {/* Confirm Button for Multi-Select */}
      {isMulti && (
        <div className="mt-6 flex justify-end">
          <button
            type="button"
            disabled={disabled || selectedMulti.length === 0}
            onClick={handleConfirmMulti}
            className="flex items-center gap-2 px-6 py-3.5 rounded-2xl font-bold bg-gradient-to-r from-emerald-500 to-teal-600 text-white shadow-lg hover:from-emerald-600 hover:to-teal-700 disabled:opacity-40 disabled:cursor-not-allowed transition-all cursor-pointer"
          >
            <CheckCircle2 className="w-5 h-5" />
            <span>Confirm Selections ({selectedMulti.length})</span>
          </button>
        </div>
      )}
    </div>
  );
};

export default QuestionCard;
