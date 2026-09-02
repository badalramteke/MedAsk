from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Literal
from enum import Enum

class VoiceActionEnum(str, Enum):
    NAV_NEXT = "NAV_NEXT"
    NAV_PREVIOUS = "NAV_PREVIOUS"
    NAV_REPEAT = "NAV_REPEAT"
    NAV_HOME = "NAV_HOME"
    NAV_HELP = "NAV_HELP"
    
    LANG_HINDI = "LANG_HINDI"
    LANG_ENGLISH = "LANG_ENGLISH"
    LANG_MARATHI = "LANG_MARATHI"
    LANG_BENGALI = "LANG_BENGALI"
    LANG_TAMIL = "LANG_TAMIL"
    LANG_TELUGU = "LANG_TELUGU"
    
    CONFIRM_AGREE = "CONFIRM_AGREE"
    CONFIRM_DECLINE = "CONFIRM_DECLINE"
    
    SELECT_OPTION_1 = "SELECT_OPTION_1"
    SELECT_OPTION_2 = "SELECT_OPTION_2"
    SELECT_OPTION_3 = "SELECT_OPTION_3"
    SELECT_OPTION_4 = "SELECT_OPTION_4"
    
    EMERGENCY_HELP = "EMERGENCY_HELP"
    CALL_STAFF = "CALL_STAFF"


# Multilingual allow-listed semantic keywords mapped to actions (Module E)
VOICE_ACTION_KEYWORDS: Dict[VoiceActionEnum, Dict[str, List[str]]] = {
    VoiceActionEnum.NAV_NEXT: {
        "en": ["next", "continue", "proceed", "go forward"],
        "hi": ["आगे", "अगला", "आगे बढ़ें", "आगे चलो"],
        "mr": ["पुढे", "पुढील", "पुढे चला"],
        "bn": ["পরবর্তী", "সামনে", "পরেরটা"],
        "ta": ["அடுத்து", "முன்னேறு"],
        "te": ["తరువాత", "ముందుకు"],
    },
    VoiceActionEnum.NAV_PREVIOUS: {
        "en": ["back", "previous", "go back"],
        "hi": ["पीछे", "पिछला", "वापस"],
        "mr": ["मागे", "मागील", "परत"],
        "bn": ["পূর্ববর্তী", "পেছনে", "আগেরটা"],
        "ta": ["பின்னால்", "முந்தைய"],
        "te": ["వెనుక", "మునుపటి"],
    },
    VoiceActionEnum.NAV_REPEAT: {
        "en": ["repeat", "say again", "repeat question", "listen again"],
        "hi": ["दोबारा", "फिर से", "दोबारा सुनाएं", "फिर से बोलें"],
        "mr": ["पुन्हा सांगा", "पुन्हा", "परत बोला"],
        "bn": ["আবার বলুন", "আবার", "পুনরাবৃত্তি"],
        "ta": ["மீண்டும் சொல்", "மறுபடி சொல்"],
        "te": ["మళ్ళీ చెప్పు", "మరలా చెప్పు"],
    },
    VoiceActionEnum.LANG_HINDI: {
        "en": ["hindi", "change to hindi", "hindi language"],
        "hi": ["हिंदी", "हिन्दी भाषा", "हिंदी चुनो"],
        "mr": ["हिंदी"],
        "bn": ["হিন্দি"],
        "ta": ["இந்தி"],
        "te": ["హిందీ"],
    },
    VoiceActionEnum.LANG_ENGLISH: {
        "en": ["english", "change to english", "english language"],
        "hi": ["अंग्रेजी", "इंग्लिश"],
        "mr": ["इंग्रजी", "इंग्लिश"],
        "bn": ["ইংরেজি", "ইংলিশ"],
        "ta": ["ஆங்கிலம்", "இங்கிலீஷ்"],
        "te": ["ఇంగ్లీష్", "ఆంగ్లం"],
    },
    VoiceActionEnum.LANG_MARATHI: {
        "en": ["marathi", "marathi language"],
        "hi": ["मराठी"],
        "mr": ["मराठी", "मराठी भाषा"],
        "bn": ["মারাঠি"],
        "ta": ["மராத்தி"],
        "te": ["మరాఠీ"],
    },
    VoiceActionEnum.LANG_BENGALI: {
        "en": ["bengali", "bangla", "bengali language"],
        "hi": ["बंगाली", "बांग्ला"],
        "mr": ["बंगाली"],
        "bn": ["বাংলা", "বাংলা भाषा"],
        "ta": ["வங்காளம்"],
        "te": ["బెంగాలీ"],
    },
    VoiceActionEnum.LANG_TAMIL: {
        "en": ["tamil", "tamil language"],
        "hi": ["तमिल", "तमिळ"],
        "mr": ["तमिळ"],
        "bn": ["তামিল"],
        "ta": ["தமிழ்", "தமிழ் மொழி"],
        "te": ["తమిళం"],
    },
    VoiceActionEnum.LANG_TELUGU: {
        "en": ["telugu", "telugu language"],
        "hi": ["तेलुगु"],
        "mr": ["तेलगू"],
        "bn": ["তেলেগু"],
        "ta": ["தெலுங்கு"],
        "te": ["తెలుగు", "తెలుగు భాష"],
    },
    VoiceActionEnum.CONFIRM_AGREE: {
        "en": ["agree", "i agree", "yes", "confirm", "accept"],
        "hi": ["सहमत हैं", "हाँ", "स्वीकार", "मंजूर है", "सहमति"],
        "mr": ["सहमत", "होय", "मान्य आहे"],
        "bn": ["একমত", "হ্যাঁ", "সম্মত"],
        "ta": ["ஒப்புக்கொள்கிறேன்", "ஆம்", "சரி"],
        "te": ["అంగీకరిస్తున్నాను", "అవును", "సరే"],
    },
    VoiceActionEnum.CONFIRM_DECLINE: {
        "en": ["decline", "i decline", "no", "reject", "cancel"],
        "hi": ["अस्वीकार", "नहीं", "मना", "रद्द"],
        "mr": ["अमान्य", "नाही", "रद्द"],
        "bn": ["প্রত্যাখ্যান", "না", "বাতিল"],
        "ta": ["நிராகரி", "இல்லை"],
        "te": ["తిరస్కరించు", "వద్దు", "కాదు"],
    },
    VoiceActionEnum.SELECT_OPTION_1: {
        "en": ["option one", "option 1", "first option", "number one"],
        "hi": ["पहला विकल्प", "विकल्प एक", "नंबर एक", "पहला"],
        "mr": ["पहिला पर्याय", "पर्याय एक"],
        "bn": ["প্রথম বিকল্প", "বিকল্প এক"],
        "ta": ["முதல் விருப்பம்", "விருப்பம் ஒன்று"],
        "te": ["మొదటి ఎంపిక", "ఎంపిక ఒకటి"],
    },
    VoiceActionEnum.SELECT_OPTION_2: {
        "en": ["option two", "option 2", "second option", "number two"],
        "hi": ["दूसरा विकल्प", "विकल्प दो", "नंबर दो", "दूसरा"],
        "mr": ["दुसरा पर्याय", "पर्याय दोन"],
        "bn": ["দ্বিতীয় বিকল্প", "বিকল্প দুই"],
        "ta": ["இரண்டாவது விருப்பம்", "விருப்பம் இரண்டு"],
        "te": ["రెండవ ఎంపిక", "ఎంపిక రెండు"],
    },
    VoiceActionEnum.SELECT_OPTION_3: {
        "en": ["option three", "option 3", "third option", "number three"],
        "hi": ["तीसरा विकल्प", "विकल्प तीन", "नंबर तीन", "तीसरा"],
        "mr": ["तिसरा पर्याय", "पर्याय तीन"],
        "bn": ["তৃতীয় বিকল্প", "বিকল্প তিন"],
        "ta": ["மூன்றாவது விருப்பம்", "விருப்பம் மூன்று"],
        "te": ["మూడవ ఎంపిక", "ఎంపిక మూడు"],
    },
    VoiceActionEnum.SELECT_OPTION_4: {
        "en": ["option four", "option 4", "fourth option", "number four"],
        "hi": ["चौथा विकल्प", "विकल्प चार", "नंबर चार", "चौथा"],
        "mr": ["चौथा पर्याय", "पर्याय चार"],
        "bn": ["চতুর্থ विकल्प", "বিকল্প চার"],
        "ta": ["நான்காவது விருப்பம்", "விருப்பம் நான்கு"],
        "te": ["నాల్గవ ఎంపిక", "ఎంపిక నాలుగు"],
    },
    VoiceActionEnum.EMERGENCY_HELP: {
        "en": ["help", "emergency", "doctor", "i need help", "call nurse", "sos"],
        "hi": ["मदद", "मदद चाहिए", "आपातकाल", "डॉक्टर को बुलाओ", "नर्स", "बचाओ"],
        "mr": ["मदत", "तातडीची मदत", "डॉक्टरला बोलवा"],
        "bn": ["সাহায্য", "জরুরী", "ডাক্তার ডাকুন"],
        "ta": ["உதவி", "அவசரம்", "மருத்துவரை கூப்பிடு"],
        "te": ["సహాయం", "అత్యవసరం", "డాక్టర్ని పిలవండి"],
    },
}


