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
import SingleSelectCard from '@/components/interactive/SingleSelectCard';
import MultiSelectCard from '@/components/interactive/MultiSelectCard';
import { useSessionStore } from '@/stores/useSessionStore';
import { useFlowStore } from '@/stores/useFlowStore';
import { useIntakeStore } from '@/stores/useIntakeStore';
import { useVoiceStore } from '@/stores/useVoiceStore';
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
  Keyboard,
} from 'lucide-react';
import {
  SymptomIcon,
  HealthStethoscope,
  Person as HealthPerson,
  Pain as HealthPain,
  Doctor as HealthDoctor,
  Positive,
  Negative,
} from '@/components/icons/ClinicalIcon';

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
    symptomsTab,
    setSymptomsTab,
    chiefComplaint,
    setChiefComplaint,
    bodyRegion,
    setBodyRegion,
    painSeverity,
    setPainSeverity,
    activeQuestion,
    setActiveQuestion,
    pushQuestionHistory,
    popQuestionHistory,
    freeTextAnswer,
    setFreeTextAnswer,
    selectedOptionCode,
    setSelectedOptionCode,
    selectedMultiCodes,
    setSelectedMultiCodes,
  } = useIntakeStore();

  const { speak, isSpeaking, stop } = useTTS();
  const activeTab = symptomsTab;
  const setActiveTab = setSymptomsTab;

  useEffect(() => {
    setCurrentScreen('chief_complaint');
  }, [setCurrentScreen]);

  const [voiceFeedback, setVoiceFeedback] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [showKeyboardInput, setShowKeyboardInput] = useState(false);

  const handleReadOptions = useCallback(() => {
    if (!activeQuestion?.options || activeQuestion.options.length === 0) return;
    const listText = activeQuestion.options.map((opt, i) => `${i + 1}. ${opt.text}`).join('. ');
    speak(`Options are: ${listText}`, language);
  }, [activeQuestion, language, speak]);

  // Voice Guidance: Spoken prompt on tab/question change (does not auto-trigger mic or beep)
  useEffect(() => {
    let promptMsg = '';
    if (activeTab === 'COMPLAINT') {
      promptMsg = t('intake.chief_complaint', language) || 'What brings you to the hospital today? Please select or tell me what you are experiencing.';
    } else if (activeTab === 'BODY_MAP') {
      promptMsg = 'Where is your pain or discomfort located? Tap on the body map or tell me the location.';
    } else if (activeTab === 'PAIN_SCALE') {
      promptMsg = 'On a scale from 0 to 10, how severe is your pain? Say a number or tap the slider.';
    } else if (activeTab === 'ADAPTIVE_QUESTION' && activeQuestion?.question_text) {
      promptMsg = activeQuestion.question_text;
    }

    if (promptMsg) {
      speak(promptMsg, language);
    }

    return () => {
      stop();
    };
  }, [activeTab, activeQuestion?.question_id, language, speak, stop]);

  const handleSelectComplaint = (complaint: (typeof COMMON_CHIEF_COMPLAINTS)[0]) => {
    setChiefComplaint(complaint.text);

    // Immediate Red-Flag rule evaluation
    if (complaint.redFlag && (complaint.id === 'chest_pain' || complaint.id === 'shortness_of_breath')) {
      triggerEmergency(
        `Critical symptom selected: "${complaint.text}" — Urgent clinical evaluation required.`,
        '/intake/symptoms'
      );
      router.push('/triage/alert');
      return;
    }

    setActiveTab('BODY_MAP');
  };

  /**
   * Spoken voice answer handler:
   * 1. Checks emergency keywords in transcript.
   * 2. Checks voice navigation commands (repeat, read-options, skip).
   * 3. Conversational symptom & MCQ matching with automatic progression!
   */
  const handleVoiceTranscript = async (transcript: string) => {
    if (!transcript) return;
    const lower = transcript.toLowerCase().trim();

    // Distinguish family / relative history from acute patient emergencies
    const isFamilyOrRelative =
      lower.includes('family') ||
      lower.includes('relative') ||
      lower.includes('father') ||
      lower.includes('mother') ||
      lower.includes('dad') ||
      lower.includes('mom') ||
      lower.includes('brother') ||
      lower.includes('sister') ||
      lower.includes('grandfather') ||
      lower.includes('grandmother') ||
      lower.includes('parent') ||
      lower.includes('he ') ||
      lower.includes("he's") ||
      lower.includes('he was') ||
      lower.includes('he has') ||
      lower.includes('his ') ||
      lower.includes('she ') ||
      lower.includes("she's") ||
      lower.includes('she was') ||
      lower.includes('she has') ||
      lower.includes('her ') ||
      lower.includes('pita') ||
      lower.includes('mata') ||
      lower.includes('bhai') ||
      lower.includes('behen') ||
      lower.includes('परिवार') ||
      lower.includes('पिता') ||
      lower.includes('माता') ||
      Boolean(
        activeQuestion && (
          activeQuestion.question_id?.includes('FH') ||
          activeQuestion.phase === 'GENERAL_HISTORY' ||
          activeQuestion.question_text?.toLowerCase().includes('family')
        )
      );

    // Only check acute presenting red-flags if this is patient acute symptom context
    const isAcuteEmergency =
      !isFamilyOrRelative &&
      (
        lower.includes('acute chest pain') ||
        lower.includes('crushing chest pain') ||
        (lower.includes('chest pain') && (lower.includes('arm') || lower.includes('jaw') || lower.includes('sweat') || lower.includes('severe'))) ||
        lower.includes('cannot breathe') ||
        lower.includes('difficulty breathing right now') ||
        lower.includes('severe shortness of breath') ||
        (lower.includes('paralysis') && !lower.includes('history')) ||
        lower.includes('छाती में तेज दर्द') ||
        lower.includes('सांस नहीं आ रही')
      );

    if (isAcuteEmergency) {
      triggerEmergency(
        `Spoken red-flag: "${transcript}" — Urgent triage required`,
        '/intake/symptoms'
      );
      router.push('/triage/alert');
      return;
    }

    // Tab 1: Chief Complaint (Conversational match)
    if (activeTab === 'COMPLAINT') {
      const matched = COMMON_CHIEF_COMPLAINTS.find((c) => {
        const textLow = c.text.toLowerCase();
        const idLow = c.id.replace(/_/g, ' ');
        return lower.includes(textLow) || textLow.includes(lower) || lower.includes(idLow);
      });

      if (matched) {
        setVoiceFeedback(`Recognized: "${matched.text}"`);
        handleSelectComplaint(matched);
      } else {
        // Custom spoken complaint
        setChiefComplaint(transcript);
        setVoiceFeedback(`Recorded: "${transcript}"`);
        setTimeout(() => {
          setActiveTab('BODY_MAP');
        }, 500);
      }
      return;
    }

    // Tab 2: Body Map
    if (activeTab === 'BODY_MAP') {
      const regions = ['head', 'chest', 'abdomen', 'stomach', 'pelvis', 'back', 'arms', 'legs', 'knee', 'joints', 'neck', 'shoulder'];
      const matchedRegion = regions.find((r) => lower.includes(r));
      if (matchedRegion) {
        const mapped = matchedRegion === 'stomach' ? 'abdomen' : matchedRegion;
        setBodyRegion(mapped);
        setVoiceFeedback(`Location: "${mapped}"`);
        setTimeout(() => {
          setActiveTab('PAIN_SCALE');
        }, 500);
        return;
      }
      if (lower.includes('next') || lower.includes('aage') || lower.includes('continue')) {
        setActiveTab('PAIN_SCALE');
        return;
      }
    }

    // Tab 3: Pain Scale
    if (activeTab === 'PAIN_SCALE') {
      const numMatch = lower.match(/\b([0-9]|10)\b/);
      const wordMap: Record<string, number> = {
        zero: 0, one: 1, two: 2, three: 3, four: 4, five: 5, six: 6, seven: 7, eight: 8, nine: 9, ten: 10,
        shunya: 0, ek: 1, do: 2, teen: 3, chaar: 4, paanch: 5, chheh: 6, saat: 7, aath: 8, nau: 9, das: 10
      };
      let val: number | null = null;
      if (numMatch) {
        val = parseInt(numMatch[1], 10);
      } else {
        for (const [w, n] of Object.entries(wordMap)) {
          if (lower.includes(w)) {
            val = n;
            break;
          }
        }
      }

      if (val !== null) {
        setPainSeverity(val);
        setVoiceFeedback(`Pain: ${val}/10`);
        setTimeout(() => {
          submitChiefComplaintToGraph();
        }, 500);
        return;
      }

      if (lower.includes('start') || lower.includes('shuru') || lower.includes('next') || lower.includes('aage')) {
        submitChiefComplaintToGraph();
        return;
      }
    }

    // Tab 4: Live Adaptive Clinical Questioning (Auto MCQ Match & Advance)
    if (activeTab === 'ADAPTIVE_QUESTION' && activeQuestion) {
      if (lower.includes('dobara') || lower.includes('repeat') || lower.includes('phir se') || lower.includes('bolo')) {
        speak(activeQuestion.question_text, language);
        return;
      }
      if (lower.includes('read options') || lower.includes('vikalp') || lower.includes('options padho')) {
        handleReadOptions();
        return;
      }
      if (lower.includes('skip') || lower.includes('unsure') || lower.includes('pta nahi') || lower.includes('nahi pta') || lower.includes("don't know")) {
        await submitActiveAnswer([], null, 'UNKNOWN');
        return;
      }

      // Intercept "next" / "continue" voice commands so they never get submitted as free-text
      const trimmed = lower.trim();
      if (
        trimmed === 'next' ||
        trimmed === 'aage' ||
        trimmed === 'continue' ||
        trimmed === 'आगे' ||
        trimmed === 'next question' ||
        trimmed === 'aage badho'
      ) {
        if (selectedOptionCode) {
          await submitActiveAnswer([selectedOptionCode]);
        } else if (selectedMultiCodes.length > 0) {
          await submitActiveAnswer(selectedMultiCodes);
        } else if (freeTextAnswer.trim()) {
          await submitActiveAnswer([], freeTextAnswer.trim());
        } else {
          setVoiceFeedback(
            language === 'hi'
              ? 'कृपया आगे बढ़ने के लिए स्क्रीन पर एक विकल्प चुनें।'
              : 'Please select an option on screen before continuing.'
          );
        }
        return;
      }

      // Check for negative intent (e.g. "I do not take substances", "nahi lete", "no", "never", "none")
      const words = lower.replace(/[.,\/#!$%\^&\*;:{}=\-_`~()?'"|।]/g, ' ').split(/\s+/);
      const isNegative =
        words.includes('no') ||
        words.includes('none') ||
        words.includes('never') ||
        words.includes('nahi') ||
        words.includes('not') ||
        lower.includes('do not') ||
        lower.includes("don't") ||
        lower.includes('kuch nahi') ||
        lower.includes('nahi leta') ||
        lower.includes('nahi lete');

      if (isNegative && activeQuestion.options && activeQuestion.options.length > 0) {
        const noOpt = activeQuestion.options.find(
          (o) =>
            o.value_code.endsWith('_NO') ||
            o.value_code.includes('NONE') ||
            o.value_code.includes('NOT') ||
            o.text.toLowerCase().startsWith('no') ||
            o.text.toLowerCase().includes('नहीं') ||
            o.text.toLowerCase().includes('नाही')
        );
        if (noOpt) {
          setVoiceFeedback(`Recognized: "${noOpt.text}"`);
          setSelectedOptionCode(noOpt.value_code);
          setTimeout(() => {
            submitActiveAnswer([noOpt.value_code], null);
          }, 350);
          return;
        }
      }

      // Strip conversational prefixes ("I am having...", "I have...", "Mujhe...")
      const core = lower.replace(/(i am having|i have|i am experiencing|mujhe|mere|mera|hai|dard|ka problem|problem|issue)/gi, '').trim();

      // Check if patient answered with an option name
      let matchedOpt: QuestionOption | null = null;
      if (activeQuestion.options && activeQuestion.options.length > 0) {
        for (const opt of activeQuestion.options) {
          const optText = opt.text.toLowerCase();
          const valCode = opt.value_code.toLowerCase().replace(/_/g, ' ');
          if (
            lower.includes(optText) ||
            optText.includes(lower) ||
            lower.includes(valCode) ||
            (core.length > 2 && (optText.includes(core) || core.includes(optText)))
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
          setTimeout(() => {
            submitActiveAnswer([matchedOpt!.value_code], null);
          }, 400);
        }
      } else {
        // Free-text submission
        setFreeTextAnswer(transcript);
        setVoiceFeedback(`Captured: "${transcript}"`);
        await submitActiveAnswer([], transcript);
      }
    }
  };

  const toggleMultiCode = (code: string) => {
    const next = selectedMultiCodes.includes(code)
      ? selectedMultiCodes.filter((c) => c !== code)
      : [...selectedMultiCodes, code];
    setSelectedMultiCodes(next);
  };

  const submitChiefComplaintToGraph = async () => {
    setLoading(true);
    try {
      const activeSessionId = sessionId || (await ensureBackendSession(language));
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
        triggerEmergency(msg, '/intake/symptoms');
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
      console.warn('Backend graph progression notice, using clinical fallback:', err);
      // Fallback SOCRATES question to ensure smooth uninterrupted intake
      setActiveQuestion({
        question_id: 'SOC_FALLBACK_ONSET',
        question_text: language === 'hi'
          ? 'यह तकलीफ या लक्षण कब शुरू हुआ?'
          : 'When did this discomfort or symptom begin?',
        input_type: 'single_select',
        phase: 'SOCRATES_DEEP_DIVE',
        options: [
          { option_id: 'sudden', text: language === 'hi' ? 'अचानक (कुछ ही मिनटों में)' : 'Suddenly (within minutes)', value_code: 'SUDDEN' },
          { option_id: 'hours', text: language === 'hi' ? 'कुछ घंटे पहले' : 'A few hours ago', value_code: 'FEW_HOURS' },
          { option_id: 'days', text: language === 'hi' ? 'पिछले 1–2 दिनों से' : 'Past 1–2 days', value_code: 'FEW_DAYS' },
          { option_id: 'chronic', text: language === 'hi' ? 'एक सप्ताह से अधिक समय से' : 'More than a week ago', value_code: 'CHRONIC' },
        ],
      });
      setActiveTab('ADAPTIVE_QUESTION');
      setSelectedOptionCode(null);
      setSelectedMultiCodes([]);
      setFreeTextAnswer('');
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

    const codes =
      valueCodes !== undefined
        ? valueCodes
        : activeQuestion.input_type === 'multi_select'
        ? selectedMultiCodes
        : selectedOptionCode
        ? [selectedOptionCode]
        : [];

    const text = customText !== undefined ? customText : freeTextAnswer;

    // Guard: Prevent empty submissions from failing and accidentally skipping to documents
    if (
      answerState === 'ANSWERED' &&
      (!codes || codes.length === 0) &&
      (!text || !text.trim())
    ) {
      setVoiceFeedback(
        language === 'hi'
          ? 'कृपया आगे बढ़ने के लिए स्क्रीन पर एक विकल्प चुनें।'
          : 'Please select an option on screen before continuing.'
      );
      return;
    }

    setLoading(true);

    try {
      const activeSessionId = sessionId || (await ensureBackendSession(language));

      const result = await intakeService.submitAnswer(activeSessionId, {
        question_id: activeQuestion.question_id,
        selected_value_codes: codes || [],
        free_text: text ? text.trim() : null,
        answer_state: answerState,
      });

      if (result.new_alerts && result.new_alerts.length > 0) {
        const msg = result.new_alerts[0].alert_message || 'Critical red-flag symptom reported.';
        triggerEmergency(msg, '/intake/symptoms');
        router.push('/triage/alert');
        return;
      }

      // Always clear previous voice transcript when transitioning question
      useVoiceStore.getState().clearTranscript();

      if (result.next_question && !result.interview_complete) {
        if (activeQuestion) {
          pushQuestionHistory(activeQuestion);
        }
        setActiveQuestion(result.next_question);
        setSelectedOptionCode(null);
        setSelectedMultiCodes([]);
        setFreeTextAnswer('');
        setVoiceFeedback(null);
        setShowKeyboardInput(false);
      } else {
        finishSymptomIntake();
      }
    } catch (err) {
      console.warn('Answer submission error note:', err);
      // NEVER prematurely advance to documents on submission error
      setVoiceFeedback(
        language === 'hi'
          ? 'उत्तर दर्ज करने में समस्या हुई। कृपया पुनः प्रयास करें।'
          : 'Could not record response. Please select an option to retry.'
      );
    } finally {
      setLoading(false);
    }
  };

  const finishSymptomIntake = () => {
    stop();
    useVoiceStore.getState().clearTranscript();
    if (intakeMode === 'AYUSH') {
      setCurrentScreen('ayush_assessment');
      router.push('/intake/ayush');
    } else {
      setCurrentScreen('document_scanner');
      router.push('/documents/scan');
    }
  };

  const handleProceed = () => {
    useVoiceStore.getState().clearTranscript();
    if (activeTab === 'COMPLAINT') {
      setActiveTab('BODY_MAP');
    } else if (activeTab === 'BODY_MAP') {
      setActiveTab('PAIN_SCALE');
    } else if (activeTab === 'PAIN_SCALE') {
      submitChiefComplaintToGraph();
    } else if (activeTab === 'ADAPTIVE_QUESTION') {
      // Validate option selection before firing submit
      if (
        activeQuestion?.input_type === 'single_select' &&
        !selectedOptionCode &&
        !freeTextAnswer.trim()
      ) {
        setVoiceFeedback(
          language === 'hi'
            ? 'कृपया आगे बढ़ने के लिए स्क्रीन पर एक विकल्प चुनें।'
            : 'Please select an option before continuing.'
        );
        return;
      }
      if (
        activeQuestion?.input_type === 'multi_select' &&
        selectedMultiCodes.length === 0 &&
        !freeTextAnswer.trim()
      ) {
        setVoiceFeedback(
          language === 'hi'
            ? 'कृपया एक या अधिक विकल्प चुनें।'
            : 'Please select one or more options before continuing.'
        );
        return;
      }
      submitActiveAnswer();
    }
  };

  const handleBack = () => {
    stop();
    useVoiceStore.getState().clearTranscript();
    if (activeTab === 'ADAPTIVE_QUESTION') {
      const prevQ = popQuestionHistory();
      if (prevQ) {
        setActiveQuestion(prevQ);
        setSelectedOptionCode(null);
        setSelectedMultiCodes([]);
        setFreeTextAnswer('');
        setShowKeyboardInput(false);
        return;
      }
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
                : t('intake.header_badge', language)}
            </span>
          </div>

          <div className="flex items-center justify-center gap-3">
            <h1 className="text-2xl md:text-3xl font-black text-[#191c1d] tracking-tight">
              {activeTab === 'COMPLAINT' && t('intake.chief_complaint', language)}
              {activeTab === 'BODY_MAP' && t('intake.body_map_title', language)}
              {activeTab === 'PAIN_SCALE' && t('pain.title', language)}
              {activeTab === 'ADAPTIVE_QUESTION' && (activeQuestion?.question_text || 'Clinical Follow-up')}
            </h1>

            {activeTab === 'ADAPTIVE_QUESTION' && activeQuestion?.question_text && (
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  data-voice-action="repeat"
                  data-voice-label="Replay Question"
                  onClick={() => speak(activeQuestion.question_text, language)}
                  aria-label="Replay question audio"
                  className="p-2 rounded-full bg-[#eceeee] hover:bg-[#e1e3e3] text-[#005f53] transition-all cursor-pointer shadow-xs"
                  title="Listen to question"
                >
                  <Volume2 className={`w-5 h-5 ${isSpeaking ? 'animate-bounce text-[#0f7a6b]' : ''}`} />
                </button>
                {activeQuestion.options && activeQuestion.options.length > 0 && (
                  <button
                    type="button"
                    data-voice-action="read-options"
                    data-voice-label="Read Options Aloud"
                    onClick={handleReadOptions}
                    aria-label="Read out options"
                    className="px-3 py-1.5 rounded-full bg-[#eceeee] hover:bg-[#e1e3e3] text-[#005f53] text-xs font-bold transition-all cursor-pointer flex items-center gap-1.5 shadow-xs"
                    title="Read options aloud"
                  >
                    <Volume2 className="w-3.5 h-3.5" />
                    <span>{t('intake.read_options', language)}</span>
                  </button>
                )}
              </div>
            )}
          </div>

          <p className="text-xs md:text-sm text-[#3e4946] mt-1">
            {t('intake.interaction_hint', language)}
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
            className={`px-4 py-1.5 rounded-full text-xs font-bold transition-all cursor-pointer flex items-center gap-1.5 ${
              activeTab === 'COMPLAINT'
                ? 'bg-[#005f53] text-white shadow-xs'
                : 'bg-[#eceeee] text-[#3e4946]'
            }`}
          >
            <HealthStethoscope className="w-3.5 h-3.5" />
            <span>{t('intake.tab_complaint', language)} {chiefComplaint && '✓'}</span>
          </button>
          <button
            type="button"
            onClick={() => setActiveTab('BODY_MAP')}
            className={`px-4 py-1.5 rounded-full text-xs font-bold transition-all cursor-pointer flex items-center gap-1.5 ${
              activeTab === 'BODY_MAP'
                ? 'bg-[#005f53] text-white shadow-xs'
                : 'bg-[#eceeee] text-[#3e4946]'
            }`}
          >
            <HealthPerson className="w-3.5 h-3.5" />
            <span>{t('intake.tab_body_map', language)} {bodyRegion && '✓'}</span>
          </button>
          <button
            type="button"
            onClick={() => setActiveTab('PAIN_SCALE')}
            className={`px-4 py-1.5 rounded-full text-xs font-bold transition-all cursor-pointer flex items-center gap-1.5 ${
              activeTab === 'PAIN_SCALE'
                ? 'bg-[#005f53] text-white shadow-xs'
                : 'bg-[#eceeee] text-[#3e4946]'
            }`}
          >
            <HealthPain className="w-3.5 h-3.5" />
            <span>{t('intake.tab_pain_scale', language)} {painSeverity > 0 && `(${painSeverity}/10)`}</span>
          </button>
          {activeQuestion && (
            <button
              type="button"
              onClick={() => setActiveTab('ADAPTIVE_QUESTION')}
              className={`px-4 py-1.5 rounded-full text-xs font-bold transition-all cursor-pointer flex items-center gap-1.5 ${
                activeTab === 'ADAPTIVE_QUESTION'
                  ? 'bg-[#005f53] text-white shadow-xs'
                  : 'bg-[#eceeee] text-[#3e4946]'
              }`}
            >
              <HealthDoctor className="w-3.5 h-3.5" />
              <span>{t('intake.tab_adaptive', language)}</span>
            </button>
          )}
        </div>

        {/* Tab 1: Chief Complaint Quick Chips */}
        {activeTab === 'COMPLAINT' && (
          <div className="flex-1 flex flex-col items-center justify-center my-auto">
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 w-full max-w-4xl mb-6">
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
                    className={`min-h-[120px] p-4 rounded-2xl font-bold text-sm md:text-base flex flex-col items-center justify-center text-center transition-all cursor-pointer border group ${
                      isSelected
                        ? 'bg-[#005f53] text-white border-transparent shadow-lg scale-102 ring-2 ring-[#005f53]/30'
                        : 'bg-white hover:bg-[#eceeee] text-[#191c1d] border-[#bdc9c5]/60 hover:border-[#005f53]'
                    }`}
                  >
                    <div className="w-12 h-12 rounded-xl flex items-center justify-center mb-2 transition-transform group-hover:scale-110">
                      <SymptomIcon id={item.id} className={`w-10 h-10 ${isSelected ? 'text-white' : ''}`} />
                    </div>
                    <span className="leading-tight">{t(`symptom.${item.id}`, language) || item.text}</span>
                    {item.redFlag && (
                      <span className="text-[10px] mt-1.5 px-2 py-0.5 rounded-full bg-[#aa0a17]/10 text-[#aa0a17] font-bold flex items-center gap-1">
                        <ShieldAlert className="w-3 h-3" /> {t('intake.priority_badge', language)}
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
            {/* 1. Specialized Slider Question (e.g. Severity) */}
            {activeQuestion.input_type === 'slider' ? (
              <div className="w-full mb-6 flex flex-col items-center">
                <PainSeveritySlider
                  value={painSeverity}
                  onChange={(val) => setPainSeverity(val)}
                />
                <button
                  type="button"
                  data-voice-action="confirm"
                  onClick={() => submitActiveAnswer([painSeverity.toString()], `Severity: ${painSeverity}/10`)}
                  className="mt-6 px-8 py-3.5 rounded-full bg-[#005f53] hover:bg-[#0f7a6b] text-white font-bold text-base shadow-md cursor-pointer transition-all active:scale-95 flex items-center gap-2"
                >
                  <CheckCircle2 className="w-5 h-5" />
                  <span>{t('intake.confirm_severity', language)} ({painSeverity}/10)</span>
                </button>
              </div>
            ) : activeQuestion.input_type === 'body_map' ? (
              /* 2. Specialized 2D Body Map Question */
              <div className="w-full mb-6 flex flex-col items-center">
                <BodyMapSelector
                  selectedRegion={bodyRegion}
                  onSelectRegion={(reg) => {
                    setBodyRegion(reg);
                    submitActiveAnswer([reg], `Location: ${reg}`);
                  }}
                />
              </div>
            ) : activeQuestion.options && activeQuestion.options.length > 0 ? (
              /* 3. Multi-Select or Single-Select Responsive Card Grid */
              <div className="w-full mb-6">
                {activeQuestion.input_type === 'multi_select' ? (
                  <MultiSelectCard
                    options={activeQuestion.options}
                    selectedValues={selectedMultiCodes}
                    onToggle={(code) => toggleMultiCode(code)}
                    onConfirm={() => submitActiveAnswer(selectedMultiCodes)}
                    disabled={loading}
                  />
                ) : (
                  <SingleSelectCard
                    options={activeQuestion.options}
                    selectedValue={selectedOptionCode}
                    matchedVoiceOption={voiceFeedback}
                    onSelect={(code) => {
                      setSelectedOptionCode(code);
                      submitActiveAnswer([code]);
                    }}
                    disabled={loading}
                  />
                )}
              </div>
            ) : (
              /* 4. Spoken / Button Interactive Choice Fallback */
              <div className="w-full mb-6 flex flex-col items-center gap-4">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 w-full">
                  <button
                    type="button"
                    onClick={() => submitActiveAnswer(['NONE_REPORTED'], 'None / No symptoms')}
                    className="min-h-[85px] p-4 sm:p-5 rounded-2xl bg-white hover:bg-[#f8fafa] text-[#191c1d] border border-[#bdc9c5]/60 hover:border-[#005f53] flex items-center justify-between cursor-pointer transition-all shadow-sm active:scale-98"
                  >
                    <div className="flex items-center gap-3.5">
                      <div className="w-11 h-11 rounded-xl bg-[#eceeee] text-[#005f53] flex items-center justify-center shrink-0">
                        <Negative className="w-6 h-6 text-[#aa0a17]" />
                      </div>
                      <div className="flex flex-col text-left">
                        <span className="text-lg font-bold">
                          {language === 'hi' ? 'कोई समस्या नहीं / कुछ नहीं' : 'None / No prior history'}
                        </span>
                        <span className="text-xs text-[#6e7976]">
                          {language === 'hi' ? 'कोई लक्षण नहीं' : 'No relevant condition'}
                        </span>
                      </div>
                    </div>
                  </button>

                  <button
                    type="button"
                    onClick={() => submitActiveAnswer(['MILD_OCCASIONAL'], 'Mild or occasional symptoms')}
                    className="min-h-[85px] p-4 sm:p-5 rounded-2xl bg-white hover:bg-[#f8fafa] text-[#191c1d] border border-[#bdc9c5]/60 hover:border-[#005f53] flex items-center justify-between cursor-pointer transition-all shadow-sm active:scale-98"
                  >
                    <div className="flex items-center gap-3.5">
                      <div className="w-11 h-11 rounded-xl bg-[#eceeee] text-[#005f53] flex items-center justify-center shrink-0">
                        <Positive className="w-6 h-6 text-[#005f53]" />
                      </div>
                      <div className="flex flex-col text-left">
                        <span className="text-lg font-bold">
                          {language === 'hi' ? 'हाँ / कभी-कभार' : 'Yes / Mild or occasional'}
                        </span>
                        <span className="text-xs text-[#6e7976]">
                          {language === 'hi' ? 'हल्के लक्षण हैं' : 'Experiencing some symptoms'}
                        </span>
                      </div>
                    </div>
                  </button>
                </div>

                {/* Collapsible Keyboard Option if patient specifically desires to type */}
                {showKeyboardInput ? (
                  <div className="w-full flex flex-col gap-2">
                    <div className="relative">
                      <input
                        type="text"
                        autoFocus
                        placeholder={t('intake.type_or_speak', language)}
                        value={freeTextAnswer}
                        onChange={(e) => setFreeTextAnswer(e.target.value)}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter' && freeTextAnswer.trim()) {
                            submitActiveAnswer([], freeTextAnswer.trim());
                          }
                        }}
                        className="w-full h-16 px-6 pr-28 rounded-2xl border-2 border-[#005f53] text-lg bg-white focus:outline-none shadow-sm"
                      />
                      {freeTextAnswer.trim() && (
                        <button
                          type="button"
                          onClick={() => submitActiveAnswer([], freeTextAnswer.trim())}
                          className="absolute right-3 top-3 h-10 px-4 rounded-xl bg-[#005f53] text-white font-bold text-sm flex items-center gap-1 cursor-pointer"
                        >
                          <span>{t('nav.next', language)}</span>
                        </button>
                      )}
                    </div>
                  </div>
                ) : (
                  <button
                    type="button"
                    onClick={() => setShowKeyboardInput(true)}
                    className="text-xs text-[#005f53] hover:underline font-semibold flex items-center gap-1.5 py-1 px-3 rounded-lg hover:bg-[#eceeee]/50 cursor-pointer"
                  >
                    <Keyboard className="w-4 h-4" />
                    <span>{language === 'hi' ? 'कीबोर्ड से विवरण लिखें' : 'Type custom note with keyboard'}</span>
                  </button>
                )}
              </div>
            )}

            {/* Quick Skip / Unsure Buttons */}
            <div className="flex items-center gap-3 mb-4">
              <button
                type="button"
                data-voice-action="skip"
                data-voice-label="Not sure"
                onClick={() => submitActiveAnswer([], null, 'UNKNOWN')}
                className="px-4 py-2 rounded-full bg-[#eceeee] hover:bg-[#e1e3e3] text-[#3e4946] text-xs font-bold transition-all cursor-pointer"
              >
                {t('intake.not_sure', language)}
              </button>
              <button
                type="button"
                data-voice-action="skip"
                data-voice-label="Prefer not to say"
                onClick={() => submitActiveAnswer([], null, 'REFUSED')}
                className="px-4 py-2 rounded-full bg-[#eceeee] hover:bg-[#e1e3e3] text-[#3e4946] text-xs font-bold transition-all cursor-pointer"
              >
                {t('intake.prefer_not_say', language)}
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
        nextDisabled={
          loading ||
          (activeTab === 'ADAPTIVE_QUESTION' &&
            activeQuestion?.input_type === 'single_select' &&
            !selectedOptionCode &&
            !freeTextAnswer.trim()) ||
          (activeTab === 'ADAPTIVE_QUESTION' &&
            activeQuestion?.input_type === 'multi_select' &&
            selectedMultiCodes.length === 0 &&
            !freeTextAnswer.trim())
        }
        nextText={
          loading
            ? t('intake.btn_processing', language)
            : activeTab === 'ADAPTIVE_QUESTION'
            ? t('intake.btn_next_question', language)
            : activeTab === 'PAIN_SCALE'
            ? t('intake.btn_start_inquiry', language)
            : t('intake.btn_next_step', language)
        }
      />
    </div>
  );
}
