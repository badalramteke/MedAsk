/**
 * MediKiosk — Conversational Multimodal History Engine (/intake/symptoms)
 * Screen 06: Dual-mode voice & touch clinical interview with adaptive SOCRATES
 * questioning, auto-TTS audio prompts, spoken option recognition,
 * 2D anatomical body map, pain scale, and real-time emergency red-flag interception.
 */

'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import KioskHeader from '@/components/layout/KioskHeader';
import KioskFooter from '@/components/layout/KioskFooter';
import StepProgressBar from '@/components/layout/StepProgressBar';
import VoiceOrb from '@/components/voice/VoiceOrb';
import BodyMapSelector from '@/components/interactive/BodyMapSelector';
import PainSeveritySlider from '@/components/interactive/PainSeveritySlider';
import { useSessionStore } from '@/stores/useSessionStore';
import { useFlowStore } from '@/stores/useFlowStore';
import { useIntakeStore } from '@/stores/useIntakeStore';
import { useTTS } from '@/hooks/useTTS';
import { intakeService } from '@/services/intakeService';
import type { QuestionResponse, QuestionOption } from '@/lib/types';
import { t } from '@/lib/i18n';
import {
  Activity,
  CheckCircle2,
  Volume2,
  HelpCircle,
  ShieldAlert,
  Sparkles,
  Check,
} from 'lucide-react';

const COMMON_CHIEF_COMPLAINTS = [
  { id: 'chest_pain', text: 'Chest Pain', redFlag: true },
  { id: 'fever', text: 'High Fever & Chills', redFlag: false },
  { id: 'cough', text: 'Severe Cough & Phlegm', redFlag: false },
  { id: 'headache', text: 'Throbbing Headache', redFlag: false },
  { id: 'abdominal_pain', text: 'Stomach / Abdominal Pain', redFlag: false },
  { id: 'shortness_of_breath', text: 'Shortness of Breath', redFlag: true },
  { id: 'joint_pain', text: 'Joint / Knee Pain', redFlag: false },
  { id: 'vomiting', text: 'Vomiting & Diarrhea', redFlag: false },
];

