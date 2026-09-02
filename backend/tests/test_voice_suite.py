import pytest
import base64
import io
from fastapi.testclient import TestClient
from app.main import app
from app.services.speech.mock_speech_adapter import generate_synthetic_wav_bytes
from app.services.speech.action_matcher import voice_action_matcher
from app.models.speech import VoiceActionEnum

client = TestClient(app)

def create_test_pdo(session_id: str, gender: str = "FEMALE", age: int = 52, lang: str = "hi") -> dict:
    return {
        "version": "1.0.0",
        "identity": {
            "session_id": session_id,
            "facility_id": "AIIA_NEW_DELHI_01",
            "preferred_language": lang,
            "gender": gender,
            "age": age,
            "external_identifier": None,
            "patient_reference": None
        },
        "consent": {
            "scope": "INTAKE_AND_SUMMARY",
            "status": "GRANTED",
            "evidence_reference": "TEST_AUDIT_REF_001"
        },
        "documents": {},
        "summary": {},
        "alerts": {},
        "integration_status": {},
        "plugin_outputs": {}
    }

@pytest.fixture
def sample_wav_bytes() -> bytes:
    """Fixture providing valid 16kHz 16-bit mono PCM WAV bytes."""
    return generate_synthetic_wav_bytes(duration_seconds=1.0)


def test_speech_transcribe_base64_json(sample_wav_bytes):
    """Test /api/v1/voice/transcribe with Base64 JSON payload across languages."""
    b64_str = base64.b64encode(sample_wav_bytes).decode("utf-8")
    
    # Test Hindi
    payload_hi = {
        "audio_base64": b64_str,
        "audio_format": "wav",
        "language": "hi"
    }
    res = client.post("/api/v1/voice/transcribe", json=payload_hi)
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["success"] is True
    assert "सीने में तेज दर्द" in data["transcript"] or len(data["transcript"]) > 0
    assert data["detected_language"] == "hi"
    assert data["confidence"] > 0.8
    assert data["provider_used"] in ("BHASHINI_ULCA", "GEMINI_AUDIO", "MOCK_SPEECH")


def test_speech_transcribe_multipart_upload(sample_wav_bytes):
    """Test /api/v1/voice/transcribe with multipart/form-data upload."""
    audio_file = io.BytesIO(sample_wav_bytes)
    files = {"file": ("test_recording.wav", audio_file, "audio/wav")}
    data = {"language": "mr", "audio_format": "wav"}

    res = client.post("/api/v1/voice/transcribe", files=files, data=data)
    assert res.status_code == 200, res.text
    resp_data = res.json()
    assert resp_data["success"] is True
    assert resp_data["detected_language"] == "mr"
    assert len(resp_data["transcript"]) > 0


def test_speech_synthesis_tts():
    """Test /api/v1/voice/synthesize returning valid base64 audio."""
    payload = {
        "text": "आपको दर्द कब से हो रहा है?",
        "language": "hi",
        "gender": "female",
        "audio_format": "wav"
    }
    res = client.post("/api/v1/voice/synthesize", json=payload)
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["success"] is True
    assert len(data["audio_base64"]) > 50
    assert data["audio_format"] == "audio/wav"
    assert data["language"] == "hi"

    # Decode and verify WAV RIFF header
    audio_bytes = base64.b64decode(data["audio_base64"])
    assert audio_bytes[:4] == b"RIFF"
    assert audio_bytes[8:12] == b"WAVE"


def test_hybrid_tts_caching():
    """Test that repeated TTS requests return from in-memory cache."""
    text = "कृपया अपने लक्षण बताएं।"
    payload = {
        "text": text,
        "language": "hi",
        "gender": "female",
        "audio_format": "wav"
    }
    # First call
    res1 = client.post("/api/v1/voice/synthesize", json=payload)
    assert res1.status_code == 200
    # Second call should hit hybrid cache
    res2 = client.post("/api/v1/voice/synthesize", json=payload)
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["success"] is True
    assert data2["is_pre_cached"] is True
    assert data2["provider_used"] == "HYBRID_TTS_CACHE"


def test_module_e_voice_action_matcher():
    """Test Module E semantic keyword matching across 6 Indian languages."""
    # Hindi Navigation
    is_action, action = voice_action_matcher.match_action("आगे बढ़ें", language="hi")
    assert is_action is True
    assert action == VoiceActionEnum.NAV_NEXT

    # English Previous
    is_action, action = voice_action_matcher.match_action("go back please", language="en")
    assert is_action is True
    assert action == VoiceActionEnum.NAV_PREVIOUS

    # Tamil Repeat
    is_action, action = voice_action_matcher.match_action("மீண்டும் சொல்", language="ta")
    assert is_action is True
    assert action == VoiceActionEnum.NAV_REPEAT

    # Language change
    is_action, action = voice_action_matcher.match_action("हिंदी भाषा", language="en")
    assert is_action is True
    assert action == VoiceActionEnum.LANG_HINDI

    # Consent Confirmation
    is_action, action = voice_action_matcher.match_action("सहमत हैं", language="hi")
    assert is_action is True
    assert action == VoiceActionEnum.CONFIRM_AGREE

    # Emergency Assistance
    is_action, action = voice_action_matcher.match_action("मदद चाहिए डॉक्टर", language="hi")
    assert is_action is True
    assert action == VoiceActionEnum.EMERGENCY_HELP

    # Non-action clinical fact
    is_action, action = voice_action_matcher.match_action("2 days mild fever and dry cough", language="en")
    assert is_action is False
    assert action is None


