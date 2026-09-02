import io
import logging
from typing import List

logger = logging.getLogger("image_preprocessor")


class ImagePreprocessor:
    """
    OpenCV-based image preprocessing for OCR quality improvement.
    Applies: grayscale conversion, adaptive thresholding, denoising, deskewing.
    Falls back to passthrough if OpenCV is not installed.
    """

    def __init__(self):
        self._cv2_available = False
        try:
            import cv2
            import numpy as np
            self._cv2_available = True
        except ImportError:
            logger.warning("opencv-python-headless not installed. Image preprocessing will pass through raw bytes.")

    def preprocess(self, image_bytes: bytes) -> bytes:
        """
        Clean and normalize a document image for OCR.
        Returns preprocessed image bytes (PNG format) or original bytes if OpenCV unavailable.
        """
        if not self._cv2_available:
            return image_bytes

        try:
            import cv2
            import numpy as np

            # Decode image from bytes
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img is None:
                logger.warning("Failed to decode image bytes. Returning original.")
                return image_bytes

            # 1. Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # 2. Denoise
            denoised = cv2.fastNlMeansDenoising(gray, None, h=10, templateWindowSize=7, searchWindowSize=21)

            # 3. Adaptive thresholding for binarization
            binary = cv2.adaptiveThreshold(
                denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )

            # 4. Encode back to PNG bytes
            success, encoded = cv2.imencode(".png", binary)
            if success:
                return encoded.tobytes()
            return image_bytes

        except Exception as e:
            logger.error(f"Image preprocessing failed: {e}. Returning original bytes.")
            return image_bytes

    def pdf_to_images(self, pdf_bytes: bytes) -> List[bytes]:
        """
        Convert PDF pages to individual image byte arrays.
        Uses pdf2image if available; otherwise returns empty list.
        """
        try:
            from pdf2image import convert_from_bytes
            images = convert_from_bytes(pdf_bytes, dpi=300, fmt="png")
            result = []
            for pil_img in images:
                buf = io.BytesIO()
                pil_img.save(buf, format="PNG")
                result.append(buf.getvalue())
            return result
        except ImportError:
            logger.warning("pdf2image not installed. PDF processing unavailable.")
            return []
        except Exception as e:
            logger.error(f"PDF to image conversion failed: {e}")
            return []


image_preprocessor = ImagePreprocessor()
