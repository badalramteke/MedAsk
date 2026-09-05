/**
 * MediKiosk — Ayurvedic Dashavidha Pariksha & Ahara-Vihara Engine (/intake/ayush)
 * Screen 07: Comprehensive Ayurvedic constitutional and lifestyle assessment.
 * Sequences through all 10 Dashavidha Pariksha parameters (Prakriti, Vikriti, Sara,
 * Samhanana, Pramana, Satmya, Sattva, Ahara Shakti, Vyayama Shakti, Vaya)
 * plus Agni, Koshtha, and Ahara-Vihara assessment with dual-mode touch & voice.
 */

'use client';

import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import KioskHeader from '@/components/layout/KioskHeader';
import KioskFooter from '@/components/layout/KioskFooter';
import StepProgressBar from '@/components/layout/StepProgressBar';
import VoiceOrb from '@/components/voice/VoiceOrb';
import { useSessionStore } from '@/stores/useSessionStore';
import { useFlowStore } from '@/stores/useFlowStore';
import { useIntakeStore } from '@/stores/useIntakeStore';
import { useTTS } from '@/hooks/useTTS';
import { intakeService } from '@/services/intakeService';
import type { QuestionResponse, QuestionOption } from '@/lib/types';
import {
  Flower2,
  Volume2,
  Check,
  CheckCircle2,
  Sparkles,
  Flame,
  Wind,
  Droplets,
  HeartPulse,
  SunMedium,
  Brain,
  Scale,
} from 'lucide-react';