def test_voice_actions_catalog_endpoint():
    """Test GET /api/v1/voice/actions returns full catalog."""
    res = client.get("/api/v1/voice/actions")
    assert res.status_code == 200
    data = res.json()
    assert data["total_actions"] >= 15
    assert "en" in data["supported_languages"]
    assert "hi" in data["supported_languages"]
    assert "NAV_NEXT" in data["actions"]
    assert "EMERGENCY_HELP" in data["actions"]


def test_voice_health_endpoint():
    """Test GET /api/v1/voice/health reports provider diagnostics."""
    res = client.get("/api/v1/voice/health")
    assert res.status_code == 200
    data = res.json()
    assert "bhashini" in data
    assert "gemini_audio" in data
    assert "mock_speech" in data
    assert data["overall_status"] == "online"


def test_unified_voice_answer_flow(sample_wav_bytes):
    """Test POST /api/v1/sessions/{id}/voice/answer advancing intake and returning next question audio."""
    session_id = "test_voice_flow_session_001"
    sess_res = client.post("/api/v1/sessions/", json=create_test_pdo(session_id, gender="FEMALE", lang="hi"))
    assert sess_res.status_code == 201

    # Submit spoken chief complaint ("सीने में तेज दर्द है")
    b64_audio = base64.b64encode(sample_wav_bytes).decode("utf-8")
    payload = {
        "audio_base64": b64_audio,
        "audio_format": "wav",
        "language": "hi"
    }

    voice_res = client.post(f"/api/v1/sessions/{session_id}/voice/answer", json=payload)
    assert voice_res.status_code == 200, voice_res.text
    data = voice_res.json()
    assert data["success"] is True
    assert data["is_voice_action"] is False
    assert "सीने में तेज दर्द" in data["transcript"] or len(data["transcript"]) > 0
    assert data["next_question"] is not None
    # Verify synthesized audio for next question
    assert data["next_question_audio_base64"] is not None
    audio_bytes = base64.b64decode(data["next_question_audio_base64"])
    assert audio_bytes[:4] == b"RIFF"


def test_voice_answer_semantic_navigation_command(sample_wav_bytes):
    """Test speaking a navigation command to /voice/answer returns action event."""
    session_id = "test_voice_nav_session_002"
    sess_res = client.post("/api/v1/sessions/", json=create_test_pdo(session_id, lang="hi"))
    assert sess_res.status_code == 201

    # Mock SpeechService transcribe_audio to return an allow-listed action
    from unittest.mock import patch
    from app.models.speech import SpeechRecognitionResult

    mock_res = SpeechRecognitionResult(
        success=True,
        transcript="आगे बढ़ें",
        detected_language="hi",
        confidence=0.98,
        provider_used="MOCK_SPEECH",
        is_voice_action=True,
        matched_action=VoiceActionEnum.NAV_NEXT
    )

    with patch("app.services.speech.speech_service.SpeechService.transcribe_audio", return_value=mock_res):
        b64_audio = base64.b64encode(sample_wav_bytes).decode("utf-8")
        res = client.post(f"/api/v1/sessions/{session_id}/voice/answer", json={"audio_base64": b64_audio})
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert data["is_voice_action"] is True
        assert data["matched_action"] == "NAV_NEXT"


def test_spoken_red_flag_alert_trigger(sample_wav_bytes):
    """Test speaking critical emergency symptoms immediately flags nursing triage."""
    session_id = "test_voice_rf_session_003"
    sess_res = client.post("/api/v1/sessions/", json=create_test_pdo(session_id, gender="MALE", lang="hi"))
    assert sess_res.status_code == 201

    b64_audio = base64.b64encode(sample_wav_bytes).decode("utf-8")
    voice_res = client.post(f"/api/v1/sessions/{session_id}/voice/answer", json={
        "audio_base64": b64_audio,
        "language": "hi"
    })
    assert voice_res.status_code == 200
    
    # Check triage alerts endpoint
    alerts_res = client.get(f"/api/v1/sessions/{session_id}/alerts")
    assert alerts_res.status_code == 200
    alerts = alerts_res.json()["alerts"]
    assert len(alerts) >= 1
    assert alerts[0]["severity"] in ("CRITICAL", "HIGH")
