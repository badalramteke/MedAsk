import logging
from typing import Dict, Any, Tuple
from app.services.ocr.base_ocr import BaseOCRAdapter
from app.services.ocr.image_preprocessor import image_preprocessor

logger = logging.getLogger("tesseract_adapter")


class TesseractOCRAdapter(BaseOCRAdapter):
    """
    OCR adapter using Tesseract (pytesseract) for printed document text extraction.
    Supports multilingual extraction: eng + hin (English + Hindi/Devanagari).
    Returns per-character confidence scores for handwriting quality gate.
    """

    def __init__(self):
        super().__init__(name="TESSERACT")
        self._available = False
        try:
            import pytesseract
            self._available = True
        except ImportError:
            logger.warning("pytesseract not installed. Tesseract OCR unavailable.")

    async def extract_text(
        self, image_bytes: bytes, mime_type: str = "image/jpeg"
    ) -> Tuple[bool, str, float, str]:
        """
        Extract text from a document image using Tesseract OCR.
        Returns: (success, extracted_text, mean_confidence, error_message)
        """
        if not self._available:
            return False, "", 0.0, "pytesseract not installed."

        try:
            import pytesseract
            from PIL import Image
            import io

            # Preprocess image for better OCR quality
            preprocessed = image_preprocessor.preprocess(image_bytes)

            # Load into PIL Image
            pil_image = Image.open(io.BytesIO(preprocessed))

            # Extract text with confidence data
            data = pytesseract.image_to_data(pil_image, lang="eng+hin", output_type=pytesseract.Output.DICT)

            # Build text and compute mean confidence
            words = []
            confidences = []
            for i, conf in enumerate(data["conf"]):
                text_word = data["text"][i].strip()
                if text_word and int(conf) > 0:
                    words.append(text_word)
                    confidences.append(int(conf))

            if not words:
                return False, "", 0.0, "Tesseract extracted no readable text from the document."

            full_text = " ".join(words)
            mean_confidence = sum(confidences) / len(confidences) / 100.0  # Normalize to 0.0-1.0

            return True, full_text, round(mean_confidence, 3), ""

        except Exception as e:
            return False, "", 0.0, f"Tesseract OCR exception: {str(e)}"

    async def health_check(self) -> Dict[str, Any]:
        """Check Tesseract installation status."""
        if not self._available:
            return {"status": "unavailable", "message": "pytesseract not installed"}
        try:
            import pytesseract
            version = pytesseract.get_tesseract_version()
            return {"status": "online", "version": str(version), "languages": "eng+hin"}
        except Exception:
            return {"status": "error", "message": "Tesseract binary not found in PATH"}
