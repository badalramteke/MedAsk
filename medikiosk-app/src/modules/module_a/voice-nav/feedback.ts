/**
 * Voice UI Navigation & Accessibility Plugin — Feedback & ARIA Live Regions
 */

export function updateAriaVoiceStatus(message: string): void {
  let statusEl = document.getElementById('voice-status');
  if (!statusEl) {
    statusEl = document.createElement('div');
    statusEl.id = 'voice-status';
    statusEl.setAttribute('aria-live', 'polite');
    statusEl.setAttribute('aria-atomic', 'true');
    statusEl.className = 'sr-only';
    document.body.appendChild(statusEl);
  }

  statusEl.textContent = message;
}

export function playAudioFeedback(_type: 'matched' | 'failed'): void {
  // Beep sound muted per user requirement
}
