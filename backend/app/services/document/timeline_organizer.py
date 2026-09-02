import logging
from typing import List, Optional
from datetime import datetime

logger = logging.getLogger("timeline_organizer")


class TimelineOrganizer:
    """
    Organizes processed document extraction results into a chronological medical timeline.
    Documents with known dates are sorted oldest → newest.
    Documents with uncertain/unknown dates are appended at the end with appropriate flags.
    """

    def sort_chronologically(self, extraction_results: list) -> list:
        """
        Sort DocumentExtractionResult items by document_date.
        Returns a list of DocumentTimelineEntry dicts.
        """
        from app.models.document import DocumentTimelineEntry

        entries = []
        for result in extraction_results:
            # Build a one-line summary for timeline display
            summary_parts = []
            doc_type = result.document_type if hasattr(result, "document_type") else result.get("document_type", "OTHER")
            meds = result.extracted_medications if hasattr(result, "extracted_medications") else result.get("extracted_medications", [])
            labs = result.extracted_lab_results if hasattr(result, "extracted_lab_results") else result.get("extracted_lab_results", [])
            diags = result.extracted_diagnoses if hasattr(result, "extracted_diagnoses") else result.get("extracted_diagnoses", [])
            abnormals = result.abnormal_flags if hasattr(result, "abnormal_flags") else result.get("abnormal_flags", [])
            doc_id = result.document_id if hasattr(result, "document_id") else result.get("document_id", "")
            doc_date = result.document_date if hasattr(result, "document_date") else result.get("document_date")
            date_unc = result.date_uncertainty if hasattr(result, "date_uncertainty") else result.get("date_uncertainty", True)
            date_conf = result.date_confidence if hasattr(result, "date_confidence") else result.get("date_confidence", "UNKNOWN")
            source_tag = result.source_tag if hasattr(result, "source_tag") else result.get("source_tag", "")

            if doc_type == "PRESCRIPTION":
                med_count = len(meds)
                summary_parts.append(f"Prescription with {med_count} medication(s)")
                if diags:
                    diag_texts = [d.diagnosis_text if hasattr(d, "diagnosis_text") else d.get("diagnosis_text", "") for d in diags[:2]]
                    summary_parts.append(f"Dx: {', '.join(diag_texts)}")
            elif doc_type == "LAB_REPORT":
                lab_count = len(labs)
                abnormal_count = len(abnormals)
                summary_parts.append(f"Lab report with {lab_count} test(s)")
                if abnormal_count > 0:
                    summary_parts.append(f"⚠ {abnormal_count} abnormal value(s)")
            elif doc_type == "DISCHARGE_SUMMARY":
                summary_parts.append("Discharge summary")
                if diags:
                    diag_texts = [d.diagnosis_text if hasattr(d, "diagnosis_text") else d.get("diagnosis_text", "") for d in diags[:2]]
                    summary_parts.append(f"Dx: {', '.join(diag_texts)}")
            elif doc_type == "IMAGING_SCAN":
                summary_parts.append("Medical imaging scan")
            else:
                summary_parts.append("Medical document")

            entry = DocumentTimelineEntry(
                document_id=doc_id,
                document_type=doc_type,
                document_date=doc_date,
                date_uncertainty=date_unc,
                date_confidence=date_conf,
                summary_text=" — ".join(summary_parts),
                source_tag=source_tag,
                has_abnormals=len(abnormals) > 0,
                total_medications=len(meds),
                total_lab_results=len(labs),
                total_diagnoses=len(diags),
            )
            entries.append(entry)

        # Sort: known dates first (ascending), then unknown dates
        def sort_key(e):
            if e.document_date and not e.date_uncertainty:
                try:
                    return (0, e.document_date)
                except Exception:
                    return (1, "")
            elif e.document_date:
                return (1, e.document_date)
            else:
                return (2, "")

        entries.sort(key=sort_key)
        return entries


timeline_organizer = TimelineOrganizer()
