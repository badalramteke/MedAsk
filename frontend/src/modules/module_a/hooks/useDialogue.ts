'use client';

import { useState, useCallback } from 'react';
import {
  moduleAClient,
  QuestionItem,
  RedFlagAlert,
  HpiStructuredSummary,
} from '../api/moduleAClient';

export function useDialogue() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [currentQuestion, setCurrentQuestion] = useState<QuestionItem | null>(null);
  const [phase, setPhase] = useState<string>('greeting');
  const [progressPercent, setProgressPercent] = useState<number>(0);
  const [mode, setMode] = useState<'allopathic' | 'ayush' | 'both'>('allopathic');
  const [language, setLanguage] = useState<string>('en');
  const [activeAlert, setActiveAlert] = useState<RedFlagAlert | null>(null);
  const [summary, setSummary] = useState<HpiStructuredSummary | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  /**
   * Initializes a new session with Module A
   */
  const initSession = useCallback(
    async (params: {
      patientId?: string;
      language?: string;
      chiefComplaint?: string;
      mode?: 'allopathic' | 'ayush' | 'both';
    }) => {
      setIsLoading(true);
      setErrorMessage(null);
      try {
        const res = await moduleAClient.startSession(params);
        setSessionId(res.session_id);
        setCurrentQuestion(res.first_question);
        setPhase(res.current_phase);
        setMode(res.mode as any);
        setLanguage(res.language);
        setProgressPercent(res.current_phase === 'chief_complaint' ? 10 : 20);
        return res;
      } catch (err: any) {
        setErrorMessage(err.message || 'Failed to start intake session');
        throw err;
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  /**
   * Submits an answer via REST
   */
  const submitAnswer = useCallback(
    async (params: {
      answerText?: string;
      optionId?: string;
      optionIds?: string[];
      audioB64?: string;
    }) => {
      if (!sessionId) return null;
      setIsLoading(true);
      setErrorMessage(null);
      try {
        const res = await moduleAClient.submitAnswer(sessionId, params);
        if (res.red_flag_detected && res.red_flag_alert) {
          setActiveAlert(res.red_flag_alert);
        }
        if (res.next_question) {
          setCurrentQuestion(res.next_question);
        }
        setPhase(res.phase);
        setProgressPercent(res.progress_percent);
        return res;
      } catch (err: any) {
        setErrorMessage(err.message || 'Failed to submit response');
        throw err;
      } finally {
        setIsLoading(false);
      }
    },
    [sessionId]
  );

  /**
   * Switches clinical mode
   */
  const changeMode = useCallback(
    async (newMode: 'allopathic' | 'ayush' | 'both') => {
      if (!sessionId) return;
      try {
        await moduleAClient.switchMode(sessionId, newMode);
        setMode(newMode);
      } catch (err: any) {
        console.error('Mode switch failed:', err);
      }
    },
    [sessionId]
  );

  /**
   * Completes intake session and fetches final summary
   */
  const finishSession = useCallback(async () => {
    if (!sessionId) return null;
    setIsLoading(true);
    try {
      const sum = await moduleAClient.completeSession(sessionId);
      setSummary(sum);
      setPhase('complete');
      setProgressPercent(100);
      return sum;
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to generate summary');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [sessionId]);

  return {
    sessionId,
    currentQuestion,
    setCurrentQuestion,
    phase,
    setPhase,
    progressPercent,
    setProgressPercent,
    mode,
    language,
    setLanguage,
    activeAlert,
    setActiveAlert,
    summary,
    isLoading,
    errorMessage,
    initSession,
    submitAnswer,
    changeMode,
    finishSession,
  };
}
