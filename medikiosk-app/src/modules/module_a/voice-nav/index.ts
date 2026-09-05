/**
 * Voice UI Navigation & Accessibility Plugin
 * Export initialization helper and definitions.
 */

import { VoiceNavPlugin } from './VoiceNavPlugin';

export * from './allowlist';
export * from './phrases';
export * from './matcher';
export * from './dispatcher';
export * from './feedback';
export { VoiceNavPlugin };

export function initVoiceNav(
  container: HTMLElement | null,
  onStateChange?: (state: string) => void
): () => void {
  const plugin = new VoiceNavPlugin(container, onStateChange);
  return () => plugin.stop();
}
