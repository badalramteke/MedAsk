/**
 * MediKiosk — Inactivity & Session Lifecycle Hook
 * Monitors user interaction and triggers warning / auto-purge
 * according to DPDP Act 2023 session retention rules.
 */

'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import { useSessionStore } from '@/stores/useSessionStore';
import { SESSION_TIMEOUT_MS, SESSION_WARNING_MS } from '@/lib/constants';

export function useInactivityTimer(onTimeout?: () => void) {
  const { sessionId, resetSession } = useSessionStore();
  const [showWarning, setShowWarning] = useState(false);
  const [countdown, setCountdown] = useState(30);

  const warningTimerRef = useRef<NodeJS.Timeout | null>(null);
  const expiryTimerRef = useRef<NodeJS.Timeout | null>(null);
  const countdownIntervalRef = useRef<NodeJS.Timeout | null>(null);

  const resetTimer = useCallback(() => {
    setShowWarning(false);
    setCountdown(30);

    if (warningTimerRef.current) clearTimeout(warningTimerRef.current);
    if (expiryTimerRef.current) clearTimeout(expiryTimerRef.current);
    if (countdownIntervalRef.current) clearInterval(countdownIntervalRef.current);

    if (!sessionId) return;

    // Warning before timeout
    warningTimerRef.current = setTimeout(() => {
      setShowWarning(true);
      countdownIntervalRef.current = setInterval(() => {
        setCountdown((prev) => {
          if (prev <= 1) {
            clearInterval(countdownIntervalRef.current!);
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    }, SESSION_WARNING_MS);

    // Hard timeout & session termination
    expiryTimerRef.current = setTimeout(() => {
      setShowWarning(false);
      resetSession();
      if (onTimeout) onTimeout();
    }, SESSION_TIMEOUT_MS);
  }, [sessionId, resetSession, onTimeout]);

  useEffect(() => {
    if (!sessionId) return;

    const events = ['mousedown', 'mousemove', 'touchstart', 'keydown', 'scroll'];
    const handleActivity = () => {
      if (!showWarning) {
        resetTimer();
      }
    };

    events.forEach((event) => {
      window.addEventListener(event, handleActivity, { passive: true });
    });

    resetTimer();

    return () => {
      events.forEach((event) => {
        window.removeEventListener(event, handleActivity);
      });
      if (warningTimerRef.current) clearTimeout(warningTimerRef.current);
      if (expiryTimerRef.current) clearTimeout(expiryTimerRef.current);
      if (countdownIntervalRef.current) clearInterval(countdownIntervalRef.current);
    };
  }, [sessionId, showWarning, resetTimer]);

  const extendSession = () => {
    setShowWarning(false);
    resetTimer();
  };

  return {
    showWarning,
    countdown,
    extendSession,
  };
}
