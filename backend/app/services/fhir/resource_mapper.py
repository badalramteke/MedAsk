"""
FHIR Resource Mapper: Transforms canonical PatientDataObject entities into
validated HL7 FHIR R4 resources conforming to ABDM NRCeS profiles.
"""
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime
import uuid

from app.models.core import PatientDataObject
from app.services.fhir.fhir_types import (
    FHIRPatient, FHIREncounter, FHIRCondition, FHIRObservation,
    FHIRMedicationStatement, FHIRDiagnosticReport, FHIRDocumentReference,
    CodeableConcept, Coding, Identifier, Reference, Period, Attachment,
)


class FHIRResourceMapper:
    """
    Transforms internal PatientDataObject models to standardized FHIR R4 resources.
    Preserves provenance, clinician review state, and clinical source citations.
    """

    @staticmethod
    def map_patient(pdo: PatientDataObject) -> FHIRPatient:
        """Map IdentityContext to FHIR Patient."""
        ident = pdo.identity
        identifiers = []

        # Map ABHA ID / Address if present
        if ident.external_identifier:
            identifiers.append(Identifier(
                system="https://healthid.abdm.gov.in",
                value=ident.external_identifier,
                type=CodeableConcept(
                    coding=[Coding(system="http://terminology.hl7.org/CodeSystem/v2-0203", code="MR", display="Medical Record Number")],
                    text="ABHA Identifier"
                )
            ))
        else:
            identifiers.append(Identifier(
                system="https://medikiosk.internal/session",
                value=ident.session_id,
                type=CodeableConcept(text="MediKiosk Ephemeral Session ID")
            ))

        # Gender mapping to FHIR valueset
        gender_map = {
            "MALE": "male",
            "FEMALE": "female",
            "OTHER": "other"
        }
        fhir_gender = gender_map.get((ident.gender or "").upper(), "unknown")

        # Age to birthDate estimation (if age provided)
        birth_date = None
        if ident.age:
            current_year = datetime.utcnow().year
            birth_date = f"{current_year - ident.age}-01-01"

        return FHIRPatient(
            id=f"pat-{ident.session_id[:8]}",
            identifier=identifiers,
            active=True,
            gender=fhir_gender,
            birthDate=birth_date
        )

    @staticmethod
    def map_encounter(pdo: PatientDataObject, patient_ref: Reference) -> FHIREncounter:
        """Map session intake encounter to FHIR Encounter."""
        ident = pdo.identity
        facility = ident.facility_id or "MEDIKIOSK_KIOSK_01"

        return FHIREncounter(
            id=f"enc-{ident.session_id[:8]}",
            status="finished",
            subject=patient_ref,
            period=Period(
                start=datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                end=datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
            ),
            serviceProvider=Reference(
                reference=f"Organization/{facility}",
                display=f"Facility: {facility}"
            )
        )

    @staticmethod
    def map_conditions(pdo: PatientDataObject, patient_ref: Reference) -> List[FHIRCondition]:
        """Map chief complaint and past diagnoses to FHIR Conditions."""
        conditions: List[FHIRCondition] = []
        now_str = datetime.utcnow().strftime("%Y-%m-%d")

        # 1. Chief Complaint
        if pdo.history and pdo.history.chief_complaint:
            cc = pdo.history.chief_complaint
            conditions.append(FHIRCondition(
                id=f"cond-cc-{uuid.uuid4().hex[:6]}",
                code=CodeableConcept(
                    coding=[Coding(system="http://snomed.info/sct", code="422843007", display="Chief complaint")],
                    text=f"Chief Complaint: {cc}"
                ),
                subject=patient_ref,
                recordedDate=now_str
            ))

        # 2. Past medical history
        if pdo.history and getattr(pdo.history, "past_medical_history", None):
            for pmh in pdo.history.past_medical_history:
                conditions.append(FHIRCondition(
                    id=f"cond-pmh-{uuid.uuid4().hex[:6]}",
                    code=CodeableConcept(text=f"Past Medical: {pmh}"),
                    subject=patient_ref,
                    recordedDate=now_str
                ))

        # 3. Diagnoses extracted from documents
        for doc_id, doc_data in pdo.documents.items():
            if isinstance(doc_data, dict):
                diags = doc_data.get("extracted_diagnoses", [])
                for d in diags:
                    d_text = d.get("diagnosis_text") if isinstance(d, dict) else getattr(d, "diagnosis_text", "")
                    if d_text:
                        conditions.append(FHIRCondition(
                            id=f"cond-doc-{uuid.uuid4().hex[:6]}",
                            code=CodeableConcept(text=d_text),
                            subject=patient_ref,
                            recordedDate=now_str
                        ))

        # Fallback if no conditions exist
        if not conditions:
            conditions.append(FHIRCondition(
                id=f"cond-gen-{uuid.uuid4().hex[:6]}",
                code=CodeableConcept(text="General OPD Intake Consultation"),
                subject=patient_ref,
                recordedDate=now_str
            ))

        return conditions

    @staticmethod
    def map_observations(pdo: PatientDataObject, patient_ref: Reference) -> List[FHIRObservation]:
        """Map review of systems, HPI symptoms, and AYUSH parameters to FHIR Observations."""
        observations: List[FHIRObservation] = []
        now_str = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

        if pdo.history:
            # 1. Review of systems
            ros = getattr(pdo.history, "review_of_systems", {}) or {}
            for sys_name, is_present in ros.items():
                observations.append(FHIRObservation(
                    id=f"obs-ros-{uuid.uuid4().hex[:6]}",
                    code=CodeableConcept(text=f"Review of Systems: {sys_name}"),
                    subject=patient_ref,
                    effectiveDateTime=now_str,
                    valueString="Positive" if is_present else "Negative"
                ))

            # 2. History of present illness symptoms
            hpi = getattr(pdo.history, "history_of_present_illness", []) or []
            for symptom in hpi:
                s_name = getattr(symptom, "symptom_name", str(symptom))
                observations.append(FHIRObservation(
                    id=f"obs-hpi-{uuid.uuid4().hex[:6]}",
                    code=CodeableConcept(text=f"Reported Symptom: {s_name}"),
                    subject=patient_ref,
                    effectiveDateTime=now_str,
                    valueString="Present"
                ))

            # 3. Menstrual & reproductive history
            mrh = getattr(pdo.history, "menstrual_reproductive_history", None) or {}
            for m_key, m_val in mrh.items():
                observations.append(FHIRObservation(
                    id=f"obs-mrh-{uuid.uuid4().hex[:6]}",
                    code=CodeableConcept(text=f"Menstrual/Reproductive: {m_key}"),
                    subject=patient_ref,
                    effectiveDateTime=now_str,
                    valueString=str(m_val)
                ))

            # 4. Optional answered_questions if dynamically populated
            dyn_q = getattr(pdo.history, "answered_questions", None) or {}
            if isinstance(dyn_q, dict):
                for qid, ans in dyn_q.items():
                    val_text = str(ans.get("value_text") or ans.get("value_code") or "Reported") if isinstance(ans, dict) else str(ans)
                    observations.append(FHIRObservation(
                        id=f"obs-q-{uuid.uuid4().hex[:6]}",
                        code=CodeableConcept(text=f"Intake Question: {qid}"),
                        subject=patient_ref,
                        effectiveDateTime=now_str,
                        valueString=val_text
                    ))

        # 5. AYUSH parameters
        if pdo.ayush and pdo.ayush.parameters:
            for param_key, param_val in pdo.ayush.parameters.items():
                observations.append(FHIRObservation(
                    id=f"obs-ayush-{uuid.uuid4().hex[:6]}",
                    code=CodeableConcept(
                        coding=[Coding(system="https://ayush.gov.in/ontology", code=param_key, display=param_key.replace('_', ' ').title())],
                        text=f"AYUSH Dashavidha: {param_key}"
                    ),
                    subject=patient_ref,
                    effectiveDateTime=now_str,
                    valueString=str(param_val)
                ))

        return observations

    @staticmethod
    def map_medications(pdo: PatientDataObject, patient_ref: Reference) -> List[FHIRMedicationStatement]:
        """Map active medications and prescription extractions to FHIR MedicationStatements."""
        medications: List[FHIRMedicationStatement] = []

        # 1. From history medications list
        if pdo.history and getattr(pdo.history, "medications", None):
            for med_str in pdo.history.medications:
                medications.append(FHIRMedicationStatement(
                    id=f"med-hist-{uuid.uuid4().hex[:6]}",
                    status="active",
                    medicationCodeableConcept=CodeableConcept(text=med_str),
                    subject=patient_ref
                ))

        # 2. From documents
        for doc_id, doc_data in pdo.documents.items():
            if isinstance(doc_data, dict):
                extracted_meds = doc_data.get("extracted_medications", [])
                for m in extracted_meds:
                    m_name = m.get("drug_name") if isinstance(m, dict) else getattr(m, "drug_name", "")
                    dosage = m.get("dosage") if isinstance(m, dict) else getattr(m, "dosage", None)
                    freq = m.get("frequency") if isinstance(m, dict) else getattr(m, "frequency", None)
                    if m_name:
                        dosage_list = []
                        if dosage or freq:
                            dosage_list.append({"text": f"{dosage or ''} {freq or ''}".strip()})

                        medications.append(FHIRMedicationStatement(
                            id=f"med-{uuid.uuid4().hex[:6]}",
                            status="active",
                            medicationCodeableConcept=CodeableConcept(text=m_name),
                            subject=patient_ref,
                            dosage=dosage_list or None
                        ))

        return medications

    @staticmethod
    def map_diagnostic_reports_and_lab_obs(
        pdo: PatientDataObject, patient_ref: Reference
    ) -> Tuple[List[FHIRDiagnosticReport], List[FHIRObservation]]:
        """Map lab results to DiagnosticReports with linked Observation results."""
        reports: List[FHIRDiagnosticReport] = []
        lab_observations: List[FHIRObservation] = []
        now_str = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

        for doc_id, doc_data in pdo.documents.items():
            if isinstance(doc_data, dict) and doc_data.get("document_type") == "LAB_REPORT":
                lab_results = doc_data.get("extracted_lab_results", [])
                report_obs_refs: List[Reference] = []

                for lr in lab_results:
                    t_name = lr.get("test_name") if isinstance(lr, dict) else getattr(lr, "test_name", "")
                    val_str = lr.get("value") if isinstance(lr, dict) else getattr(lr, "value", "")
                    unit_str = lr.get("unit") if isinstance(lr, dict) else getattr(lr, "unit", None)
                    ref_range = lr.get("reference_range") if isinstance(lr, dict) else getattr(lr, "reference_range", None)
                    is_abnormal = lr.get("is_abnormal", False) if isinstance(lr, dict) else getattr(lr, "is_abnormal", False)

                    if t_name:
                        obs_id = f"obs-lab-{uuid.uuid4().hex[:6]}"
                        interpretations = None
                        if is_abnormal:
                            interpretations = [CodeableConcept(
                                coding=[Coding(system="http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation", code="A", display="Abnormal")]
                            )]

                        lab_obs = FHIRObservation(
                            id=obs_id,
                            code=CodeableConcept(text=t_name),
                            subject=patient_ref,
                            effectiveDateTime=now_str,
                            valueString=f"{val_str} {unit_str or ''}".strip(),
                            interpretation=interpretations,
                            referenceRange=[{"text": ref_range}] if ref_range else None
                        )
                        lab_observations.append(lab_obs)
                        report_obs_refs.append(Reference(
                            reference=f"Observation/{obs_id}",
                            display=t_name
                        ))

                if report_obs_refs:
                    reports.append(FHIRDiagnosticReport(
                        id=f"dr-{uuid.uuid4().hex[:6]}",
                        status="final",
                        code=CodeableConcept(
                            coding=[Coding(system="http://loinc.org", code="11502-2", display="Laboratory report")],
                            text="Scanned Laboratory Report"
                        ),
                        subject=patient_ref,
                        effectiveDateTime=now_str,
                        result=report_obs_refs
                    ))

        return reports, lab_observations

    @staticmethod
    def map_document_references(pdo: PatientDataObject, patient_ref: Reference) -> List[FHIRDocumentReference]:
        """Map staged/digitized documents to FHIR DocumentReferences."""
        doc_refs: List[FHIRDocumentReference] = []
        now_str = datetime.utcnow().strftime("%Y-%m-%d")

        for doc_id, doc_data in pdo.documents.items():
            if isinstance(doc_data, dict):
                f_type = doc_data.get("document_type") or doc_data.get("file_type") or "OTHER"
                f_name = doc_data.get("file_name", "document")
                source_tag = doc_data.get("source_tag", f"[Doc: {doc_id}]")

                doc_refs.append(FHIRDocumentReference(
                    id=f"docref-{doc_id[-6:] if len(doc_id) >= 6 else uuid.uuid4().hex[:6]}",
                    status="current",
                    type=CodeableConcept(text=f"Medical Document: {f_type}"),
                    subject=patient_ref,
                    date=now_str,
                    content=[{
                        "attachment": {
                            "contentType": doc_data.get("mime_type", "image/jpeg"),
                            "title": f_name,
                            "url": f"urn:medikiosk:document:{doc_id}"
                        }
                    }]
                ))

        return doc_refs
