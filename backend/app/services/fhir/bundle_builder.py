"""
FHIR Document Bundle Builder: Assembles a complete, validated HL7 FHIR R4
Document Bundle conforming to ABDM NRCeS OPConsultRecord specifications.
CRITICAL ABDM RULE: entry[0] MUST ALWAYS be the Composition resource.
"""
from typing import List, Dict, Any
from datetime import datetime
import uuid

from app.models.core import PatientDataObject
from app.services.fhir.fhir_types import (
    FHIRBundle, FHIRBundleEntry, FHIRComposition, FHIRCompositionSection,
    Reference, Narrative, CodeableConcept, Coding, Identifier
)
from app.services.fhir.resource_mapper import FHIRResourceMapper


class FHIRBundleBuilder:
    """
    Builds the ABDM OPConsultRecord Document Bundle from validated PatientDataObject.
    """

    @classmethod
    def build_document_bundle(cls, pdo: PatientDataObject) -> FHIRBundle:
        """
        Assemble the complete FHIR R4 Document Bundle.
        Guarantees entry[0] is the root Composition resource.
        """
        bundle_id = f"bundle-{uuid.uuid4().hex}"
        now_iso = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

        # 1. Map base resources
        patient = FHIRResourceMapper.map_patient(pdo)
        pat_urn = f"urn:uuid:{patient.id}"
        patient_ref = Reference(reference=pat_urn, display=f"Patient {pdo.identity.session_id[:8]}")

        encounter = FHIRResourceMapper.map_encounter(pdo, patient_ref)
        enc_urn = f"urn:uuid:{encounter.id}"
        encounter_ref = Reference(reference=enc_urn, display="OPD Encounter")

        conditions = FHIRResourceMapper.map_conditions(pdo, patient_ref)
        observations = FHIRResourceMapper.map_observations(pdo, patient_ref)
        medications = FHIRResourceMapper.map_medications(pdo, patient_ref)
        reports, lab_observations = FHIRResourceMapper.map_diagnostic_reports_and_lab_obs(pdo, patient_ref)
        doc_refs = FHIRResourceMapper.map_document_references(pdo, patient_ref)

        # 2. Build Composition Sections referencing resources
        sections: List[FHIRCompositionSection] = []

        # Section A: Chief Complaint & Present Illness
        cond_refs = [Reference(reference=f"urn:uuid:{c.id}", display=c.code.text) for c in conditions]
        cc_text = pdo.history.chief_complaint if pdo.history else "General OPD consultation"
        sections.append(FHIRCompositionSection(
            title="Chief Complaints & History of Present Illness",
            code=CodeableConcept(
                coding=[Coding(system="http://snomed.info/sct", code="422843007", display="Chief complaint section")],
                text="Chief Complaints"
            ),
            text=Narrative(
                status="generated",
                div=f"<div xmlns=\"http://www.w3.org/1999/xhtml\"><p><strong>Chief Complaint:</strong> {cc_text}</p></div>"
            ),
            entry=cond_refs
        ))

        # Section B: Review of Systems & Intake Observations
        if observations:
            obs_refs = [Reference(reference=f"urn:uuid:{o.id}", display=o.code.text) for o in observations]
            sections.append(FHIRCompositionSection(
                title="Review of Systems & Patient Intake Observations",
                code=CodeableConcept(
                    coding=[Coding(system="http://snomed.info/sct", code="425044008", display="Physical exam section")],
                    text="Intake Observations"
                ),
                text=Narrative(
                    status="generated",
                    div=f"<div xmlns=\"http://www.w3.org/1999/xhtml\"><p>Total structured intake observations: {len(observations)}</p></div>"
                ),
                entry=obs_refs
            ))

        # Section C: Medications & Prescriptions
        if medications:
            med_refs = [Reference(reference=f"urn:uuid:{m.id}", display=m.medicationCodeableConcept.text) for m in medications]
            sections.append(FHIRCompositionSection(
                title="Medications & Active Prescriptions",
                code=CodeableConcept(
                    coding=[Coding(system="http://snomed.info/sct", code="10160-0", display="History of medication use")],
                    text="Medications"
                ),
                text=Narrative(
                    status="generated",
                    div=f"<div xmlns=\"http://www.w3.org/1999/xhtml\"><p>Active medications recorded: {len(medications)}</p></div>"
                ),
                entry=med_refs
            ))

        # Section D: Prior Diagnostic Reports & Lab Findings
        all_lab_and_report_refs = [Reference(reference=f"urn:uuid:{r.id}", display=r.code.text) for r in reports]
        all_lab_and_report_refs.extend([Reference(reference=f"urn:uuid:{lo.id}", display=lo.code.text) for lo in lab_observations])
        if all_lab_and_report_refs:
            sections.append(FHIRCompositionSection(
                title="Diagnostic Reports & Laboratory Investigations",
                code=CodeableConcept(
                    coding=[Coding(system="http://snomed.info/sct", code="30954-2", display="Relevant diagnostic tests")],
                    text="Investigations"
                ),
                text=Narrative(
                    status="generated",
                    div=f"<div xmlns=\"http://www.w3.org/1999/xhtml\"><p>Prior lab reports and test observations attached: {len(all_lab_and_report_refs)}</p></div>"
                ),
                entry=all_lab_and_report_refs
            ))

        # Section E: Scanned Medical Documents
        if doc_refs:
            doc_entry_refs = [Reference(reference=f"urn:uuid:{dr.id}", display=dr.type.text) for dr in doc_refs]
            sections.append(FHIRCompositionSection(
                title="Attached Scanned Medical Documents",
                code=CodeableConcept(
                    coding=[Coding(system="http://snomed.info/sct", code="371530004", display="Clinical report")],
                    text="Attached Documents"
                ),
                text=Narrative(
                    status="generated",
                    div=f"<div xmlns=\"http://www.w3.org/1999/xhtml\"><p>Total digitized documents indexed: {len(doc_refs)}</p></div>"
                ),
                entry=doc_entry_refs
            ))

        # 3. Create Root Composition Resource
        comp_id = f"comp-{uuid.uuid4().hex[:8]}"
        comp_urn = f"urn:uuid:{comp_id}"
        facility_name = pdo.identity.facility_id or "MediKiosk Clinical Station"
        author_ref = Reference(reference=f"Organization/{facility_name}", display=facility_name)

        composition = FHIRComposition(
            id=comp_id,
            status="final",
            subject=patient_ref,
            encounter=encounter_ref,
            date=now_iso,
            author=[author_ref],
            title="OPD Consultation Record (MediKiosk First-Mile Intake)",
            section=sections
        )

        # 4. Assemble Bundle Entries:
        # MANDATORY ABDM RULE: entry[0] is Composition!
        entries: List[FHIRBundleEntry] = []
        entries.append(FHIRBundleEntry(fullUrl=comp_urn, resource=composition))

        # Followed by Patient & Encounter
        entries.append(FHIRBundleEntry(fullUrl=pat_urn, resource=patient))
        entries.append(FHIRBundleEntry(fullUrl=enc_urn, resource=encounter))

        # Followed by referenced resources
        for c in conditions:
            entries.append(FHIRBundleEntry(fullUrl=f"urn:uuid:{c.id}", resource=c))
        for o in observations:
            entries.append(FHIRBundleEntry(fullUrl=f"urn:uuid:{o.id}", resource=o))
        for m in medications:
            entries.append(FHIRBundleEntry(fullUrl=f"urn:uuid:{m.id}", resource=m))
        for r in reports:
            entries.append(FHIRBundleEntry(fullUrl=f"urn:uuid:{r.id}", resource=r))
        for lo in lab_observations:
            entries.append(FHIRBundleEntry(fullUrl=f"urn:uuid:{lo.id}", resource=lo))
        for dr in doc_refs:
            entries.append(FHIRBundleEntry(fullUrl=f"urn:uuid:{dr.id}", resource=dr))

        # 5. Build final FHIR Document Bundle
        bundle = FHIRBundle(
            id=bundle_id,
            identifier=Identifier(
                system="https://healthid.abdm.gov.in/bundle",
                value=f"ABDM-BUNDLE-{pdo.identity.session_id[:8]}"
            ),
            type="document",
            timestamp=now_iso,
            entry=entries
        )

        return bundle
