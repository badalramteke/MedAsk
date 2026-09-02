import re
from typing import Optional, Tuple
from app.models.speech import VoiceActionEnum, VOICE_ACTION_KEYWORDS

class VoiceActionMatcher:
    """
    Module E: Semantic Voice UI Action Interpreter.
    Matches spoken patient utterances to allow-listed UI navigation actions across 6 languages.
    """
    @staticmethod
    def match_action(transcript: str, language: str = "hi") -> Tuple[bool, Optional[VoiceActionEnum]]:
        """
        Check if the recognized transcript contains any allow-listed voice command keyword.
        Returns: (is_voice_action, matched_action_enum)
        """
        if not transcript or not transcript.strip():
            return False, None

        cleaned = transcript.strip().lower()
        cleaned_no_punct = re.sub(r"[^\w\s]", "", cleaned)

        # 1. First check the active language dictionary
        for action, lang_dict in VOICE_ACTION_KEYWORDS.items():
            keywords = lang_dict.get(language, [])
            for kw in keywords:
                kw_clean = kw.lower()
                if kw_clean in cleaned or kw_clean in cleaned_no_punct:
                    return True, action

        # 2. Check all other language dictionaries (e.g. English keywords spoken during Hindi intake)
        for action, lang_dict in VOICE_ACTION_KEYWORDS.items():
            for lang_code, keywords in lang_dict.items():
                if lang_code == language:
                    continue
                for kw in keywords:
                    kw_clean = kw.lower()
                    if kw_clean in cleaned or kw_clean in cleaned_no_punct:
                        return True, action

        return False, None

voice_action_matcher = VoiceActionMatcher()
