/**
 * Voice UI Navigation & Accessibility Plugin — Fuzzy Matcher
 * Normalizes voice transcript and performs Levenshtein distance (<= 2) matching.
 */

import { PHRASE_DICTIONARY, VoicePhraseEntry } from './phrases';
import { VOICE_ACTION_ALLOWLIST } from './allowlist';

export function normalizePhrase(text: string): string {
  return text
    .toLowerCase()
    .replace(/[.,\/#!$%\^&\*;:{}=\-_`~()?'"|।]/g, '')
    .replace(/\s+/g, ' ')
    .trim();
}

export function levenshteinDistance(a: string, b: string): number {
  const m = a.length;
  const n = b.length;
  const dp: number[][] = [];

  for (let i = 0; i <= m; i++) {
    dp[i] = [i];
  }
  for (let j = 0; j <= n; j++) {
    dp[0][j] = j;
  }

  for (let i = 1; i <= m; i++) {
    for (let j = 1; j <= n; j++) {
      const cost = a[i - 1] === b[j - 1] ? 0 : 1;
      dp[i][j] = Math.min(
        dp[i - 1][j] + 1,      // deletion
        dp[i][j - 1] + 1,      // insertion
        dp[i - 1][j - 1] + cost // substitution
      );
    }
  }

  return dp[m][n];
}

export function matchVoiceCommand(rawTranscript: string): VoicePhraseEntry | null {
  const normalized = normalizePhrase(rawTranscript);
  if (!normalized) return null;

  // 1. Direct dictionary match
  if (PHRASE_DICTIONARY[normalized]) {
    const entry = PHRASE_DICTIONARY[normalized];
    if (VOICE_ACTION_ALLOWLIST[entry.action]) {
      return entry;
    }
  }

  // 2. Fuzzy match against dictionary keys (Levenshtein distance <= 2)
  let bestMatch: VoicePhraseEntry | null = null;
  let minDistance = 999;

  for (const [phrase, entry] of Object.entries(PHRASE_DICTIONARY)) {
    // Only test if length is reasonably close
    if (Math.abs(phrase.length - normalized.length) <= 2) {
      const dist = levenshteinDistance(normalized, phrase);
      if (dist <= 2 && dist < minDistance) {
        minDistance = dist;
        bestMatch = entry;
      }
    }
  }

  if (bestMatch && VOICE_ACTION_ALLOWLIST[bestMatch.action]) {
    return bestMatch;
  }

  return null;
}
