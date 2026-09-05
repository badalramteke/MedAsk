"""
MediKiosk OCR Service Package (Module B — Document Digitization).
Three-path document processing:
  Path 1A: Printed text → Tesseract → MedGemma entity extraction
  Path 1B: Handwritten → confidence gate → MedGemma Vision fallback
  Path 2:  Medical imaging → direct MedGemma Multimodal (no OCR)
"""
from app.services.ocr.base_ocr import BaseOCRAdapter
from app.services.ocr.tesseract_adapter import TesseractOCRAdapter
from app.services.ocr.mock_ocr_adapter import MockOCRAdapter
from app.services.ocr.image_preprocessor import ImagePreprocessor, image_preprocessor
from app.services.ocr.ocr_service import OCRService, ocr_service

__all__ = [
    "BaseOCRAdapter",
    "TesseractOCRAdapter",
    "MockOCRAdapter",
    "ImagePreprocessor",
    "image_preprocessor",
    "OCRService",
    "ocr_service",
]
