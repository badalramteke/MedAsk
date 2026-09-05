import json
import os
import logging
from typing import List, Optional, Dict, Any

logger = logging.getLogger("lab_normalizer")

# Path to lab reference ranges data file
LAB_RANGES_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
    "data", "clinical", "lab_reference_ranges.json"
)


class LabValueNormalizer:
    """
    Flags abnormal lab values by comparing extracted results against standard reference ranges.
    Reference ranges are gender-adjusted where applicable.
    Severity levels: LOW (borderline), MODERATE (clinically notable), HIGH (critical).
    """

    def __init__(self):
        self._ranges: Dict[str, Any] = {}
        self._load_ranges()

    def _load_ranges(self):
        """Load reference ranges from JSON data file."""
        try:
            if os.path.exists(LAB_RANGES_FILE):
                with open(LAB_RANGES_FILE, "r", encoding="utf-8") as f:
                    self._ranges = json.load(f)
                logger.info(f"Loaded {len(self._ranges)} lab reference ranges from {LAB_RANGES_FILE}")
            else:
                logger.warning(f"Lab reference ranges file not found at {LAB_RANGES_FILE}. Using empty ranges.")
                self._ranges = self._get_default_ranges()
        except Exception as e:
            logger.error(f"Failed to load lab ranges: {e}. Using defaults.")
            self._ranges = self._get_default_ranges()

    def _get_default_ranges(self) -> Dict[str, Any]:
        """Fallback inline reference ranges if JSON file unavailable."""
        return {
            "hemoglobin": {"male": {"low": 13.0, "high": 17.0}, "female": {"low": 12.0, "high": 15.5}, "unit": "g/dL"},
            "wbc_count": {"low": 4.0, "high": 11.0, "unit": "10^3/µL"},
            "platelet_count": {"low": 150, "high": 400, "unit": "10^3/µL"},
            "blood_glucose_fasting": {"low": 70, "high": 100, "unit": "mg/dL"},
            "blood_glucose_pp": {"low": 70, "high": 140, "unit": "mg/dL"},
            "hba1c": {"low": 0, "high": 5.7, "unit": "%"},
            "creatinine": {"male": {"low": 0.74, "high": 1.35}, "female": {"low": 0.59, "high": 1.04}, "unit": "mg/dL"},
        }

    def _normalize_test_name(self, test_name: str) -> str:
        """Normalize test name to match keys in reference ranges."""
        normalized = test_name.strip().lower()
        # Common aliases
        aliases = {
            "hb": "hemoglobin", "haemoglobin": "hemoglobin",
            "wbc": "wbc_count", "white blood cell": "wbc_count", "total wbc": "wbc_count",
            "plt": "platelet_count", "platelet": "platelet_count", "platelets": "platelet_count",
            "fbs": "blood_glucose_fasting", "fasting glucose": "blood_glucose_fasting",
            "blood glucose (f)": "blood_glucose_fasting", "blood glucose fasting": "blood_glucose_fasting",
            "ppbs": "blood_glucose_pp", "pp glucose": "blood_glucose_pp",
            "blood glucose (pp)": "blood_glucose_pp", "blood glucose pp": "blood_glucose_pp",
            "glycated hemoglobin": "hba1c", "glycosylated hemoglobin": "hba1c",
            "serum creatinine": "creatinine",
            "na": "sodium", "na+": "sodium", "serum sodium": "sodium",
            "k": "potassium", "k+": "potassium", "serum potassium": "potassium",
            "sgpt": "alt", "alanine aminotransferase": "alt",
            "sgot": "ast", "aspartate aminotransferase": "ast",
            "thyroid stimulating hormone": "tsh",
            "tc": "total_cholesterol", "total cholesterol": "total_cholesterol",
            "low density lipoprotein": "ldl",
            "high density lipoprotein": "hdl",
            "uric acid": "uric_acid", "serum uric acid": "uric_acid",
            "oxygen saturation": "spo2",
            "rbc": "rbc_count", "rbc count": "rbc_count",
            "total bilirubin": "total_bilirubin", "bilirubin": "total_bilirubin",
        }
        return aliases.get(normalized, normalized.replace(" ", "_"))

    def _get_range(self, test_key: str, gender: str = "female") -> Optional[Dict]:
        """Get reference range for a test, with gender adjustment."""
        range_data = self._ranges.get(test_key)
        if not range_data:
            return None

        # Check if gender-specific ranges exist
        if "male" in range_data and "female" in range_data:
            gender_key = gender.lower() if gender.lower() in ("male", "female") else "female"
            gen_range = range_data[gender_key]
            return {"low": gen_range["low"], "high": gen_range["high"], "unit": range_data.get("unit", "")}
        elif "low" in range_data and "high" in range_data:
            return {"low": range_data["low"], "high": range_data["high"], "unit": range_data.get("unit", "")}

        return None

    def _calculate_severity(self, value: float, low: float, high: float) -> str:
        """
        Determine severity based on how far the value deviates from normal range.
        LOW: within 10% beyond range, MODERATE: 10-30% beyond, HIGH: >30% beyond.
        """
        range_span = high - low if high > low else 1.0

        if value < low:
            deviation = (low - value) / range_span
        elif value > high:
            deviation = (value - high) / range_span
        else:
            return "LOW"  # Should not reach here, but safety fallback

        if deviation > 0.30:
            return "HIGH"
        elif deviation > 0.10:
            return "MODERATE"
        return "LOW"

    def flag_abnormals(
        self,
        extracted_lab_results: list,
        gender: str = "female",
        source_tag: str = ""
    ) -> list:
        """
        Check extracted lab results against reference ranges and flag abnormals.
        Returns list of AbnormalLabFlag dicts.
        """
        from app.models.document import AbnormalLabFlag

        flags = []
        for lab in extracted_lab_results:
            test_name = lab.get("test_name", "") if isinstance(lab, dict) else lab.test_name
            value_str = lab.get("value", "") if isinstance(lab, dict) else lab.value
            tag = lab.get("source_tag", source_tag) if isinstance(lab, dict) else lab.source_tag

            # Parse numeric value
            try:
                numeric_value = float(value_str.replace(",", "").strip())
            except (ValueError, AttributeError):
                continue  # Skip non-numeric values

            # Normalize test name and lookup range
            test_key = self._normalize_test_name(test_name)
            ref = self._get_range(test_key, gender)
            if not ref:
                continue  # No reference range available

            low = ref["low"]
            high = ref["high"]
            unit = ref.get("unit", "")

            # Check if abnormal
            if numeric_value < low or numeric_value > high:
                severity = self._calculate_severity(numeric_value, low, high)
                flags.append(AbnormalLabFlag(
                    test_name=test_name,
                    extracted_value=value_str,
                    unit=unit,
                    ref_range_low=low,
                    ref_range_high=high,
                    severity=severity,
                    source_tag=tag
                ))

        return flags


lab_normalizer = LabValueNormalizer()
