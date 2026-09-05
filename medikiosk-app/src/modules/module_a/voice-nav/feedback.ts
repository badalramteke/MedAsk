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

export function playAudioFeedback(type: 'matched' | 'failed'): void {
  try {
    const audioCtx = new (window.AudioContext || (window as any).webkitAudioContext)();
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();

    osc.connect(gain);
    gain.connect(audioCtx.destination);

    if (type === 'matched') {
      osc.frequency.setValueAtTime(587.33, audioCtx.currentTime); // D5
      osc.frequency.exponentialRampToValueAtTime(880, audioCtx.currentTime + 0.12); // A5
      gain.gain.setValueAtTime(0.08, audioCtx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.15);
      osc.start();
      osc.stop(audioCtx.currentTime + 0.15);
    } else {
      osc.frequency.setValueAtTime(329.63, audioCtx.currentTime); // E4
      osc.frequency.exponentialRampToValueAtTime(220, audioCtx.currentTime + 0.15); // A3
      gain.gain.setValueAtTime(0.08, audioCtx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.18);
      osc.start();
      osc.stop(audioCtx.currentTime + 0.18);
    }
  } catch {
    // AudioContext blocked or unsupported
  }
}
