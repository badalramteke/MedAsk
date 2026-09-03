/**
 * MediKiosk — Symptom Intake & LangGraph Adaptive Engine (/intake/symptoms)
 * Screen 06: Dual-mode voice & touch intake with interactive body map,
 * pain severity slider, real-time emergency red-flag detection,
 * and live LangGraph adaptive clinical question progression.
 */

'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import KioskHeader from '@/components/layout/KioskHeader';
import KioskFooter from '@/components/layout/KioskFooter';
import StepProgressBar from '@/components/layout/StepProgressBar';
import VoiceOrb from '@/components/voice/VoiceOrb';
import BodyMapSelector from '@/components/interactive/BodyMapSelector';
import PainSeveritySlider from '@/components/interactive/PainSeveritySlider';
import OptionCard from '@/components/interactive/OptionCard';
import { useSessionStore } from '@/stores/useSessionStore';
import { useFlowStore } from '@/stores/useFlowStore';
import { useIntakeStore } from '@/stores/useIntakeStore';
import { intakeService } from '@/services/intakeService';
import type { QuestionResponse } from '@/lib/types';
import { t } from '@/lib/i18n';
import { Activity, HelpCircle, CheckCircle2, RefreshCw } from 'lucide-react';

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

  const [activeTab, setActiveTab] = useState<'COMPLAINT' | 'BODY_MAP' | 'PAIN_SCALE' | 'ADAPTIVE_QUESTION'>('COMPLAINT');
  const [activeQuestion, setActiveQuestion] = useState<QuestionResponse | null>(null);
  const [selectedOptionCode, setSelectedOptionCode] = useState<string | null>(null);
  const [freeTextAnswer, setFreeTextAnswer] = useState<string>('');
  const [loading, setLoading] = useState(false);

  const handleSelectComplaint = (complaint: (typeof COMMON_CHIEF_COMPLAINTS)[0]) => {
    setChiefComplaint(complaint.text);

    // Immediate Red-Flag rule evaluation
    if (complaint.redFlag && complaint.id === 'chest_pain') {
      triggerEmergency('Acute Chest Pain reported: potential acute coronary syndrome / cardiac red-flag');
      router.push('/triage/alert');
      return;
    }

    setActiveTab('BODY_MAP');
  };

  const handleVoiceTranscript = async (transcript: string) => {
    if (activeTab === 'ADAPTIVE_QUESTION' && activeQuestion) {
      // Voice answering current question
      setFreeTextAnswer(transcript);
      await submitActiveAnswer(null, transcript);
      return;
    }

    // Voice answering chief complaint
    setChiefComplaint(transcript);

    const lower = transcript.toLowerCase();
    if (
      lower.includes('chest pain') ||
      lower.includes('heart') ||
      lower.includes('attack') ||
      lower.includes('breath') ||
      lower.includes('stroke') ||
      lower.includes('छाती में दर्द')
    ) {
      triggerEmergency(`Voice trigger: "${transcript}" — Urgent triage required`);
      router.push('/triage/alert');
      return;
    }
  };

  const submitChiefComplaintToGraph = async () => {
    setLoading(true);
    try {
      const activeSessionId = sessionId || await ensureBackendSession(language);
      
      // Ensure the clinical interview workflow is initialized in backend LangGraph
      try {
        await intakeService.getNextQuestion(activeSessionId);
      } catch (e) {
        // Continue if already started
      }

      const complaintSummary = `${chiefComplaint || 'General checkup'}. Region: ${bodyRegion || 'general'}. Pain scale: ${painSeverity}/10.`;
      
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

  const submitActiveAnswer = async (valueCode?: string | null, customText?: string | null) => {
    if (!activeQuestion) return;
    setLoading(true);

    try {
      const activeSessionId = sessionId || await ensureBackendSession(language);
      const code = valueCode || selectedOptionCode;
      const text = customText !== undefined ? customText : freeTextAnswer;

      const result = await intakeService.submitAnswer(activeSessionId, {
        question_id: activeQuestion.question_id,
        selected_value_codes: code ? [code] : [],
        free_text: text || null,
        answer_state: 'ANSWERED',
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
        setFreeTextAnswer('');
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
        {/* Title Header */}
        <div className="text-center mb-2">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#005f53]/10 text-[#005f53] font-bold text-xs uppercase tracking-wider mb-2">
            <Activity className="w-4 h-4" />
            <span>SOCRATES Clinical History Intake</span>
          </div>
          <h1 className="text-2xl md:text-3xl font-black text-[#191c1d] tracking-tight">
            {activeTab === 'COMPLAINT' && t('intake.chief_complaint', language)}
            {activeTab === 'BODY_MAP' && 'Where is your pain located?'}
            {activeTab === 'PAIN_SCALE' && t('pain.title', language)}
            {activeTab === 'ADAPTIVE_QUESTION' && (activeQuestion?.question_text || 'Clinical Follow-up')}
          </h1>
          <p className="text-xs md:text-sm text-[#3e4946] mt-1">
            Tap an option below or speak into the microphone.
          </p>
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
              4. Follow-up Inquiry
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
                      <span className="text-[10px] mt-1 px-2 py-0.5 rounded-full bg-[#aa0a17]/10 text-[#aa0a17] font-bold">
                        Priority
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

        {/* Tab 4: Live LangGraph Adaptive Question */}
        {activeTab === 'ADAPTIVE_QUESTION' && activeQuestion && (
          <div className="flex-1 flex flex-col items-center justify-center my-auto w-full max-w-3xl mx-auto">
            {/* Question Options or Free Text */}
            {activeQuestion.options && activeQuestion.options.length > 0 ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 w-full mb-6">
                {activeQuestion.options.map((opt) => {
                  const isSelected = selectedOptionCode === opt.value_code;
                  return (
                    <button
                      key={opt.option_id || opt.value_code}
                      type="button"
                      onClick={() => {
                        setSelectedOptionCode(opt.value_code);
                        submitActiveAnswer(opt.value_code);
                      }}
                      className={`min-h-[100px] p-5 rounded-3xl text-left flex items-center justify-between transition-all cursor-pointer border ${
                        isSelected
                          ? 'bg-[#005f53] text-white border-transparent shadow-lg scale-102'
                          : 'bg-white hover:bg-[#eceeee] text-[#191c1d] border-[#bdc9c5]/60 hover:border-[#005f53]'
                      }`}
                    >
                      <span className="font-bold text-base md:text-lg">
                        {opt.text}
                      </span>
                      {isSelected && <CheckCircle2 className="w-6 h-6 text-white" />}
                    </button>
                  );
                })}
              </div>
            ) : (
              <div className="w-full mb-6">
                <input
                  type="text"
                  placeholder="Type or speak your answer..."
                  value={freeTextAnswer}
                  onChange={(e) => setFreeTextAnswer(e.target.value)}
                  className="w-full h-16 px-6 rounded-2xl border-2 border-[#005f53] text-lg bg-white focus:outline-none"
                />
              </div>
            )}

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
