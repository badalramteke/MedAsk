import json
import logging
import re
from typing import Optional, Dict, Any, List
from datetime import datetime
from app.models.document import (
    DocumentExtractionResult,
    ExtractedMedication,
    ExtractedLabResult,
    ExtractedDiagnosis,
)
from app.models.provenance import Provenance

logger = logging.getLogger("entity_extractor")

# Common date patterns found in Indian medical documents
DATE_PATTERNS = [
    r"\b(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})\b",          # DD-MM-YYYY or DD/MM/YYYY
    r"\b(\d{1,2}\s*(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s*\d{2,4})\b",  # 15 Mar 2024
    r"\bDate\s*:\s*(.+?)(?:\n|$)",                       # Date: <value>
    r"\bDated?\s*:\s*(.+?)(?:\n|$)",                     # Dated: <value>
]


class DocumentEntityExtractor:
    """
    Coordinates entity extraction from OCR text using ModelService.
    Steps:
      1. Extract document date first (priority: printed → contextual → LLM inferred)
      2. Call ModelService.extract_document_entities() for clinical structuring
      3. Parse JSON response into DocumentExtractionResult
      4. Handle chunking for large documents (>4000 chars)
    """

    def _extract_date_from_text(self, ocr_text: str) -> tuple:
        """
        Extract document date from OCR text using regex patterns.
        Returns: (date_string_or_None, confidence: PRINTED|CONTEXTUAL|UNKNOWN)
        """
        for pattern in DATE_PATTERNS:
            match = re.search(pattern, ocr_text, re.IGNORECASE)
            if match:
                raw_date = match.group(1).strip()
                # Try to parse into ISO format
                iso_date = self._normalize_date(raw_date)
                if iso_date:
                    # If found via "Date:" header → PRINTED confidence
                    if "date" in pattern.lower():
                        return iso_date, "PRINTED"
                    return iso_date, "CONTEXTUAL"

        return None, "UNKNOWN"

    def _normalize_date(self, raw: str) -> Optional[str]:
        """Attempt to parse raw date string into ISO format."""
        formats = [
            "%d-%m-%Y", "%d/%m/%Y", "%d-%m-%y", "%d/%m/%y",
            "%d %B %Y", "%d %b %Y", "%d %B %y", "%d %b %y",
            "%d-%b-%Y", "%d-%B-%Y", "%Y-%m-%d",
        ]
        for fmt in formats:
            try:
                dt = datetime.strptime(raw.strip(), fmt)
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                continue
        return None

    async def extract_entities(
        self,
        ocr_text: str,
        document_id: str,
        session_id: str,
        document_type: str,
        source_tag: str,
        ocr_engine_used: str = "mock",
    ) -> DocumentExtractionResult:
        """
        Extract structured clinical entities from OCR text using ModelService.
        Falls back to regex/mock parsing if ModelService is unavailable.
        """
        from app.services.model_service import model_service
        from app.models.ai import ModelCapability

        # 1. Extract date first (per OCR_PIPELINE.md date-first requirement)
        doc_date, date_confidence = self._extract_date_from_text(ocr_text)
        date_uncertainty = date_confidence in ("INFERRED", "UNKNOWN")

        # 2. Call ModelService for entity extraction
        try:
            model_response = await model_service.extract_document_entities(
                ocr_text=ocr_text,
                document_type=document_type,
                source_tag=source_tag,
                session_id=session_id,
            )

            if model_response.success and model_response.structured_payload:
                payload = model_response.structured_payload

                # Parse medications
                medications = [
                    ExtractedMedication(
                        drug_name=m.get("drug_name", "Unknown"),
                        dosage=m.get("dosage"),
                        frequency=m.get("frequency"),
                        route=m.get("route"),
                        duration=m.get("duration"),
                        source_tag=source_tag,
                        confidence=m.get("confidence", 0.8),
                    )
                    for m in payload.get("medications", [])
                ]

                # Parse lab results
                lab_results = [
                    ExtractedLabResult(
                        test_name=lr.get("test_name", "Unknown"),
                        value=str(lr.get("value", "")),
                        unit=lr.get("unit"),
                        reference_range=lr.get("reference_range"),
                        source_tag=source_tag,
                        confidence=lr.get("confidence", 0.85),
                    )
                    for lr in payload.get("lab_results", [])
                ]

                # Parse diagnoses
                diagnoses = [
                    ExtractedDiagnosis(
                        diagnosis_text=d.get("diagnosis_text", "Unknown"),
                        icd_hint=d.get("icd_hint"),
                        source_tag=source_tag,
                        confidence=d.get("confidence", 0.75),
                    )
                    for d in payload.get("diagnoses", [])
                ]

                procedures = payload.get("procedures", [])
                clinician_flags = payload.get("clinician_review_flags", [])

                # Use LLM-extracted date if regex didn't find one
                if not doc_date and payload.get("document_date"):
                    doc_date = payload["document_date"]
                    date_confidence = "INFERRED"
                    date_uncertainty = True

                return DocumentExtractionResult(
                    document_id=document_id,
                    session_id=session_id,
                    document_type=document_type,
                    source_tag=source_tag,
                    ocr_raw_text_length=len(ocr_text),
                    ocr_engine_used=ocr_engine_used,
                    document_date=doc_date,
                    date_confidence=date_confidence,
                    date_uncertainty=date_uncertainty,
                    extracted_medications=medications,
                    extracted_lab_results=lab_results,
                    extracted_diagnoses=diagnoses,
                    extracted_procedures=procedures,
                    clinician_review_flags=clinician_flags,
                    review_status="PENDING",
                    provenance=Provenance(
                        source_type="AI_EXTRACTED",
                        source_id=f"ModelService:{model_response.provider_used}",
                        confidence=model_response.confidence_score,
                    ),
                )

        except Exception as e:
            logger.error(f"ModelService entity extraction failed: {e}. Using mock fallback.")

        # 3. Fallback: return minimal extraction with date only
        return DocumentExtractionResult(
            document_id=document_id,
            session_id=session_id,
            document_type=document_type,
            source_tag=source_tag,
            ocr_raw_text_length=len(ocr_text),
            ocr_engine_used=ocr_engine_used,
            document_date=doc_date,
            date_confidence=date_confidence,
            date_uncertainty=date_uncertainty,
            clinician_review_flags=["Entity extraction failed — manual review required"],
            review_status="PENDING",
            provenance=Provenance(
                source_type="AI_EXTRACTED",
                source_id="fallback_regex_only",
                confidence=0.3,
            ),
        )


entity_extractor = DocumentEntityExtractor()