class SpeechRecognitionRequest(BaseModel):
    """Payload for speech transcription."""
    audio_base64: Optional[str] = Field(None, description="Base64 encoded audio string")
    audio_format: Literal["wav", "webm", "mp3", "ogg"] = Field(default="webm")
    language: str = Field(default="hi", description="ISO 639-1 language code (en, hi, mr, bn, ta, te)")
    session_id: Optional[str] = Field(None, description="Optional associated intake session ID")


class SpeechRecognitionResult(BaseModel):
    """Output contract for speech recognition."""
    success: bool
    transcript: str = Field(..., description="Recognized vernacular text")
    detected_language: str = Field(default="hi")
    confidence: float = Field(default=0.90, ge=0.0, le=1.0)
    provider_used: str = Field(..., description="BHASHINI_ULCA | GEMINI_AUDIO | MOCK_SPEECH")
    latency_ms: float = Field(default=0.0)
    is_voice_action: bool = Field(default=False, description="Whether the transcript matched an allow-listed Module E UI action")
    matched_action: Optional[VoiceActionEnum] = Field(None, description="Matched semantic action ID")
    error_message: Optional[str] = None


class SpeechSynthesisRequest(BaseModel):
    """Payload for Text-to-Speech synthesis."""
    text: str = Field(..., description="Vernacular text to synthesize into spoken audio")
    language: str = Field(default="hi", description="Language code e.g. hi, en, mr, bn, ta, te")
    gender: Literal["female", "male"] = Field(default="female")
    audio_format: Literal["wav", "mp3"] = Field(default="wav")


class SpeechSynthesisResult(BaseModel):
    """Output contract for synthesized audio."""
    success: bool
    audio_base64: str = Field(..., description="Base64 encoded audio bytes")
    audio_format: str = Field(default="audio/wav")
    language: str
    provider_used: str
    duration_seconds: Optional[float] = None
    is_pre_cached: bool = Field(default=False, description="Whether served from static 0ms cache")
    error_message: Optional[str] = None
