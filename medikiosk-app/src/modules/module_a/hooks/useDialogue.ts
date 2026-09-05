/**
 * Hook: useDialogue
 * Manages clinical dialogue state, question progression,
 * touch answer submission, and emergency alert state.
 */

'use client';

import { useState, useCallback } from 'react';
import { moduleAClient, AnswerSubmissionResult, StartSessionParams } from '../api/moduleAClient';

export function useDialogue() {
  const [sessionId, setSessionId] = useState<string>('');
  const [currentSection, setCurrentSection] = useState<string>('greeting');
  const [currentQuestion, setCurrentQuestion] = useState<string>('');
  const [currentQuestionEnglish, setCurrentQuestionEnglish] = useState<string>('');
  const [currentOptions, setCurrentOptions] = useState<string[]>([]);
  const [language, setLanguage] = useState<string>('hi');
  const [isAyushMode, setIsAyushMode] = useState<boolean>(false);
  const [answeredCount, setAnsweredCount] = useState<number>(0);
  const [totalRequired, setTotalRequired] = useState<number>(10);
  const [progress, setProgress] = useState<number>(0);
  const [isComplete, setIsComplete] = useState<boolean>(false);
  const [redFlagAlert, setRedFlagAlert] = useState<any | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const initSession = useCallback(async (params: StartSessionParams = {}) => {
    setIsLoading(true);
    try {
      const res = await moduleAClient.startSession(params);
      setSessionId(res.session_id);
      setLanguage(res.language);
      setIsAyushMode(res.is_ayush_mode);
      setCurrentSection(res.current_section);
      setCurrentQuestion(res.greeting_text);
      setCurrentOptions(res.options || []);
      setTotalRequired(res.is_ayush_mode ? 14 : 10);
      setProgress(5);
    } catch (err) {
      console.error('Session initiation error:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const submitAnswer = useCallback(async (answerText: string, optionCode?: string, source: 'touch' | 'voice' = 'touch') => {
    if (!sessionId) return;
    setIsLoading(true);

    try {
      const res: AnswerSubmissionResult = await moduleAClient.submitAnswer(sessionId, answerText, optionCode, source);
      if (res.red_flag_triggered && res.red_flag_alert) {
        setRedFlagAlert(res.red_flag_alert);
      }

      if (res.next_question) setCurrentQuestion(res.next_question);
      if (res.next_question_english) setCurrentQuestionEnglish(res.next_question_english);
      if (res.next_options) setCurrentOptions(res.next_options);
      setCurrentSection(res.current_section);
      setAnsweredCount(res.answered_count);
      setTotalRequired(res.total_required);
      setProgress(res.progress_percentage);
      setIsComplete(res.is_complete);
    } catch (err) {
      console.error('Answer submission error:', err);
    } finally {
      setIsLoading(false);
    }
  }, [sessionId]);

  const changeLanguage = useCallback(async (newLang: string) => {
    setLanguage(newLang);
    if (!sessionId) return;

    try {
      const res = await moduleAClient.switchLanguage(sessionId, newLang);
      if (res.updated_question) setCurrentQuestion(res.updated_question);
    } catch (err) {
      console.error('Language switch error:', err);
    }
  }, [sessionId]);

  const dismissRedFlag = useCallback(() => {
    setRedFlagAlert(null);
  }, []);

  return {
    sessionId,
    currentSection,
    currentQuestion,
    currentQuestionEnglish,
    currentOptions,
    language,
    isAyushMode,
    answeredCount,
    totalRequired,
    progress,
    isComplete,
    redFlagAlert,
    isLoading,
    initSession,
    submitAnswer,
    changeLanguage,
    setRedFlagAlert,
    dismissRedFlag,
    setCurrentQuestion,
    setCurrentOptions,
    setProgress,
  };
}
