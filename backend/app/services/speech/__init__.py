from app.services.speech.speech_service import speech_service, SpeechService
from app.services.speech.base_speech import BaseSpeechAdapter
from app.services.speech.bhashini_adapter import BhashiniSpeechAdapter
from app.services.speech.gemini_audio_adapter import GeminiAudioAdapter
from app.services.speech.mock_speech_adapter import MockSpeechAdapter

__all__ = [
    "speech_service",
    "SpeechService",
    "BaseSpeechAdapter",
    "BhashiniSpeechAdapter",
    "GeminiAudioAdapter",
    "MockSpeechAdapter"
]