export default function AyushIntakePage() {
  const router = useRouter();
  const { language, sessionId, ensureBackendSession } = useSessionStore();
  const { setCurrentScreen } = useFlowStore();
  const { ayushAnswers, setAyushAnswer } = useIntakeStore();
  const { speak, isSpeaking, stop } = useTTS();

  const [activeQuestion, setActiveQuestion] = useState<QuestionResponse | null>(null);
  const [selectedOptionCode, setSelectedOptionCode] = useState<string | null>(null);
  const [selectedMultiCodes, setSelectedMultiCodes] = useState<string[]>([]);
  const [freeTextAnswer, setFreeTextAnswer] = useState<string>('');
  const [voiceFeedback, setVoiceFeedback] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  // Load the next AYUSH question from the backend LangGraph engine
  const fetchNextAyushQuestion = useCallback(async () => {
    setLoading(true);
    try {
      const sid = sessionId || (await ensureBackendSession(language));
      // Switch intake mode to AYUSH
      await intakeService.setIntakeMode(sid, 'AYUSH').catch(() => {});
      const question = await intakeService.getNextQuestion(sid, 'AYUSH');

      if (question && question.question_id) {
        setActiveQuestion(question);
        setSelectedOptionCode(null);
        setSelectedMultiCodes([]);
        setFreeTextAnswer('');
        setVoiceFeedback(null);
      } else {
        finishAyushAssessment();
      }
    } catch (err) {
      console.warn('Backend AYUSH query notice, checking local state:', err);
      finishAyushAssessment();
    } finally {
      setLoading(false);
    }
  }, [sessionId, ensureBackendSession, language]);

  // Initial load
  useEffect(() => {
    fetchNextAyushQuestion();
  }, [fetchNextAyushQuestion]);

  // Proactively speak question prompt when question loads
  useEffect(() => {
    if (activeQuestion?.question_text) {
      speak(activeQuestion.question_text, language);
    }
    return () => {
      stop();
    };
  }, [activeQuestion?.question_id, language, speak, stop]);

  const toggleMultiCode = (code: string) => {
    setSelectedMultiCodes((prev) =>
      prev.includes(code) ? prev.filter((c) => c !== code) : [...prev, code]
    );
  };

  /**
   * Spoken voice answer handler for AYUSH questions
   */
  const handleVoiceTranscript = async (transcript: string) => {
    if (!transcript || !activeQuestion) return;
    const lower = transcript.toLowerCase().trim();

    // Check if spoken text matches an option text or code
    let matchedOpt: QuestionOption | null = null;
    if (activeQuestion.options && activeQuestion.options.length > 0) {
      for (const opt of activeQuestion.options) {
        const optText = opt.text.toLowerCase();
        const valCode = opt.value_code.toLowerCase().replace(/_/g, ' ');
        if (
          lower.includes(optText) ||
          optText.includes(lower) ||
          lower.includes(valCode)
        ) {
          matchedOpt = opt;
          break;
        }
      }
    }

    if (matchedOpt) {
      setVoiceFeedback(`Recognized: "${matchedOpt.text}"`);
      if (activeQuestion.input_type === 'multi_select') {
        toggleMultiCode(matchedOpt.value_code);
      } else {
        setSelectedOptionCode(matchedOpt.value_code);
        await submitAyushAnswer([matchedOpt.value_code]);
      }
    } else {
      setFreeTextAnswer(transcript);
      setVoiceFeedback(`Captured: "${transcript}"`);
      await submitAyushAnswer([], transcript);
    }
  };

  const submitAyushAnswer = async (
    valueCodes?: string[] | null,
    customText?: string | null,
    answerState: 'ANSWERED' | 'UNKNOWN' | 'REFUSED' = 'ANSWERED'
  ) => {
    if (!activeQuestion) return;
    setLoading(true);

    try {
      const sid = sessionId || (await ensureBackendSession(language));
      const codes =
        valueCodes !== undefined
          ? valueCodes
          : activeQuestion.input_type === 'multi_select'
          ? selectedMultiCodes
          : selectedOptionCode
          ? [selectedOptionCode]
          : [];

      const text = customText !== undefined ? customText : freeTextAnswer;

      // Save locally to intake store
      const answerVal = codes && codes.length > 0 ? (codes.length === 1 ? codes[0] : codes) : text || '';
      setAyushAnswer(activeQuestion.question_id, answerVal);

      const result = await intakeService.submitAnswer(
        sid,
        {
          question_id: activeQuestion.question_id,
          selected_value_codes: codes || [],
          free_text: text || null,
          answer_state: answerState,
        },
        'AYUSH'
      );

      if (result.next_question && !result.interview_complete) {
        setActiveQuestion(result.next_question);
        setSelectedOptionCode(null);
        setSelectedMultiCodes([]);
        setFreeTextAnswer('');
        setVoiceFeedback(null);
      } else {
        finishAyushAssessment();
      }
    } catch (err) {
      console.warn('AYUSH answer progression note:', err);
      finishAyushAssessment();
    } finally {
      setLoading(false);
    }
  };

  const finishAyushAssessment = () => {
    stop();
    setCurrentScreen('document_scanner');
    router.push('/documents/scan');
  };

  const handleBack = () => {
    stop();
    setCurrentScreen('chief_complaint');
    router.push('/intake/symptoms');
  };

  // Helper icon for Ayurvedic concepts
  const getAyushIcon = (questionId?: string) => {
    if (!questionId) return <Flower2 className="w-5 h-5 text-[#005f53]" />;
    const q = questionId.toUpperCase();
    if (q.includes('PRAKRITI') || q.includes('VIKRITI')) return <Wind className="w-5 h-5 text-[#005f53]" />;
    if (q.includes('AGNI')) return <Flame className="w-5 h-5 text-[#005f53]" />;
    if (q.includes('SARA') || q.includes('SAMHANANA')) return <HeartPulse className="w-5 h-5 text-[#005f53]" />;
    if (q.includes('SATTVA')) return <Brain className="w-5 h-5 text-[#005f53]" />;
    if (q.includes('PRAMANA') || q.includes('SATMYA')) return <Scale className="w-5 h-5 text-[#005f53]" />;
    if (q.includes('VAYA')) return <SunMedium className="w-5 h-5 text-[#005f53]" />;
    return <Flower2 className="w-5 h-5 text-[#005f53]" />;
  };

  return (
    <div className="h-screen w-screen flex flex-col bg-[#f8fafa] overflow-hidden">
      <KioskHeader onBack={handleBack} />
      <StepProgressBar />

      <main className="flex-1 max-w-5xl w-full mx-auto p-4 md:p-8 flex flex-col justify-between overflow-y-auto">
        {/* Header Badge & Title */}
        <div className="text-center mb-2">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#005f53]/10 text-[#005f53] font-bold text-xs uppercase tracking-wider mb-2">
            {getAyushIcon(activeQuestion?.question_id)}
            <span>
              {activeQuestion?.phase === 'AYUSH_AHARA_VIHARA'
                ? 'Ahara-Vihara Lifestyle Assessment'
                : activeQuestion?.phase === 'AYUSH_SUPPORTING'
                ? 'Supporting Ayurvedic Parameters'
                : 'AIIA Ayurvedic Dashavidha Pariksha'}
            </span>
          </div>

          <div className="flex items-center justify-center gap-3">
            <h1 className="text-2xl md:text-3xl font-black text-[#191c1d] tracking-tight">
              {activeQuestion?.question_text || 'Ayurvedic Constitutional Assessment'}
            </h1>

            {activeQuestion?.question_text && (
              <button
                type="button"
                onClick={() => speak(activeQuestion.question_text, language)}
                aria-label="Replay audio question"
                className="p-2 rounded-full bg-[#eceeee] hover:bg-[#e1e3e3] text-[#005f53] transition-all cursor-pointer"
                title="Listen to question"
              >
                <Volume2 className={`w-5 h-5 ${isSpeaking ? 'animate-bounce text-[#0f7a6b]' : ''}`} />
              </button>
            )}
          </div>

          <p className="text-xs md:text-sm text-[#3e4946] mt-1">
            Tap an option on screen OR speak naturally into the microphone below.
          </p>

          {/* Voice Recognition Badge */}
          {voiceFeedback && (
            <div className="inline-flex items-center gap-2 mt-2 px-4 py-1.5 rounded-full bg-[#005f53]/10 text-[#005f53] text-xs font-bold animate-fade-in-up">
              <Sparkles className="w-3.5 h-3.5" />
              <span>{voiceFeedback}</span>
            </div>
          )}
        </div>

        {/* Question Options or Free Text */}
        {activeQuestion && (
          <div className="flex-1 flex flex-col items-center justify-center my-auto w-full max-w-3xl mx-auto">
            {activeQuestion.options && activeQuestion.options.length > 0 ? (
              <div className="w-full mb-6">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5 w-full">
                  {activeQuestion.options.map((opt) => {
                    const isMulti = activeQuestion.input_type === 'multi_select';
                    const isSelected = isMulti
                      ? selectedMultiCodes.includes(opt.value_code)
                      : selectedOptionCode === opt.value_code;

                    return (
                      <button
                        key={opt.option_id || opt.value_code}
                        type="button"
                        onClick={() => {
                          if (isMulti) {
                            toggleMultiCode(opt.value_code);
                          } else {
                            setSelectedOptionCode(opt.value_code);
                            submitAyushAnswer([opt.value_code]);
                          }
                        }}
                        className={`min-h-[85px] p-5 rounded-2xl text-left flex items-center justify-between transition-all cursor-pointer border ${
                          isSelected
                            ? 'bg-[#005f53] text-white border-transparent shadow-lg scale-102 ring-2 ring-[#005f53]/30'
                            : 'bg-white hover:bg-[#eceeee] text-[#191c1d] border-[#bdc9c5]/60 hover:border-[#005f53]'
                        }`}
                      >
                        <div className="flex items-center gap-3">
                          <div
                            className={`w-6 h-6 rounded-lg border flex items-center justify-center transition-all ${
                              isSelected
                                ? 'bg-white text-[#005f53] border-white font-bold'
                                : 'border-[#bdc9c5] bg-[#f8fafa]'
                            }`}
                          >
                            {isSelected && <Check className="w-4 h-4 stroke-[3]" />}
                          </div>
                          <span className="font-bold text-base md:text-lg">
                            {opt.text}
                          </span>
                        </div>
                      </button>
                    );
                  })}
                </div>

                {/* Confirm Multi-Select Button */}
                {activeQuestion.input_type === 'multi_select' && (
                  <div className="flex justify-center mt-4">
                    <button
                      type="button"
                      onClick={() => submitAyushAnswer(selectedMultiCodes)}
                      className="px-8 py-3 rounded-full bg-[#005f53] hover:bg-[#0f7a6b] text-white font-bold text-base shadow-md cursor-pointer transition-all active:scale-95"
                    >
                      Confirm Selected ({selectedMultiCodes.length})
                    </button>
                  </div>
                )}
              </div>
            ) : (
              <div className="w-full mb-6">
                <input
                  type="text"
                  placeholder="Type or speak your answer..."
                  value={freeTextAnswer}
                  onChange={(e) => setFreeTextAnswer(e.target.value)}
                  className="w-full h-16 px-6 rounded-2xl border-2 border-[#005f53] text-lg bg-white focus:outline-none shadow-sm"
                />
              </div>
            )}

            {/* Quick Skip / Unsure Buttons */}
            <div className="flex items-center gap-3 mb-4">
              <button
                type="button"
                onClick={() => submitAyushAnswer([], null, 'UNKNOWN')}
                className="px-4 py-2 rounded-full bg-[#eceeee] hover:bg-[#e1e3e3] text-[#3e4946] text-xs font-bold transition-all cursor-pointer"
              >
                Not sure / Don&apos;t know
              </button>
              <button
                type="button"
                onClick={() => submitAyushAnswer([], null, 'REFUSED')}
                className="px-4 py-2 rounded-full bg-[#eceeee] hover:bg-[#e1e3e3] text-[#3e4946] text-xs font-bold transition-all cursor-pointer"
              >
                Prefer not to say
              </button>
            </div>

            {/* Voice Orb for AYUSH Question */}
            <VoiceOrb
              promptText={activeQuestion.question_text}
              onTranscriptReady={handleVoiceTranscript}
              inline
            />
          </div>
        )}
      </main>

      <KioskFooter
        onNext={() => submitAyushAnswer()}
        onBack={handleBack}
        nextText={loading ? 'Processing...' : 'Next Parameter'}
      />
    </div>
  );
}
