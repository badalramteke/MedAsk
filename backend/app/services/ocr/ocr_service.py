import time
import logging
from typing import Dict, Any, Tuple, Optional
from app.services.ocr.base_ocr import BaseOCRAdapter
from app.services.ocr.tesseract_adapter import TesseractOCRAdapter
from app.services.ocr.mock_ocr_adapter import MockOCRAdapter
from app.services.ocr.image_preprocessor import image_preprocessor

logger = logging.getLogger("ocr_service")

# Handwriting confidence threshold: if Tesseract confidence falls below this,
# the document is routed to MedGemma Vision instead (per OCR_PIPELINE.md Path 1B)
HANDWRITING_CONFIDENCE_THRESHOLD = 0.60


class OCRService:
    """
    Central OCR Orchestrator for MediKiosk Module B.
    Implements three-path document processing:
      Path 1A: Printed text → Tesseract → MedGemma text extraction
      Path 1B: Handwritten → Tesseract confidence check → MedGemma Vision fallback
      Path 2:  Medical imaging → direct MedGemma Multimodal (no OCR)

    Cascade: Tesseract → Mock (PaddleOCR can be added as a middle fallback later)
    """

    def __init__(self):
        self.tesseract_adapter = TesseractOCRAdapter()
        self.mock_adapter = MockOCRAdapter()

        self.ocr_cascade = [
            self.tesseract_adapter,
            self.mock_adapter,
        ]

    async def extract_text(
        self,
        image_bytes: bytes,
        mime_type: str = "image/jpeg",
        document_type: str = "LAB_REPORT"
    ) -> Dict[str, Any]:
        """
        Extract text from a document image using OCR cascade.

        Returns dict:
            success: bool
            text: str (extracted OCR text)
            confidence: float (0.0-1.0 mean confidence)
            engine_used: str (tesseract | mock)
            needs_vision_fallback: bool (True if handwriting confidence too low)
            latency_ms: float
            error: str
        """
        start_time = time.time()

        # Path 2: Imaging files skip OCR entirely
        if document_type == "IMAGING_SCAN":
            return {
                "success": False,
                "text": "",
                "confidence": 0.0,
                "engine_used": "NONE",
                "needs_vision_fallback": True,
                "latency_ms": 0.0,
                "error": "IMAGING_SCAN routed directly to MedGemma Multimodal — no OCR needed."
            }

        # Handle PDF files: rasterize pages first
        page_images = []
        if mime_type == "application/pdf":
            page_images = image_preprocessor.pdf_to_images(image_bytes)
            if not page_images:
                # PDF rasterization failed — try as single image anyway
                page_images = [image_bytes]
        else:
            page_images = [image_bytes]

        # Run OCR cascade across all pages
        all_text_parts = []
        total_confidence = 0.0
        pages_processed = 0
        engine_used = "NONE"
        needs_vision = False
        last_error = ""

        try:
            for page_idx, page_bytes in enumerate(page_images):
                page_success = False

                for adapter in self.ocr_cascade:
                    if isinstance(adapter, MockOCRAdapter):
                        success, text, conf, err = await adapter.extract_text(
                            page_bytes, mime_type, document_type=document_type
                        )
                    else:
                        success, text, conf, err = await adapter.extract_text(page_bytes, mime_type)

                    if success and text:
                        # Path 1B: Handwriting confidence gate
                        if document_type == "PRESCRIPTION" and conf < HANDWRITING_CONFIDENCE_THRESHOLD:
                            logger.info(
                                f"Tesseract confidence {conf:.2f} < threshold {HANDWRITING_CONFIDENCE_THRESHOLD} "
                                f"for PRESCRIPTION page {page_idx+1}. Flagging for MedGemma Vision fallback."
                            )
                            needs_vision = True
                            engine_used = adapter.name
                            # Still collect the low-confidence text as backup
                            all_text_parts.append(f"--- PAGE {page_idx + 1} (LOW CONFIDENCE) ---\n{text}")
                        else:
                            all_text_parts.append(
                                f"--- PAGE {page_idx + 1} ---\n{text}" if len(page_images) > 1 else text
                            )

                        total_confidence += conf
                        pages_processed += 1
                        engine_used = adapter.name
                        page_success = True
                        break
                    else:
                        last_error = err or f"{adapter.name} failed."

                if not page_success:
                    all_text_parts.append(f"--- PAGE {page_idx + 1} (FAILED) ---\n[OCR FAILED]")

        finally:
            # DPDP: Clear local references to raw image bytes
            page_images = []

        latency = round((time.time() - start_time) * 1000, 2)
        combined_text = "\n\n".join(all_text_parts)
        avg_confidence = (total_confidence / pages_processed) if pages_processed > 0 else 0.0

        if not combined_text.strip() or combined_text.strip() == "[OCR FAILED]":
            return {
                "success": False,
                "text": "",
                "confidence": 0.0,
                "engine_used": engine_used,
                "needs_vision_fallback": True,
                "latency_ms": latency,
                "error": f"All OCR adapters failed. Last: {last_error}"
            }

        return {
            "success": True,
            "text": combined_text,
            "confidence": round(avg_confidence, 3),
            "engine_used": engine_used,
            "needs_vision_fallback": needs_vision,
            "latency_ms": latency,
            "error": ""
        }

    async def get_health_status(self) -> Dict[str, Any]:
        """Check status across all OCR providers."""
        return {
            "tesseract": await self.tesseract_adapter.health_check(),
            "mock_ocr": await self.mock_adapter.health_check(),
            "overall_status": "online"
        }


ocr_service = OCRService()
