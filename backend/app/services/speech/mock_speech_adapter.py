import base64
import struct
import math
from typing import Dict, Any, Tuple
from app.services.speech.base_speech import BaseSpeechAdapter

def generate_synthetic_wav_bytes(duration_seconds: float = 1.0, sample_rate: int = 16000) -> bytes:
    """Generate a standard valid binary 16-bit mono PCM WAV file in memory."""
    num_samples = int(sample_rate * duration_seconds)
    # Generate silent PCM audio (zero amplitude, no beep sound)
    audio_data = bytearray(num_samples * 2)

    data_size = len(audio_data)
    total_file_size = data_size + 36

    header = struct.pack(
        "<4sI4s4sIHHIIHH4sI",
        b"RIFF",
        total_file_size,
        b"WAVE",
        b"fmt ",
        16,       # Subchunk1Size for PCM
        1,        # AudioFormat (1 = PCM)
        1,        # NumChannels (1 = Mono)
        sample_rate,
        sample_rate * 2,  # ByteRate
        2,        # BlockAlign
        16,       # BitsPerSample
        b"data",
        data_size
    )

    return header + audio_data


class MockSpeechAdapter(BaseSpeechAdapter):
    """
    Deterministic offline mock adapter for ASR and TTS.
    Generates standard binary WAV audio and simulated multi-lingual transcripts.
    """
    def __init__(self):
        super().__init__(name="MOCK_SPEECH")
        self._mock_wav_bytes = generate_synthetic_wav_bytes(duration_seconds=1.5)
        self._mock_wav_b64 = base64.b64encode(self._mock_wav_bytes).decode("utf-8")

    async def transcribe(
        self, audio_bytes: bytes, audio_format: str = "webm", language: str = "hi"
    ) -> Tuple[bool, str, float, str]:
        """Return a simulated multi-lingual transcript based on language."""
        sample_transcripts = {
            "en": "I have severe chest pain radiating to left arm for two hours.",
            "hi": "मुझे दो घंटे से सीने में तेज दर्द है और यह बाएं हाथ तक जा रहा है।",
            "mr": "मला दोन तासांपासून छातीत तीव्र दुखत आहे आणि ते डाव्या हाताकडे पसरत आहे.",
            "bn": "আমার দুই ঘণ্টা ধরে বুকে তীব্র ব্যথা হচ্ছে এবং তা বাঁ হাতে ছড়িয়ে পড়ছে।",
            "ta": "எனக்கு இரண்டு மணி நேரமாக கடுமையான நெஞ்சு வலி உள்ளது, அது இடது கைக்கு பரவுகிறது.",
            "te": "నాకు రెండు గంటలుగా తీవ్రమైన ఛాతీ నొప్పి ఉంది మరియు అది ఎడమ చేయికి వ్యాపిస్తోంది."
        }
        transcript = sample_transcripts.get(language, sample_transcripts["hi"])
        return True, transcript, 0.95, ""

    async def synthesize(
        self, text: str, language: str = "hi", gender: str = "female", audio_format: str = "wav"
    ) -> Tuple[bool, str, str]:
        """Return synthetic valid WAV audio."""
        return True, self._mock_wav_b64, ""

    async def health_check(self) -> Dict[str, Any]:
        """Mock speech engine is always online and deterministic."""
        return {
            "status": "online",
            "provider": "MOCK_SPEECH",
            "offline_ready": True
        }
