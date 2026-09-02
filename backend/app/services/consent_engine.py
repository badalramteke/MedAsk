from datetime import datetime
from typing import Optional, Dict, Any
from fastapi import status
from app.models.consent import (
    ConsentContext,
    ConsentScopeEnum,
    ConsentStatusEnum,
    ScopeConsentDetail,
)
from app.middleware.error_handler import MediKioskException


# Localized Audio Guidance Scripts for Kiosk Voice Consent (6 Languages)
CONSENT_AUDIO_SCRIPTS: Dict[str, Dict[str, str]] = {
    "en": {
        "INTAKE": "To begin your consultation intake, we will ask you questions about your health and symptoms. Do you agree to proceed?",
        "DOCUMENTS": "Please scan or upload your past prescriptions and lab reports so the doctor can review them. Do you give consent to digitize these documents?",
        "SUMMARY": "We will generate a draft summary of your answers for the doctor to review and edit. Do you agree to create this clinical summary?",
        "HIS_SHARE": "Your reviewed clinical summary and documents will be shared with the hospital's electronic health record and linked to your ABHA profile. Do you consent to share this record with your care team?"
    },
    "hi": {
        "INTAKE": "आपके परामर्श की शुरुआत के लिए, हम आपके स्वास्थ्य और लक्षणों के बारे में प्रश्न पूछेंगे। क्या आप आगे बढ़ने के लिए सहमत हैं?",
        "DOCUMENTS": "कृपया अपने पिछले नुस्खे और लैब रिपोर्ट स्कैन करें ताकि डॉक्टर उनकी समीक्षा कर सकें। क्या आप इन दस्तावेजों को डिजिटाइज़ करने की सहमति देते हैं?",
        "SUMMARY": "डॉक्टर के संपादन और समीक्षा के लिए आपके उत्तरों का एक सारांश तैयार किया जाएगा। क्या आप इस सारांश को बनाने के लिए सहमत हैं?",
        "HIS_SHARE": "आपकी स्वीकृत स्वास्थ्य रिपोर्ट अस्पताल के ईएचआर और आपके आभा (ABHA) खाते से साझा की जाएगी। क्या आप इसे अपने डॉक्टर और अस्पताल से साझा करने की सहमति देते हैं?"
    },
    "mr": {
        "INTAKE": "तुमच्या आरोग्य तपासणीसाठी, आम्ही तुम्हाला काही प्रश्न विचारू. आपण पुढे जाण्यास सहमत आहात का?",
        "DOCUMENTS": "कृपया तुमच्या जुन्या प्रिस्क्रिप्शन आणि लॅब रिपोर्ट स्कॅन करा. या कागदपत्रांचे डिजिटायझेशन करण्यास आपली संमती आहे का?",
        "SUMMARY": "डॉक्टरांच्या तपासणीसाठी तुमच्या उत्तरांचा एक सारांश तयार केला जाईल. आपण यास सहमत आहात का?",
        "HIS_SHARE": "तुमची आरोग्य माहिती रुग्णालयाच्या प्रणालीशी आणि तुमच्या आभा (ABHA) खात्याशी जोडली जाईल. आपण यास संमती देता का?"
    },
    "bn": {
        "INTAKE": "আপনার স্বাস্থ্য পরীক্ষার জন্য, আমরা কিছু প্রশ্ন করব। আপনি কি এগিয়ে যেতে সম্মত?",
        "DOCUMENTS": "ডাক্তারের পর্যালোচনার জন্য অনুগ্রহ করে আপনার প্রেসক্রিপশন এবং রিপোর্ট স্কॅन করুন। আপনি কি সম্মতি দিচ্ছেন?",
        "SUMMARY": "ডাক্তারের পর্যালোচনার জন্য একটি সারসংক্ষেপ তৈরি করা হবে। আপনি কি সম্মত?",
        "HIS_SHARE": "আপনার স্বাস্থ্য তথ্য হাসপাতালের রেকর্ড এবং আভা (ABHA) প্রোফাইলের সাথে শেয়ার করা হবে। আপনি কি সম্মতি দিচ্ছেন?"
    },
    "ta": {
        "INTAKE": "உங்கள் மருத்துவ ஆலோசனைக்காக, உங்கள் உடல்நலம் குறித்த கேள்விகளைக் கேட்போம். தொடர ஒப்புக்கொள்கிறீர்களா?",
        "DOCUMENTS": "மருத்துவர் சரிபார்க்க உங்கள் பழைய மருந்துச் சீட்டுகளை ஸ்கேன் செய்யவும். இதற்கு ஒப்புதல் அளிக்கிறீர்களா?",
        "SUMMARY": "மருத்துவரின் பார்வைக்காக உங்கள் பதில்களின் சுருக்கம் உருவாக்கப்படும். ஒப்புக்கொள்கிறீர்களா?",
        "HIS_SHARE": "உங்கள் மருத்துவ அறிக்கை மருத்துவமனை அமைப்பிற்கும் உங்கள் ஆபா (ABHA) கணக்கிற்கும் பகிரப்படும். ஒப்புதல் அளிக்கிறீர்களா?"
    },
    "te": {
        "INTAKE": "మీ ఆరోగ్య వివరాల కోసం మేము కొన్ని ప్రశ్నలు అడుగుతాము. మీరు కొనసాగడానికి అంగీకరిస్తున్నారా?",
        "DOCUMENTS": "డాక్టర్ సమీక్ష కోసం మీ పాత ప్రిస్క్రిప్షన్లు మరియు రిపోర్టులను స్కాన్ చేయండి. అనుమతిస్తారా?",
        "SUMMARY": "డాక్టర్ పరిశీలన కోసం సారాంశం తయారు చేయబడుతుంది. మీరు అంగీకరిస్తున్నారా?",
        "HIS_SHARE": "మీ ఆరోగ్య నివేదిక ఆసుపత్రి వ్యవస్థకు మరియు మీ ఆభా (ABHA) ఖాతాకు భాగస్వామ్యం చేయబడుతుంది. అనుమతిస్తున్నారా?"
    }
}


