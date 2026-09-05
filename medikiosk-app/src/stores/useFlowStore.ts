/**
 * MediKiosk — Navigation Flow Store (Zustand)
 * Manages clinical progression, active stage, and step history.
 */

import { create } from 'zustand';
import {
  PATIENT_FLOW,
  getAllScreensFlat,
  getStageForScreen,
  type FlowScreen,
  type FlowStage,
} from '@/lib/flowConfig';

export interface FlowState {
  currentStageIndex: number;
  currentScreenId: string;
  screenHistory: string[];

  // Helpers
  getCurrentStage: () => FlowStage;
  getCurrentScreen: () => FlowScreen | undefined;
  getOverallProgress: () => number;

  // Navigation
  setCurrentScreen: (screenId: string) => void;
  getNextRoute: () => string;
  getPreviousRoute: () => string;
  goBack: () => string;
  resetFlow: () => void;
}

export const useFlowStore = create<FlowState>((set, get) => ({
  currentStageIndex: 0,
  currentScreenId: 'welcome_gate',
  screenHistory: ['welcome_gate'],

  getCurrentStage: () => {
    const stage = getStageForScreen(get().currentScreenId);
    return stage || PATIENT_FLOW[0];
  },

  getCurrentScreen: () => {
    const screens = getAllScreensFlat();
    return screens.find((s) => s.id === get().currentScreenId);
  },

  getOverallProgress: () => {
    const allScreens = getAllScreensFlat();
    const idx = allScreens.findIndex((s) => s.id === get().currentScreenId);
    if (idx === -1) return 0;
    return Math.round(((idx + 1) / allScreens.length) * 100);
  },

  setCurrentScreen: (screenId: string) => {
    const stage = getStageForScreen(screenId);
    const stageIdx = stage
      ? PATIENT_FLOW.findIndex((s) => s.key === stage.key)
      : 0;

    set((state) => ({
      currentScreenId: screenId,
      currentStageIndex: stageIdx >= 0 ? stageIdx : state.currentStageIndex,
      screenHistory: state.screenHistory[state.screenHistory.length - 1] === screenId
        ? state.screenHistory
        : [...state.screenHistory, screenId],
    }));
  },

  getNextRoute: () => {
    const allScreens = getAllScreensFlat();
    const idx = allScreens.findIndex((s) => s.id === get().currentScreenId);
    if (idx >= 0 && idx < allScreens.length - 1) {
      return allScreens[idx + 1].route;
    }
    return '/complete';
  },

  getPreviousRoute: () => {
    const { screenHistory } = get();
    if (screenHistory.length > 1) {
      const prevId = screenHistory[screenHistory.length - 2];
      const allScreens = getAllScreensFlat();
      const prevScreen = allScreens.find((s) => s.id === prevId);
      if (prevScreen) return prevScreen.route;
    }
    return '/';
  },

  goBack: () => {
    const { screenHistory } = get();
    if (screenHistory.length > 1) {
      const newHistory = [...screenHistory];
      newHistory.pop();
      const prevId = newHistory[newHistory.length - 1];
      const allScreens = getAllScreensFlat();
      const prevScreen = allScreens.find((s) => s.id === prevId);
      const stage = getStageForScreen(prevId);
      const stageIdx = stage
        ? PATIENT_FLOW.findIndex((s) => s.key === stage.key)
        : 0;

      set({
        screenHistory: newHistory,
        currentScreenId: prevId,
        currentStageIndex: stageIdx >= 0 ? stageIdx : 0,
      });

      return prevScreen?.route || '/';
    }
    return '/';
  },

  resetFlow: () => {
    set({
      currentStageIndex: 0,
      currentScreenId: 'welcome_gate',
      screenHistory: ['welcome_gate'],
    });
  },
}));
