"""
RedFlagScanner: Loads red_flags_rules.json and evaluates
PatientDataObject state after every answer for deterministic red-flag matches.
Does NOT diagnose. Only flags for triage staff.
"""
import json
import os
from typing import List, Dict, Any
from datetime import datetime
from app.models.interview import RedFlagAlert

_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "clinical")


class RedFlagScanner:
    def __init__(self, data_dir: str = _DATA_DIR):
        self._rules: List[dict] = []
        self._load(data_dir)

    def _load(self, data_dir: str):
        path = os.path.join(data_dir, "red_flags_rules.json")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._rules = data.get("rules", [])

    def scan(self, answer_history: Dict[str, Any], language: str = "en") -> List[RedFlagAlert]:
        """
        Evaluate all red flag rules against the accumulated answer history.
        Uses structured_fact_pattern matching from the JSON rules.
        Returns a list of triggered RedFlagAlerts.
        """
        triggered = []

        # Flatten all answered value codes into a set for pattern matching
        all_value_codes = set()
        for val in answer_history.values():
            if isinstance(val, list):
                all_value_codes.update(val)
            elif isinstance(val, str):
                all_value_codes.add(val)

        # 1. Check structured value codes across accumulated answers
        for rule in self._rules:
            trigger = rule.get("trigger", {})
            pattern = trigger.get("structured_fact_pattern", {})
            keywords_by_lang = rule.get("trigger_keywords_by_lang", {})

            matched = self._matches_pattern(pattern, all_value_codes, answer_history)

            # 2. Check multilingual spoken keyword phrases within individual patient narratives
            # (Strictly excludes family history, relative context, or past history)
            if not matched and keywords_by_lang:
                for qid, val in answer_history.items():
                    narrative = str(val).strip().lower() if isinstance(val, (str, int, float)) else ""
                    if not narrative or self._is_family_or_relative_context(qid, narrative):
                        continue

                    for lang_code, kw_list in keywords_by_lang.items():
                        for kw in kw_list:
                            if self._matches_keyword(kw, narrative):
                                matched = True
                                break
                        if matched:
                            break
                    if matched:
                        break

            if matched:
                alert_messages = rule.get("alert_message", {})
                alert_msg = alert_messages.get(language, alert_messages.get("en", "Red flag triggered."))

                triggered.append(RedFlagAlert(
                    rule_id=rule["rule_id"],
                    category=rule.get("category", "unknown"),
                    urgency_level=rule.get("urgency_level", "URGENT_PRIORITY"),
                    alert_message=alert_msg,
                    action_code=rule.get("action_code", "TRIAGE_NOTIFY"),
                    triggered_at=datetime.utcnow(),
                    evidence_summary=f"Matched red-flag trigger in answers: {rule['rule_id']}",
                ))

        return triggered

    def _matches_pattern(
        self, pattern: dict, all_codes: set, answer_history: Dict[str, Any]
    ) -> bool:
        """Check if accumulated answers match a rule's structured_fact_pattern."""
        if not pattern:
            return False

        # Check symptom_present
        if pattern.get("symptom_present") and not all_codes:
            return False

        # Check radiation_includes_any / radiation_include_any
        radiation_codes = pattern.get("radiation_includes_any") or pattern.get("radiation_include_any", [])
        if radiation_codes:
            if any(code in all_codes for code in radiation_codes):
                return True

        # Check associated_symptoms_includes_any / associated_symptoms_include_any
        assoc_codes = pattern.get("associated_symptoms_includes_any") or pattern.get("associated_symptoms_include_any", [])
        if assoc_codes:
            if any(code in all_codes for code in assoc_codes):
                return True

        # Check severity_includes_any / severity_include_any
        severity_codes = pattern.get("severity_includes_any") or pattern.get("severity_include_any", [])
        if severity_codes:
            if any(code in all_codes for code in severity_codes):
                return True

        # Check character_includes_any / character_include_any
        char_codes = pattern.get("character_includes_any") or pattern.get("character_include_any", [])
        if char_codes:
            if any(code in all_codes for code in char_codes):
                return True

        return False

    def _get_pattern_codes(self, pattern: dict) -> set:
        """Extract all value codes referenced in a pattern for evidence."""
        codes = set()
        for key in [
            "radiation_includes_any", "radiation_include_any",
            "associated_symptoms_includes_any", "associated_symptoms_include_any",
            "severity_includes_any", "severity_include_any",
            "character_includes_any", "character_include_any"
        ]:
            codes.update(pattern.get(key, []))
        return codes


    def _is_family_or_relative_context(self, qid: str, text: str) -> bool:
        """
        Check if a question ID or answer narrative is about family/relative history.
        Family illnesses must not trigger acute patient presenting red flags.
        """
        qid_lower = qid.lower()
        if "fh" in qid_lower or "family" in qid_lower or "relative" in qid_lower:
            return True

        text_lower = text.lower()
        relative_markers = [
            "he ", "he's", "he was", "he has", "his ", "him ",
            "she ", "she's", "she was", "she has", "her ",
            "father", "mother", "dad", "mom", "brother", "sister",
            "grandfather", "grandmother", "grandpa", "grandma",
            "uncle", "aunt", "cousin", "family", "parent", "parents", "relative",
            "पिता", "माता", "भाई", "बहन", "दादा", "दादी", "नाना", "नानी", "परिवार", "उनको", "उन्हें",
            "वडील", "आई", "भाऊ", "बहीण", "बाबा", "মা", "পরিবার",
            "தந்தை", "தாய்", "குடும்பம்", "తండ్రి", "తల్లి", "కుటుంబం"
        ]
        return any(marker in text_lower for marker in relative_markers)

    def _matches_keyword(self, kw: str, narrative: str) -> bool:
        """
        Check if a clinical red-flag keyword phrase matches within a single patient narrative.
        Requires the actual phrase or all key medical terms of the trigger to be present.
        """
        kw_clean = kw.strip().lower()
        if not kw_clean:
            return False

        # 1. Direct phrase match (e.g. 'chest pain left arm')
        if kw_clean in narrative:
            return True

        # 2. Term co-occurrence in the same narrative sentence/answer
        terms = [t.strip().lower() for t in kw_clean.split() if len(t.strip()) > 1]
        if len(terms) >= 2:
            return all(term in narrative for term in terms)
        elif len(terms) == 1:
            return terms[0] in narrative
        return False

# Singleton
red_flag_scanner = RedFlagScanner()
