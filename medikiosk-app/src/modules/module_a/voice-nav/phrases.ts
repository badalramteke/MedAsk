/**
 * Voice UI Navigation & Accessibility Plugin — Phrase Mappings
 * Supported Languages: English, Hindi, Marathi, Telugu, Tamil
 */

export interface VoicePhraseEntry {
  action: string;
  param?: string;
}

export const PHRASE_DICTIONARY: Record<string, VoicePhraseEntry> = {
  // Navigation: Next
  "next": { action: "next" },
  "continue": { action: "next" },
  "aage": { action: "next" },
  "आगे": { action: "next" },
  "aage badho": { action: "next" },
  "pudhe": { action: "next" },
  "पुढे": { action: "next" },
  "munduku": { action: "next" },
  "ముందుకు": { action: "next" },
  "aduthu": { action: "next" },
  "அடுத்து": { action: "next" },

  // Navigation: Back / Previous
  "back": { action: "back" },
  "go back": { action: "back" },
  "previous": { action: "back" },
  "peeche": { action: "back" },
  "पीछे": { action: "back" },
  "piche": { action: "back" },
  "maage": { action: "back" },
  "मागे": { action: "back" },
  "venakki": { action: "back" },
  "వెనక్కి": { action: "back" },
  "pinnal": { action: "back" },
  "பின்னால்": { action: "back" },

  // Confirmation
  "confirm": { action: "confirm" },
  "yes": { action: "confirm" },
  "ok": { action: "confirm" },
  "haan": { action: "confirm" },
  "हाँ": { action: "confirm" },
  "theek hai": { action: "confirm" },
  "ho": { action: "confirm" },
  "हो": { action: "confirm" },
  "avunu": { action: "confirm" },
  "అవును": { action: "confirm" },
  "sari": { action: "confirm" },
  "aam": { action: "confirm" },
  "ஆம்": { action: "confirm" },

  // Repeat Audio
  "repeat": { action: "repeat" },
  "say again": { action: "repeat" },
  "dobara": { action: "repeat" },
  "दोबारा": { action: "repeat" },
  "phir se bolo": { action: "repeat" },
  "punha sanga": { action: "repeat" },
  "पुन्हा": { action: "repeat" },
  "malli cheppandi": { action: "repeat" },
  "మళ్లీ": { action: "repeat" },
  "meendum sollungal": { action: "repeat" },
  "மீண்டும்": { action: "repeat" },

  // Read Options
  "options": { action: "read-options" },
  "choices": { action: "read-options" },
  "read options": { action: "read-options" },
  "vikalp": { action: "read-options" },
  "विकल्प": { action: "read-options" },
  "paryay": { action: "read-options" },
  "पर्याय": { action: "read-options" },
  "ennikalu": { action: "read-options" },
  "ఎంపికలు": { action: "read-options" },
  "therivugal": { action: "read-options" },
  "தெரிவுகள்": { action: "read-options" },

  // Help
  "help": { action: "help" },
  "madad": { action: "help" },
  "मदद": { action: "help" },
  "sahayyam": { action: "help" },
  "sahayata": { action: "help" },
  "सहायता": { action: "help" },
  "madat": { action: "help" },
  "मदत": { action: "help" },
  "sahayam": { action: "help" },
  "సహాయం": { action: "help" },
  "udhavi": { action: "help" },
  "உதவி": { action: "help" },

  // Pause / Stop
  "stop": { action: "pause" },
  "pause": { action: "pause" },
  "ruko": { action: "pause" },
  "रुको": { action: "pause" },
  "ruk jao": { action: "pause" },
  "thamba": { action: "pause" },
  "थांबा": { action: "pause" },
  "aagandi": { action: "pause" },
  "ఆగండి": { action: "pause" },
  "nillungal": { action: "pause" },
  "நில்லுங்கள்": { action: "pause" },

  // Cancel
  "cancel": { action: "cancel" },
  "band karo": { action: "cancel" },
  "बंद करो": { action: "cancel" },
  "radd kara": { action: "cancel" },
  "రద్దు": { action: "cancel" },
  "ரத்து": { action: "cancel" },

  // Start Intake
  "start": { action: "start-intake" },
  "begin": { action: "start-intake" },
  "shuru karo": { action: "start-intake" },
  "शुरू करो": { action: "start-intake" },
  "shuru kara": { action: "start-intake" },
  "prārambhinchandi": { action: "start-intake" },
  "thodangavum": { action: "start-intake" },

  // Change Language
  "hindi": { action: "set-language", param: "hi" },
  "hindi mein bolo": { action: "set-language", param: "hi" },
  "english": { action: "set-language", param: "en" },
  "marathi": { action: "set-language", param: "mr" },
  "marathi madhe bola": { action: "set-language", param: "mr" },
  "telugu": { action: "set-language", param: "te" },
  "tamil": { action: "set-language", param: "ta" },
};
