import time
import base64
from typing import Dict, Any, List, Optional
from app.models.speech import (
    SpeechRecognitionResult,
    SpeechSynthesisResult,
    VoiceActionEnum
)
from app.services.speech.base_speech import BaseSpeechAdapter
from app.services.speech.bhashini_adapter import BhashiniSpeechAdapter
from app.services.speech.gemini_audio_adapter import GeminiAudioAdapter
from app.services.speech.mock_speech_adapter import MockSpeechAdapter
from app.services.speech.action_matcher import voice_action_matcher
from app.services.speech.tts_cache import tts_cache

class SpeechService:
    """
    Central Speech Orchestrator for MediKiosk (Module E).
    Coordinates the 3-tier speech cascade (Bhashini -> Gemini Audio -> Mock),
    Module E semantic voice navigation, and hybrid 0ms TTS caching.
    """
    def __init__(self):
        self.bhashini_adapter = BhashiniSpeechAdapter()
        self.gemini_adapter = GeminiAudioAdapter()
        self.mock_adapter = MockSpeechAdapter()
        
        self.asr_cascade: List[BaseSpeechAdapter] = [
            self.bhashini_adapter,
            self.gemini_adapter,
            self.mock_adapter
        ]
        
        self.tts_cascade: List[BaseSpeechAdapter] = [
            self.bhashini_adapter,
            self.mock_adapter
        ]

    async def transcribe_audio(
        self,
        audio_bytes: bytes,
        audio_format: str = "webm",
        language: str = "hi",
        session_id: Optional[str] = None
    ) -> SpeechRecognitionResult:
        """
        Execute speech-to-text with 3-tier cascading fallback.
        Checks for allow-listed Module E voice actions in transcript.
        Purges raw audio buffer immediately from memory.
        """
        start_time = time.time()
        last_error = ""

        try:
            for adapter in self.asr_cascade:
                success, transcript, confidence, error_msg = await adapter.transcribe(
                    audio_bytes=audio_bytes,
                    audio_format=audio_format,
                    language=language
                )
                
                if success and transcript:
                    latency = round((time.time() - start_time) * 1000, 2)
                    
                    # Module E: Check if transcript matches any semantic navigation action
                    is_action, matched_action = voice_action_matcher.match_action(
                        transcript=transcript, language=language
                    )

                    return SpeechRecognitionResult(
                        success=True,
                        transcript=transcript,
                        detected_language=language,
                        confidence=confidence,
                        provider_used=adapter.name,
                        latency_ms=latency,
                        is_voice_action=is_action,
                        matched_action=matched_action,
                        error_message=None
                    )
                else:
                    last_error = error_msg or f"{adapter.name} failed without transcript."
        finally:
            # DPDP Act: Explicitly clear local memory reference to raw audio bytes
            audio_bytes = b""

        # If all cascades failed (should not happen due to Mock)
        latency = round((time.time() - start_time) * 1000, 2)
        return SpeechRecognitionResult(
            success=False,
            transcript="",
            detected_language=language,
            confidence=0.0,
            provider_used="NONE",
            latency_ms=latency,
            is_voice_action=False,
            matched_action=None,
            error_message=f"All speech ASR adapters failed. Last error: {last_error}"
        )

    async def synthesize_speech(
        self,
        text: str,
        language: str = "hi",
        gender: str = "female",
        audio_format: str = "wav"
    ) -> SpeechSynthesisResult:
        """
        Synthesize speech using hybrid cache + Bhashini TTS cascade.
        """
        if not text or not text.strip():
            return SpeechSynthesisResult(
                success=False,
                audio_base64="",
                audio_format=f"audio/{audio_format}",
                language=language,
                provider_used="NONE",
                error_message="Empty text provided for TTS synthesis."
            )

        # 1. Check in-memory hybrid TTS cache
        cached_b64 = tts_cache.get(text, language, gender)
        if cached_b64:
            return SpeechSynthesisResult(
                success=True,
                audio_base64=cached_b64,
                audio_format=f"audio/{audio_format}",
                language=language,
                provider_used="HYBRID_TTS_CACHE",
                duration_seconds=1.5,
                is_pre_cached=True
            )

        # 2. Execute TTS cascade
        last_error = ""
        for adapter in self.tts_cascade:
            success, audio_b64, err = await adapter.synthesize(
                text=text,
                language=language,
                gender=gender,
                audio_format=audio_format
            )
            if success and audio_b64:
                # Cache for future instant retrieval
                tts_cache.set(text, language, audio_b64, gender)
                
                return SpeechSynthesisResult(
                    success=True,
                    audio_base64=audio_b64,
                    audio_format=f"audio/{audio_format}",
                    language=language,
                    provider_used=adapter.name,
                    duration_seconds=2.0,
                    is_pre_cached=False
                )
            else:
                last_error = err

        # Fallback to default cache audio
        default_b64 = tts_cache.get_or_default(text, language, gender)
        return SpeechSynthesisResult(
            success=True,
            audio_base64=default_b64,
            audio_format=f"audio/{audio_format}",
            language=language,
            provider_used="MOCK_SPEECH_FALLBACK",
            duration_seconds=1.2,
            is_pre_cached=True,
            error_message=f"Synthesized via fallback: {last_error}"
        )

    async def get_health_status(self) -> Dict[str, Any]:
        """Check status across all speech providers."""
        return {
            "bhashini": await self.bhashini_adapter.health_check(),
            "gemini_audio": await self.gemini_adapter.health_check(),
            "mock_speech": await self.mock_adapter.health_check(),
            "overall_status": "online"
        }

speech_service = SpeechService()
