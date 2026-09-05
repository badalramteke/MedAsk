/**
 * Voice UI Navigation & Accessibility Plugin — Action Dispatcher
 * Locates allow-listed DOM targets, triggers focus visual feedback,
 * and executes click event without duplicate code paths.
 */

import { VoicePhraseEntry } from './phrases';
import { updateAriaVoiceStatus } from './feedback';

export function dispatchVoiceAction(entry: VoicePhraseEntry, root: Document | HTMLElement = document): boolean {
  const { action, param } = entry;

  // Build target query
  let selector = `[data-voice-action="${action}"]`;
  if (param) {
    selector = `[data-voice-action="${action}"][data-voice-param="${param}"]`;
  }

  const targetEl = root.querySelector(selector) as HTMLElement | null;

  if (!targetEl) {
    console.warn(`[VoiceNav] Target element not found in DOM for action: ${action}`);
    return false;
  }

  // Check disabled state
  if (targetEl.getAttribute('data-voice-disabled') === 'true' || (targetEl as HTMLButtonElement).disabled) {
    console.warn(`[VoiceNav] Action '${action}' is currently disabled.`);
    return false;
  }

  // Visual focus and activation feedback (outline + scale)
  targetEl.focus();
  targetEl.classList.add('voice-activated');

  const voiceLabel = targetEl.getAttribute('data-voice-label') || targetEl.innerText || action;
  updateAriaVoiceStatus(`Voice command recognized: ${voiceLabel}`);

  // Trigger existing touch/click handler
  targetEl.click();

  setTimeout(() => {
    targetEl.classList.remove('voice-activated');
  }, 350);

  return true;
}
