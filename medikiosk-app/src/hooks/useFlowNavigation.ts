/**
 * MediKiosk — Navigation Hook
 * Bridges the clinical flow store with Next.js router.
 */

'use client';

import { useRouter } from 'next/navigation';
import { useFlowStore } from '@/stores/useFlowStore';

export function useFlowNavigation() {
  const router = useRouter();
  const {
    currentScreenId,
    currentStageIndex,
    getCurrentStage,
    getCurrentScreen,
    getOverallProgress,
    getNextRoute,
    getPreviousRoute,
    setCurrentScreen,
  } = useFlowStore();

  const goNext = () => {
    const nextRoute = getNextRoute();
    router.push(nextRoute);
  };

  const goBack = () => {
    const prevRoute = getPreviousRoute();
    router.push(prevRoute);
  };

  const goTo = (route: string, screenId: string) => {
    setCurrentScreen(screenId);
    router.push(route);
  };

  return {
    currentScreenId,
    currentStageIndex,
    currentStage: getCurrentStage(),
    currentScreen: getCurrentScreen(),
    progress: getOverallProgress(),
    goNext,
    goBack,
    goTo,
  };
}