export default function SymptomsPage() {
  const router = useRouter();
  const { language, sessionId, intakeMode, triggerEmergency, ensureBackendSession } = useSessionStore();
  const { setCurrentScreen } = useFlowStore();
  const {
    chiefComplaint,
    setChiefComplaint,
    bodyRegion,
    setBodyRegion,
    painSeverity,
    setPainSeverity,
  } = useIntakeStore();

  const { speak, isSpeaking, stop } = useTTS();

  const [activeTab, setActiveTab] = useState<'COMPLAINT' | 'BODY_MAP' | 'PAIN_SCALE' | 'ADAPTIVE_QUESTION'>('COMPLAINT');
  const [activeQuestion, setActiveQuestion] = useState<QuestionResponse | null>(null);
  const [selectedOptionCode, setSelectedOptionCode] = useState<string | null>(null);
  const [selectedMultiCodes, setSelectedMultiCodes] = useState<string[]>([]);
  const [freeTextAnswer, setFreeTextAnswer] = useState<string>('');
  const [voiceFeedback, setVoiceFeedback] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  // Auto-speak questions when adaptive inquiry changes
  useEffect(() => {
    if (activeTab === 'ADAPTIVE_QUESTION' && activeQuestion?.question_text) {
      speak(activeQuestion.question_text, language);
    }
  }, [activeQuestion?.question_id, activeTab, language, speak]);

  const handleSelectComplaint = (complaint: (typeof COMMON_CHIEF_COMPLAINTS)[0]) => {
    setChiefComplaint(complaint.text);

    // Immediate Red-Flag rule evaluation
    if (complaint.redFlag && (complaint.id === 'chest_pain' || complaint.id === 'shortness_of_breath')) {
      triggerEmergency(`Critical symptom selected: "${complaint.text}" — Urgent clinical evaluation required.`);
      router.push('/triage/alert');
      return;
    }

    setActiveTab('BODY_MAP');
  };

  /**
   * Spoken voice answer handler:
   * 1. Checks emergency keywords in transcript.
   * 2. If in ADAPTIVE_QUESTION mode: fuzzy matches spoken phrase to active options.
   * 3. Falls back to free-text submission.
   */
  const handleVoiceTranscript = async (transcript: string) => {
    if (!transcript) return;
    const lower = transcript.toLowerCase().trim();

    // Check emergency spoken phrases across languages
    if (
      lower.includes('chest pain') ||
      lower.includes('heart attack') ||
      lower.includes('breath') ||
      lower.includes('difficulty breathing') ||
      lower.includes('stroke') ||
      lower.includes('paralysis') ||
      lower.includes('छाती में दर्द') ||
      lower.includes('सांस लेने में तकलीफ') ||
      lower.includes('दौरा')
    ) {
      triggerEmergency(`Spoken red-flag: "${transcript}" — Urgent triage required`);
      router.push('/triage/alert');
      return;
    }

    if (activeTab === 'COMPLAINT') {
      setChiefComplaint(transcript);
      setVoiceFeedback(`Recorded: "${transcript}"`);
      return;
    }

    if (activeTab === 'ADAPTIVE_QUESTION' && activeQuestion) {
      // 1. Check if patient answered with an option name
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
          await submitActiveAnswer([matchedOpt.value_code], null);
        }
      } else {
        // Submit spoken narrative as free-text answer
        setFreeTextAnswer(transcript);
        setVoiceFeedback(`Captured: "${transcript}"`);
        await submitActiveAnswer([], transcript);
      }
    }
  };

  const toggleMultiCode = (code: string) => {
    setSelectedMultiCodes((prev) =>
      prev.includes(code) ? prev.filter((c) => c !== code) : [...prev, code]
    );
  };

  const submitChiefComplaintToGraph = async () => {
    setLoading(true);
    try {
      const activeSessionId = sessionId || await ensureBackendSession(language);
      
      // Ensure the clinical interview workflow is initialized in backend LangGraph
      try {
        await intakeService.getNextQuestion(activeSessionId);
      } catch (e) {
        // Initialized
      }

      const complaintSummary = `${chiefComplaint || 'General health evaluation'}. Region: ${bodyRegion || 'general'}. Pain scale: ${painSeverity}/10.`;
      
      const result = await intakeService.submitAnswer(activeSessionId, {
        question_id: '__CHIEF_COMPLAINT__',
        free_text: complaintSummary,
        selected_value_codes: [],
        answer_state: 'ANSWERED',
      });

      // Check for red flags returned by LangGraph scanner
      if (result.new_alerts && result.new_alerts.length > 0) {
        const msg = result.new_alerts[0].alert_message || 'Emergency red-flag symptom detected by clinical graph.';
        triggerEmergency(msg);
        router.push('/triage/alert');
        return;
      }

      if (result.next_question) {
        setActiveQuestion(result.next_question);
        setActiveTab('ADAPTIVE_QUESTION');
        setSelectedOptionCode(null);
        setSelectedMultiCodes([]);
        setFreeTextAnswer('');
      } else {
        finishSymptomIntake();
      }
    } catch (err) {
      console.warn('Backend graph progression fallback to next stage:', err);
      finishSymptomIntake();
    } finally {
      setLoading(false);
    }
  };

  const submitActiveAnswer = async (
    valueCodes?: string[] | null,
    customText?: string | null,
    answerState: 'ANSWERED' | 'UNKNOWN' | 'REFUSED' = 'ANSWERED'
  ) => {
    if (!activeQuestion) return;
    setLoading(true);

    try {
      const activeSessionId = sessionId || await ensureBackendSession(language);
      const codes =
        valueCodes !== undefined
          ? valueCodes
          : activeQuestion.input_type === 'multi_select'
          ? selectedMultiCodes
          : selectedOptionCode
          ? [selectedOptionCode]
          : [];

      const text = customText !== undefined ? customText : freeTextAnswer;

      const result = await intakeService.submitAnswer(activeSessionId, {
        question_id: activeQuestion.question_id,
        selected_value_codes: codes || [],
        free_text: text || null,
        answer_state: answerState,
      });

      if (result.new_alerts && result.new_alerts.length > 0) {
        const msg = result.new_alerts[0].alert_message || 'Critical red-flag symptom reported.';
        triggerEmergency(msg);
        router.push('/triage/alert');
        return;
      }

      if (result.next_question && !result.interview_complete) {
        setActiveQuestion(result.next_question);
        setSelectedOptionCode(null);
        setSelectedMultiCodes([]);
        setFreeTextAnswer('');
        setVoiceFeedback(null);
      } else {
        finishSymptomIntake();
      }
    } catch (err) {
      console.warn('Answer submission advance note:', err);
      finishSymptomIntake();
    } finally {
      setLoading(false);
    }
  };

  const finishSymptomIntake = () => {
    stop();
    if (intakeMode === 'AYUSH') {
      setCurrentScreen('ayush_assessment');
      router.push('/intake/ayush');
    } else {
      setCurrentScreen('document_scanner');
      router.push('/documents/scan');
    }
  };

  const handleProceed = () => {
    if (activeTab === 'COMPLAINT') {
      setActiveTab('BODY_MAP');
    } else if (activeTab === 'BODY_MAP') {
      setActiveTab('PAIN_SCALE');
    } else if (activeTab === 'PAIN_SCALE') {
      submitChiefComplaintToGraph();
    } else if (activeTab === 'ADAPTIVE_QUESTION') {
      submitActiveAnswer();
    }
  };

  const handleBack = () => {
    stop();
    if (activeTab === 'ADAPTIVE_QUESTION') {
      setActiveTab('PAIN_SCALE');
    } else if (activeTab === 'PAIN_SCALE') {
      setActiveTab('BODY_MAP');
    } else if (activeTab === 'BODY_MAP') {
      setActiveTab('COMPLAINT');
    } else {
      setCurrentScreen('consent_capture');
      router.push('/consent');
    }
  };

  return (
    <div className="h-screen w-screen flex flex-col bg-[#f8fafa] overflow-hidden">
      <KioskHeader onBack={handleBack} />
      <StepProgressBar />

      <main className="flex-1 max-w-5xl w-full mx-auto p-4 md:p-8 flex flex-col justify-between overflow-y-auto">
        {/* Title & Phase Header */}
        <div className="text-center mb-2">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#005f53]/10 text-[#005f53] font-bold text-xs uppercase tracking-wider mb-2">
            <Activity className="w-4 h-4" />
            <span>
              {activeTab === 'ADAPTIVE_QUESTION'
                ? activeQuestion?.phase || 'Adaptive SOCRATES Inquiry'
                : 'Conversational Clinical History'}
            </span>
          </div>

          <div className="flex items-center justify-center gap-3">
            <h1 className="text-2xl md:text-3xl font-black text-[#191c1d] tracking-tight">
              {activeTab === 'COMPLAINT' && t('intake.chief_complaint', language)}
              {activeTab === 'BODY_MAP' && 'Where is your pain located?'}
              {activeTab === 'PAIN_SCALE' && t('pain.title', language)}
              {activeTab === 'ADAPTIVE_QUESTION' && (activeQuestion?.question_text || 'Clinical Follow-up')}
            </h1>

            {activeTab === 'ADAPTIVE_QUESTION' && activeQuestion?.question_text && (
              <button
                type="button"
                onClick={() => speak(activeQuestion.question_text, language)}
                aria-label="Replay question audio"
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

          {/* Voice Feedback Banner */}
          {voiceFeedback && (
            <div className="inline-flex items-center gap-2 mt-2 px-4 py-1.5 rounded-full bg-[#005f53]/10 text-[#005f53] text-xs font-bold animate-fade-in-up">
              <Sparkles className="w-3.5 h-3.5" />
              <span>{voiceFeedback}</span>
            </div>
          )}
        </div>

        {/* 4 Step Pills */}
        <div className="flex flex-wrap justify-center gap-2 mb-4">
          <button
            type="button"
            onClick={() => setActiveTab('COMPLAINT')}
            className={`px-4 py-1.5 rounded-full text-xs font-bold transition-all cursor-pointer ${
              activeTab === 'COMPLAINT'
                ? 'bg-[#005f53] text-white shadow-xs'
                : 'bg-[#eceeee] text-[#3e4946]'
            }`}
          >
            1. Chief Complaint {chiefComplaint && '✓'}
          </button>
          <button
            type="button"
            onClick={() => setActiveTab('BODY_MAP')}
            className={`px-4 py-1.5 rounded-full text-xs font-bold transition-all cursor-pointer ${
              activeTab === 'BODY_MAP'
                ? 'bg-[#005f53] text-white shadow-xs'
                : 'bg-[#eceeee] text-[#3e4946]'
            }`}
          >
            2. Body Map {bodyRegion && '✓'}
          </button>
          <button
            type="button"
            onClick={() => setActiveTab('PAIN_SCALE')}
            className={`px-4 py-1.5 rounded-full text-xs font-bold transition-all cursor-pointer ${
              activeTab === 'PAIN_SCALE'
                ? 'bg-[#005f53] text-white shadow-xs'
                : 'bg-[#eceeee] text-[#3e4946]'
            }`}
          >
            3. Pain Scale {painSeverity > 0 && `(${painSeverity}/10)`}
          </button>
          {activeQuestion && (
            <button
              type="button"
              onClick={() => setActiveTab('ADAPTIVE_QUESTION')}
              className={`px-4 py-1.5 rounded-full text-xs font-bold transition-all cursor-pointer ${
                activeTab === 'ADAPTIVE_QUESTION'
                  ? 'bg-[#005f53] text-white shadow-xs'
                  : 'bg-[#eceeee] text-[#3e4946]'
              }`}
            >
              4. Adaptive Inquiries
            </button>
          )}
        </div>

        {/* Tab 1: Chief Complaint Quick Chips */}
        {activeTab === 'COMPLAINT' && (
          <div className="flex-1 flex flex-col items-center justify-center my-auto">
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 w-full max-w-4xl mb-6">
              {COMMON_CHIEF_COMPLAINTS.map((item) => {
                const isSelected = chiefComplaint === item.text;
                return (
                  <button
                    key={item.id}
                    type="button"
                    id={`complaint-${item.id}`}
                    data-element={`complaint-chip-${item.id}`}
                    data-voice-action={`select-${item.id}`}
                    data-testid={`complaint-${item.id}`}
                    onClick={() => handleSelectComplaint(item)}
                    className={`h-24 p-4 rounded-2xl font-bold text-sm md:text-base flex flex-col items-center justify-center text-center transition-all cursor-pointer border ${
                      isSelected
                        ? 'bg-[#005f53] text-white border-transparent shadow-lg scale-102 ring-2 ring-[#005f53]/30'
                        : 'bg-white hover:bg-[#eceeee] text-[#191c1d] border-[#bdc9c5]/60 hover:border-[#005f53]'
                    }`}
                  >
                    <span>{item.text}</span>
                    {item.redFlag && (
                      <span className="text-[10px] mt-1 px-2 py-0.5 rounded-full bg-[#aa0a17]/10 text-[#aa0a17] font-bold flex items-center gap-1">
                        <ShieldAlert className="w-3 h-3" /> Priority
                      </span>
                    )}
                  </button>
                );
              })}
            </div>

            <VoiceOrb
              promptText={t('intake.chief_complaint', language)}
              onTranscriptReady={handleVoiceTranscript}
              inline
            />
          </div>
        )}

        {/* Tab 2: Interactive Body Map */}
        {activeTab === 'BODY_MAP' && (
          <div className="flex-1 flex flex-col items-center justify-center my-auto">
            <BodyMapSelector
              selectedRegion={bodyRegion}
              onSelectRegion={(reg) => setBodyRegion(reg)}
            />
          </div>
        )}

        {/* Tab 3: Pain Severity Slider */}
        {activeTab === 'PAIN_SCALE' && (
          <div className="flex-1 flex flex-col items-center justify-center my-auto">
            <PainSeveritySlider
              value={painSeverity}
              onChange={(val) => setPainSeverity(val)}
            />
          </div>
        )}

        {/* Tab 4: Live Adaptive Clinical Questioning */}
        {activeTab === 'ADAPTIVE_QUESTION' && activeQuestion && (
          <div className="flex-1 flex flex-col items-center justify-center my-auto w-full max-w-3xl mx-auto">
            {/* Options Grid (Single or Multi-select) */}
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
                            submitActiveAnswer([opt.value_code]);
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
                      onClick={() => submitActiveAnswer(selectedMultiCodes)}
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
                onClick={() => submitActiveAnswer([], null, 'UNKNOWN')}
                className="px-4 py-2 rounded-full bg-[#eceeee] hover:bg-[#e1e3e3] text-[#3e4946] text-xs font-bold transition-all cursor-pointer"
              >
                Not sure / Don&apos;t know
              </button>
              <button
                type="button"
                onClick={() => submitActiveAnswer([], null, 'REFUSED')}
                className="px-4 py-2 rounded-full bg-[#eceeee] hover:bg-[#e1e3e3] text-[#3e4946] text-xs font-bold transition-all cursor-pointer"
              >
                Prefer not to say
              </button>
            </div>

            {/* Voice Orb for Adaptive Question */}
            <VoiceOrb
              promptText={activeQuestion.question_text}
              onTranscriptReady={handleVoiceTranscript}
              inline
            />
          </div>
        )}
      </main>

      <KioskFooter
        onNext={handleProceed}
        onBack={handleBack}
        nextText={
          loading
            ? 'Processing...'
            : activeTab === 'ADAPTIVE_QUESTION'
            ? 'Next Question'
            : activeTab === 'PAIN_SCALE'
            ? 'Start Clinical Inquiry'
            : 'Next Step'
        }
      />
    </div>
  );
}
