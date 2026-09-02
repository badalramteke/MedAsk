from typing import Dict, Any, Tuple
from app.services.ocr.base_ocr import BaseOCRAdapter


# Realistic mock OCR outputs for deterministic testing per document type
MOCK_OCR_OUTPUTS = {
    "PRESCRIPTION": """Dr. Rajesh Kumar, MBBS, MD (Internal Medicine)
AIIMS New Delhi - OPD Prescription
Date: 15-Mar-2024

Patient: Mrs. Sunita Devi, Age: 52/F

Rx:
1. Tab. Metformin 500mg - 1 tablet twice daily after meals x 30 days
2. Tab. Amlodipine 5mg - 1 tablet once daily morning x 30 days
3. Tab. Atorvastatin 10mg - 1 tablet at bedtime x 30 days
4. Tab. Ecosprin 75mg - 1 tablet once daily after lunch x 30 days

Diagnosis: Type 2 Diabetes Mellitus, Essential Hypertension, Dyslipidemia

Follow-up: After 1 month with HbA1c and Lipid Profile reports
Next Visit: 15-Apr-2024""",

    "LAB_REPORT": """AIIMS Pathology Laboratory
Complete Blood Count (CBC) Report
Date: 10-May-2024

Patient: Mrs. Sunita Devi, Age: 52/F
Sample: EDTA Whole Blood
Report ID: LAB-2024-05-0847

Test Name          | Result  | Unit      | Reference Range
Hemoglobin         | 9.8     | g/dL      | 12.0 - 15.5
RBC Count          | 3.8     | million/µL| 3.8 - 5.2
WBC Count          | 11.5    | 10³/µL    | 4.0 - 11.0
Platelet Count     | 220     | 10³/µL    | 150 - 400
HbA1c              | 8.2     | %         | < 5.7
Blood Glucose (F)  | 156     | mg/dL     | 70 - 100
Blood Glucose (PP) | 245     | mg/dL     | 70 - 140
Creatinine         | 1.1     | mg/dL     | 0.59 - 1.04
TSH                | 3.5     | mIU/L     | 0.4 - 4.0
Total Cholesterol  | 242     | mg/dL     | < 200
LDL                | 165     | mg/dL     | < 100

Pathologist: Dr. Meena Sharma, MD Pathology""",

    "DISCHARGE_SUMMARY": """DISCHARGE SUMMARY
All India Institute of Ayurveda, New Delhi
Date of Admission: 01-Jan-2024
Date of Discharge: 05-Jan-2024

Patient: Mrs. Sunita Devi, Age: 52/F, ABHA: 91-XXXX-XXXX-XXXX

Diagnosis at Admission: Acute exacerbation of Type 2 Diabetes Mellitus with Diabetic Ketoacidosis

Procedure: IV Insulin infusion, Fluid resuscitation

Course in Hospital:
Patient was admitted with blood sugar of 450 mg/dL and ketones in urine. 
Managed with IV insulin drip and normal saline. Blood sugar stabilized over 48 hours.
Transitioned to subcutaneous insulin on day 3. Discharged on oral hypoglycemics.

Discharge Medications:
1. Tab. Metformin 1000mg BD
2. Tab. Glimepiride 2mg OD before breakfast
3. Inj. Insulin Glargine 10 units SC at bedtime

Advice: Strict diabetic diet, daily blood sugar monitoring, follow up in 2 weeks.""",

    "IMAGING_SCAN": "MEDICAL_IMAGING_NO_OCR_TEXT",

    "OTHER": """General Medical Document
Date: 20-Feb-2024
Patient notes and miscellaneous clinical information.
Blood pressure: 150/95 mmHg
Weight: 68 kg
SpO2: 97%"""
}


class MockOCRAdapter(BaseOCRAdapter):
    """
    Deterministic offline mock OCR adapter for testing.
    Returns realistic multi-section text per document type without external dependencies.
    """

    def __init__(self):
        super().__init__(name="MOCK_OCR")

    async def extract_text(
        self, image_bytes: bytes, mime_type: str = "image/jpeg",
        document_type: str = "LAB_REPORT"
    ) -> Tuple[bool, str, float, str]:
        """
        Return deterministic mock OCR text based on document type.
        Always succeeds with high confidence.
        """
        text = MOCK_OCR_OUTPUTS.get(document_type, MOCK_OCR_OUTPUTS["OTHER"])

        if document_type == "IMAGING_SCAN":
            return False, "", 0.0, "Imaging documents do not contain extractable text — route to MedGemma Multimodal."

        return True, text, 0.92, ""

    async def health_check(self) -> Dict[str, Any]:
        """Mock OCR is always online."""
        return {
            "status": "online",
            "provider": "MOCK_OCR",
            "offline_ready": True
        }
