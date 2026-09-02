from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple


class BaseOCRAdapter(ABC):
    """
    Abstract base class for OCR engine adapters (Module B).
    Follows the same adapter pattern as BaseSpeechAdapter (Module E).
    """
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    async def extract_text(
        self, image_bytes: bytes, mime_type: str = "image/jpeg"
    ) -> Tuple[bool, str, float, str]:
        """
        Extract text from a document image.
        Returns: (success, extracted_text, confidence_score, error_message)
        """
        ...

    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Check adapter availability."""
        ...
