"""
Red Flag Node: Wraps the existing Phase 2 RedFlagScanner for non-blocking alert emission.
Per RED_FLAG_RULES.md: "Rules use approved versioned configuration, not free-form LLM judgment alone."
Per CLINICAL_SAFETY.md: "Red-flag detection creates a staff alert without interrupting the interview.
Triage staff decide the clinical response."
"""
from typing import Dict, Any, List
from app.engine.red_flag_scanner import red_flag_scanner


def red_flag_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    LangGraph node: Evaluates all 13 deterministic red-flag rules against
    accumulated answers. Emits alerts WITHOUT blocking graph progression.
    
    Per CLINICAL_SAFETY.md:
    - The interview continues regardless of alerts.
    - Alerts are sent to triage staff, not the patient.
    - Red-flag rules are deterministic, not LLM-based.
    """
    answered = state.get("answered_questions", {})
    language = state.get("preferred_language", "en")
    existing_flags = state.get("active_red_flags", [])

    # Run the deterministic scanner
    new_alerts = red_flag_scanner.scan(answered, language)

    # Deduplicate by rule_id (don't re-fire already-fired rules)
    existing_rule_ids = {flag.get("rule_id") for flag in existing_flags}
    
    new_flag_dicts = []
    for alert in new_alerts:
        if alert.rule_id not in existing_rule_ids:
            new_flag_dicts.append({
                "rule_id": alert.rule_id,
                "category": alert.category,
                "urgency_level": alert.urgency_level,
                "alert_message": alert.alert_message,
                "action_code": alert.action_code,
                "triggered_at": alert.triggered_at.isoformat(),
                "evidence_summary": alert.evidence_summary,
                "acknowledged": False,
            })

    # Merge with existing flags (append new ones)
    all_flags = existing_flags + new_flag_dicts

    return {
        "active_red_flags": all_flags,
    }
