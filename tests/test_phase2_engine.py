import sys
import os

# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from fastapi.testclient import TestClient
from app.main import app
from app.engine.question_bank import question_bank
from app.engine.flow_controller import flow_controller
from app.engine.answer_validator import answer_validator
from app.engine.red_flag_scanner import red_flag_scanner

client = TestClient(app)


def test_question_bank_loads_questions():
    """Verify QuestionBank loads 29 total questions (SOCRATES + General)."""
    assert len(question_bank._questions) >= 29, "QuestionBank failed to load datasets"
    assert question_bank.has_socrates_domain("chest_pain"), "Chest pain domain missing"
    assert question_bank.has_socrates_domain("headache"), "Headache domain missing"
    print("[PASS] test_question_bank_loads_questions")


def test_question_localization():
    """Verify questions return Hindi/English text properly."""
    q_en = question_bank.localize_question("SOC_CP_001_SITE", "en")
    assert q_en["question_text"] == "Where exactly is your chest pain located?"

    q_hi = question_bank.localize_question("SOC_CP_001_SITE", "hi")
    assert "छाती" in q_hi["question_text"]
    print("[PASS] test_question_localization")


def test_answer_validation():
    """Verify AnswerValidator accepts valid value codes and rejects invalid ones."""
    # Valid
    is_valid, msg = answer_validator.validate_answer("SOC_CP_001_SITE", ["CHEST_LEFT_SUBSTERNAL"])
    assert is_valid is True, f"Validation failed: {msg}"

    # Invalid
    is_valid, msg = answer_validator.validate_answer("SOC_CP_001_SITE", ["INVALID_CODE_123"])
    assert is_valid is False
    assert "Invalid value code" in msg
    print("[PASS] test_answer_validation")


def test_red_flag_scanner():
    """Verify RedFlagScanner fires critical rule on chest pain radiating to left arm."""
    answers = {
        "SOC_CP_001_SITE": ["CHEST_LEFT_SUBSTERNAL"],
        "SOC_CP_004_RADIATION": ["RADIATION_LEFT_ARM_SHOULDER"],
    }
    alerts = red_flag_scanner.scan(answers, "en")
    assert len(alerts) >= 1, "Red flag scanner failed to detect ACS alert"
    assert alerts[0].rule_id == "RF_CARD_001_CHEST_PAIN_RADIATION"
    assert alerts[0].urgency_level == "EMERGENCY_CRITICAL"
    print("[PASS] test_red_flag_scanner")


def test_full_session_api_flow():
    """Integration test for the full API session lifecycle."""
    session_id = "test-session-phase2-001"

    # 1. Create Session
    pdo_payload = {
        "identity": {
            "session_id": session_id,
            "facility_id": "HOSP_AIIMS_DELHI",
            "preferred_language": "en"
        },
        "consent": {
            "scope": "INTAKE_AND_SUMMARY",
            "status": "GRANTED"
        }
    }
    res_create = client.post("/api/v1/sessions/", json=pdo_payload)
    assert res_create.status_code == 201, f"Session creation failed: {res_create.text}"

    # 2. Get First Question
    res_q1 = client.get(f"/api/v1/sessions/{session_id}/next-question")
    assert res_q1.status_code == 200
    assert res_q1.json()["question_id"] == "__CHIEF_COMPLAINT__"

    # 3. Submit Chief Complaint
    res_ans_cc = client.post(
        f"/api/v1/sessions/{session_id}/answer",
        json={"question_id": "__CHIEF_COMPLAINT__", "free_text": "chest pain"}
    )
    assert res_ans_cc.status_code == 200
    next_q = res_ans_cc.json()["next_question"]
    assert next_q["question_id"] == "SOC_CP_001_SITE"

    # 4. Submit Answer & Trigger Red Flag
    client.post(
        f"/api/v1/sessions/{session_id}/answer",
        json={"question_id": "SOC_CP_001_SITE", "selected_value_codes": ["CHEST_LEFT_SUBSTERNAL"]}
    )
    client.post(
        f"/api/v1/sessions/{session_id}/answer",
        json={"question_id": "SOC_CP_002_ONSET", "selected_value_codes": ["SUDDEN_ACUTE"]}
    )
    client.post(
        f"/api/v1/sessions/{session_id}/answer",
        json={"question_id": "SOC_CP_003_CHAR", "selected_value_codes": ["CRUSHING_HEAVY_PRESSURE"]}
    )
    res_rad = client.post(
        f"/api/v1/sessions/{session_id}/answer",
        json={"question_id": "SOC_CP_004_RADIATION", "selected_value_codes": ["RADIATION_LEFT_ARM_SHOULDER"]}
    )

    assert res_rad.status_code == 200
    assert len(res_rad.json()["new_alerts"]) >= 1, "API did not return new red flag alerts"

    # 5. Fetch Session Alerts
    res_alerts = client.get(f"/api/v1/sessions/{session_id}/alerts")
    assert res_alerts.status_code == 200
    assert len(res_alerts.json()) >= 1
    print("[PASS] test_full_session_api_flow")


if __name__ == "__main__":
    print("Running Phase 2 Test Suite...")
    test_question_bank_loads_questions()
    test_question_localization()
    test_answer_validation()
    test_red_flag_scanner()
    test_full_session_api_flow()
    print("\nALL PHASE 2 TESTS PASSED PERFECTLY!")
