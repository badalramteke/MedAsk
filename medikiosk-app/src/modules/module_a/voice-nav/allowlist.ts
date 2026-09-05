/**
 * Voice UI Navigation & Accessibility Plugin — Action Allow-List
 * Adheres strictly to VOICE_UI_NAV_PLUGIN.md.
 * Prohibits raw DOM queries, arbitrary script execution, or dynamic URLs.
 */

export interface VoiceActionConfig {
  requiresConfirm: boolean;
  scope: 'global' | 'entry-screen' | 'document-screen' | 'question-screen';
  hasParam?: boolean;
}

export const VOICE_ACTION_ALLOWLIST: Record<string, VoiceActionConfig> = {
  'next':           { requiresConfirm: false, scope: 'global' },
  'back':           { requiresConfirm: false, scope: 'global' },
  'confirm':        { requiresConfirm: false, scope: 'global' },
  'repeat':         { requiresConfirm: false, scope: 'global' },
  'read-options':   { requiresConfirm: false, scope: 'global' },
  'help':           { requiresConfirm: false, scope: 'global' },
  'pause':          { requiresConfirm: true,  scope: 'global' },
  'cancel':         { requiresConfirm: true,  scope: 'global' },
  'start-intake':   { requiresConfirm: false, scope: 'entry-screen' },
  'scan-doc':       { requiresConfirm: true,  scope: 'document-screen' },
  'set-language':   { requiresConfirm: false, scope: 'global', hasParam: true },
};
