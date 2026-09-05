/**
 * Voice UI Navigation & Accessibility Plugin — Core Manager
 * Continuously listens for allow-listed navigation intents and handles keyboard accessibility.
 */

import { matchVoiceCommand } from './matcher';
import { dispatchVoiceAction } from './dispatcher';
import { playAudioFeedback, updateAriaVoiceStatus } from './feedback';

export class VoiceNavPlugin {
  private recognition: any = null;
  private isRunning: boolean = false;
  private container: HTMLElement | null = null;
  private onStateChange?: (state: string) => void;

  constructor(container: HTMLElement | null, onStateChange?: (state: string) => void) {
    this.container = container;
    this.onStateChange = onStateChange;
    this.initKeyboardListeners();
    this.initSpeechRecognition();
  }

  private initSpeechRecognition() {
    if (typeof window === 'undefined') return;

    const SpeechRecognition =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

    if (!SpeechRecognition) {
      console.warn('[VoiceNav] Web Speech API not supported in this browser.');
      return;
    }

    try {
      this.recognition = new SpeechRecognition();
      this.recognition.continuous = true;
      this.recognition.interimResults = false;
      this.recognition.maxAlternatives = 1;

      this.recognition.onresult = (event: any) => {
        const last = event.results.length - 1;
        const transcript = event.results[last][0].transcript.trim();

        if (transcript) {
          this.handleTranscript(transcript);
        }
      };

      this.recognition.onerror = (event: any) => {
        if (event.error !== 'no-speech') {
          console.debug('[VoiceNav] Speech recognition notice:', event.error);
        }
      };

      this.recognition.onend = () => {
        // Auto-restart if still designated active
        if (this.isRunning) {
          try {
            this.recognition.start();
          } catch {
            // Ignore if already started
          }
        }
      };

      this.start();
    } catch (e) {
      console.warn('[VoiceNav] Could not initialize Web Speech:', e);
    }
  }

  private handleTranscript(transcript: string) {
    const match = matchVoiceCommand(transcript);

    if (match) {
      const dispatched = dispatchVoiceAction(match, this.container || document);
      if (dispatched) {
        playAudioFeedback('matched');
        if (this.onStateChange) this.onStateChange('command-matched');
        setTimeout(() => {
          if (this.onStateChange) this.onStateChange('listening');
        }, 500);
      } else {
        playAudioFeedback('failed');
      }
    }
  }

  private initKeyboardListeners() {
    if (typeof window === 'undefined') return;

    const handleKeyDown = (e: KeyboardEvent) => {
      // Alt + R -> Repeat current question
      if (e.altKey && (e.key === 'r' || e.key === 'R')) {
        e.preventDefault();
        dispatchVoiceAction({ action: 'repeat' }, this.container || document);
      }
      // Alt + H -> Help
      if (e.altKey && (e.key === 'h' || e.key === 'H')) {
        e.preventDefault();
        dispatchVoiceAction({ action: 'help' }, this.container || document);
      }
      // Escape -> Pause session
      if (e.key === 'Escape') {
        e.preventDefault();
        dispatchVoiceAction({ action: 'pause' }, this.container || document);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    (this as any)._keyCleanup = () => window.removeEventListener('keydown', handleKeyDown);
  }

  public start() {
    if (this.recognition && !this.isRunning) {
      try {
        this.isRunning = true;
        this.recognition.start();
        updateAriaVoiceStatus('Voice navigation active. Speak commands like Next, Repeat, or Help.');
      } catch {
        // Already started
      }
    }
  }

  public stop() {
    this.isRunning = false;
    if (this.recognition) {
      try {
        this.recognition.stop();
      } catch {
        // Already stopped
      }
    }
    if ((this as any)._keyCleanup) {
      (this as any)._keyCleanup();
    }
  }
}