class ConsentEngine:
    """
    Core Consent Engine managing granular, multi-scope affirmative consent,
    enforcement gates, revocation lifecycle, and multilingual audio guidance.
    """

    def check_consent(self, session: Any, scope: str) -> bool:
        """Check whether a specific consent scope is currently GRANTED."""
        if not session or not getattr(session, "consent", None):
            return False
        return session.consent.is_scope_granted(scope)

    def enforce_consent(self, session: Any, scope: str, message: Optional[str] = None):
        """Raise HTTP 403 CONSENT_REQUIRED if requested scope is not granted."""
        if not self.check_consent(session, scope):
            norm_scope = scope.upper()
            raise MediKioskException(
                error_code="CONSENT_REQUIRED",
                message=message or f"Consent for scope '{norm_scope}' has not been granted for this session.",
                status_code=status.HTTP_403_FORBIDDEN,
                retry_guidance=f"Obtain explicit affirmative consent for '{norm_scope}' before proceeding."
            )

    def grant_scope(
        self,
        session: Any,
        scope: str,
        interaction_mode: str = "TOUCH_SCREEN",
        evidence_reference: Optional[str] = None,
        language: str = "en"
    ) -> ConsentContext:
        """Grant a specific consent scope with audit trail."""
        norm_scope = scope.upper()
        now = datetime.utcnow()
        ev_ref = evidence_reference or f"AUDIT_{interaction_mode}_{session.identity.session_id[:8]}_{norm_scope}"

        # Initialize or update granular scope
        session.consent.scopes[norm_scope] = ScopeConsentDetail(
            scope=norm_scope,
            status=ConsentStatusEnum.GRANTED.value,
            granted_at=now,
            revoked_at=None,
            interaction_mode=interaction_mode,
            evidence_reference=ev_ref
        )

        # Sync top-level status
        session.consent.status = "GRANTED"
        session.consent.granted_at = now
        session.consent.evidence_reference = ev_ref

        # Update composite scope representation if applicable
        all_granted = all(
            session.consent.scopes.get(s, ScopeConsentDetail(scope=s)).status == "GRANTED"
            for s in [ConsentScopeEnum.INTAKE.value, ConsentScopeEnum.DOCUMENTS.value, ConsentScopeEnum.SUMMARY.value, ConsentScopeEnum.HIS_SHARE.value]
        )
        if all_granted:
            session.consent.scope = "FULL_HIS_SHARE"
        elif norm_scope == "DOCUMENTS":
            session.consent.scope = "DOCUMENTS_PROCESSING"
        elif norm_scope in ("INTAKE", "SUMMARY"):
            session.consent.scope = "INTAKE_AND_SUMMARY"
        else:
            session.consent.scope = norm_scope

        return session.consent

    def revoke_scope(
        self,
        session: Any,
        scope: str,
        reason: Optional[str] = None
    ) -> ConsentContext:
        """Revoke a specific consent scope."""
        norm_scope = scope.upper()
        now = datetime.utcnow()

        target_scopes = []
        if norm_scope in ("FULL_HIS_SHARE", "ALL"):
            target_scopes = [ConsentScopeEnum.INTAKE.value, ConsentScopeEnum.DOCUMENTS.value, ConsentScopeEnum.SUMMARY.value, ConsentScopeEnum.HIS_SHARE.value]
        elif norm_scope in ("INTAKE_AND_SUMMARY",):
            target_scopes = [ConsentScopeEnum.INTAKE.value, ConsentScopeEnum.SUMMARY.value]
        elif norm_scope in ("DOCUMENTS_PROCESSING", "DOCUMENTS"):
            target_scopes = [ConsentScopeEnum.DOCUMENTS.value]
        elif norm_scope in ("INTAKE_ONLY", "INTAKE"):
            target_scopes = [ConsentScopeEnum.INTAKE.value]
        else:
            target_scopes = [norm_scope]

        for s in target_scopes:
            if s in session.consent.scopes:
                session.consent.scopes[s].status = ConsentStatusEnum.REVOKED.value
                session.consent.scopes[s].revoked_at = now

        session.consent.status = "REVOKED"
        return session.consent

    def get_audio_consent_script(self, scope: str, language: str = "en") -> str:
        """Retrieve localized consent audio guidance script for kiosk TTS."""
        lang_dict = CONSENT_AUDIO_SCRIPTS.get(language.lower(), CONSENT_AUDIO_SCRIPTS["en"])
        norm_scope = scope.upper()
        # Handle composite scope names gracefully
        if norm_scope in ("FULL_HIS_SHARE", "HIS_SHARE"):
            return lang_dict.get("HIS_SHARE", "")
        if norm_scope in ("DOCUMENTS_PROCESSING", "DOCUMENTS"):
            return lang_dict.get("DOCUMENTS", "")
        if norm_scope in ("INTAKE_AND_SUMMARY", "SUMMARY"):
            return lang_dict.get("SUMMARY", "")
        if norm_scope in ("INTAKE_ONLY", "INTAKE"):
            return lang_dict.get("INTAKE", "")
        return lang_dict.get(norm_scope, lang_dict.get("INTAKE", ""))


consent_engine = ConsentEngine()
