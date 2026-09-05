/**
 * MediKiosk — Voice & Speech Store (Zustand)
 * Manages audio recording state, visualizer level, speech synthesis, and voice navigation.
 */

import { create } from 'zustand';

export interface VoiceState {
  isListening: boolean;
  isSpeaking: boolean;
  isProcessing: boolean;
  audioLevel: number; // 0.0 to 1.0 for waveform animations
  transcript: string;
  interimTranscript: string;
  lastVoiceAction: string | null;
  errorMessage: string | null;

  // Actions
  setListening: (listening: boolean) => void;
  setSpeaking: (speaking: boolean) => void;
  setProcessing: (processing: boolean) => void;
  setAudioLevel: (level: number) => void;
  setTranscript: (text: string) => void;
  setInterimTranscript: (text: string) => void;
  setVoiceAction: (action: string | null) => void;
  setError: (msg: string | null) => void;
  clearTranscript: () => void;
  resetVoice: () => void;
}

export const useVoiceStore = create<VoiceState>((set) => ({
  isListening: false,
  isSpeaking: false,
  isProcessing: false,
  audioLevel: 0,
  transcript: '',
  interimTranscript: '',
  lastVoiceAction: null,
  errorMessage: null,

  setListening: (isListening) => set({ isListening }),
  setSpeaking: (isSpeaking) => set({ isSpeaking }),
  setProcessing: (isProcessing) => set({ isProcessing }),
  setAudioLevel: (audioLevel) => set({ audioLevel }),
  setTranscript: (transcript) => set({ transcript }),
  setInterimTranscript: (interimTranscript) => set({ interimTranscript }),
  setVoiceAction: (lastVoiceAction) => set({ lastVoiceAction }),
  setError: (errorMessage) => set({ errorMessage }),
  clearTranscript: () => set({ transcript: '', interimTranscript: '' }),
  resetVoice: () =>
    set({
      isListening: false,
      isSpeaking: false,
      isProcessing: false,
      audioLevel: 0,
      transcript: '',
      interimTranscript: '',
      lastVoiceAction: null,
      errorMessage: null,
    }),
}));
