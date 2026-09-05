"""
FHIR R4 Schema Definitions for ABDM NRCeS Compliance.
Self-contained, type-safe Pydantic v2 models conforming to HL7 FHIR R4
and National Resource Center for EHR Standards (NRCeS) India profiles:
  - OPConsultRecord (Composition)
  - DiagnosticReportRecord
  - DocumentReference
  - Patient, Encounter, Condition, Observation, MedicationStatement
  - Document Bundle envelope (type: document)
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
import uuid


class Coding(BaseModel):
    system: Optional[str] = Field(None, description="Identity of the terminology system (e.g. SNOMED CT, LOINC)")
    code: Optional[str] = Field(None, description="Symbol in syntax defined by the system")
    display: Optional[str] = Field(None, description="Representation defined by the system")


class CodeableConcept(BaseModel):
    coding: List[Coding] = Field(default_factory=list)
    text: Optional[str] = Field(None, description="Plain text representation")


class Identifier(BaseModel):
    system: Optional[str] = Field(None, description="The namespace for the identifier value (e.g. ABHA, MRN)")
    value: str = Field(..., description="The value that is unique")
    type: Optional[CodeableConcept] = None


class Reference(BaseModel):
    reference: str = Field(..., description="Literal reference, Relative, internal or absolute URL (e.g. urn:uuid:... or Patient/P1)")
    display: Optional[str] = Field(None, description="Text alternative for the resource")
    type: Optional[str] = None


class Period(BaseModel):
    start: Optional[str] = None
    end: Optional[str] = None


class Attachment(BaseModel):
    contentType: Optional[str] = Field(default="application/pdf")
    language: Optional[str] = Field(default="en")
    data: Optional[str] = Field(None, description="Base64 encoded data")
    url: Optional[str] = Field(None, description="Uri where the data can be found")
    title: Optional[str] = None
    creation: Optional[str] = None


class Narrative(BaseModel):
    status: str = Field(default="generated", description="generated | extensions | additional | empty")
    div: str = Field(..., description="Limited xhtml content")


# ============================================================================
# Core FHIR R4 Resources
# ============================================================================

class FHIRPatient(BaseModel):
    resourceType: str = "Patient"
    id: str = Field(default_factory=lambda: f"pat-{uuid.uuid4().hex[:8]}")
    identifier: List[Identifier] = Field(default_factory=list)
    active: bool = True
    name: Optional[List[Dict[str, Any]]] = None
    gender: Optional[str] = Field(None, description="male | female | other | unknown")
    birthDate: Optional[str] = None


class FHIREncounter(BaseModel):
    resourceType: str = "Encounter"
    id: str = Field(default_factory=lambda: f"enc-{uuid.uuid4().hex[:8]}")
    status: str = Field(default="finished", description="planned | arrived | triaged | in-progress | onleave | finished | cancelled")
    class_: Coding = Field(
        default_factory=lambda: Coding(system="http://terminology.hl7.org/CodeSystem/v3-ActCode", code="AMB", display="ambulatory"),
        alias="class"
    )
    subject: Reference
    period: Optional[Period] = None
    serviceProvider: Optional[Reference] = None


class FHIRCondition(BaseModel):
    resourceType: str = "Condition"
    id: str = Field(default_factory=lambda: f"cond-{uuid.uuid4().hex[:8]}")
    clinicalStatus: Optional[CodeableConcept] = Field(
        default_factory=lambda: CodeableConcept(
            coding=[Coding(system="http://terminology.hl7.org/CodeSystem/condition-clinical", code="active", display="Active")]
        )
    )
    verificationStatus: Optional[CodeableConcept] = Field(
        default_factory=lambda: CodeableConcept(
            coding=[Coding(system="http://terminology.hl7.org/CodeSystem/condition-ver-status", code="provisional", display="Provisional")]
        )
    )
    code: CodeableConcept
    subject: Reference
    recordedDate: Optional[str] = None


class FHIRObservation(BaseModel):
    resourceType: str = "Observation"
    id: str = Field(default_factory=lambda: f"obs-{uuid.uuid4().hex[:8]}")
    status: str = Field(default="final", description="registered | preliminary | final | amended")
    code: CodeableConcept
    subject: Reference
    effectiveDateTime: Optional[str] = None
    valueString: Optional[str] = None
    valueQuantity: Optional[Dict[str, Any]] = None
    interpretation: Optional[List[CodeableConcept]] = None
    referenceRange: Optional[List[Dict[str, Any]]] = None


class FHIRMedicationStatement(BaseModel):
    resourceType: str = "MedicationStatement"
    id: str = Field(default_factory=lambda: f"med-{uuid.uuid4().hex[:8]}")
    status: str = Field(default="active", description="active | completed | entered-in-error | intended | stopped | on-hold")
    medicationCodeableConcept: CodeableConcept
    subject: Reference
    effectiveDateTime: Optional[str] = None
    dosage: Optional[List[Dict[str, Any]]] = None


class FHIRDiagnosticReport(BaseModel):
    resourceType: str = "DiagnosticReport"
    id: str = Field(default_factory=lambda: f"dr-{uuid.uuid4().hex[:8]}")
    status: str = Field(default="final", description="registered | partial | preliminary | final")
    code: CodeableConcept
    subject: Reference
    effectiveDateTime: Optional[str] = None
    result: List[Reference] = Field(default_factory=list, description="Observations that are part of this report")
    conclusion: Optional[str] = None


class FHIRDocumentReference(BaseModel):
    resourceType: str = "DocumentReference"
    id: str = Field(default_factory=lambda: f"docref-{uuid.uuid4().hex[:8]}")
    status: str = Field(default="current", description="current | superseded | entered-in-error")
    docStatus: Optional[str] = Field(default="final", description="preliminary | final | amended | entered-in-error")
    type: CodeableConcept
    subject: Reference
    date: Optional[str] = None
    content: List[Dict[str, Any]] = Field(default_factory=list, description="Attachment content")


class FHIRCompositionSection(BaseModel):
    title: str
    code: Optional[CodeableConcept] = None
    text: Optional[Narrative] = None
    entry: List[Reference] = Field(default_factory=list)


class FHIRComposition(BaseModel):
    """
    ABDM OPConsultRecord Root Composition resource.
    Must be the FIRST resource (entry[0]) in the FHIR document Bundle.
    """
    resourceType: str = "Composition"
    id: str = Field(default_factory=lambda: f"comp-{uuid.uuid4().hex[:8]}")
    status: str = Field(default="final", description="preliminary | final | amended | entered-in-error")
    type: CodeableConcept = Field(
        default_factory=lambda: CodeableConcept(
            coding=[Coding(system="http://snomed.info/sct", code="371530004", display="Clinical consultation report")],
            text="OP Consultation Record"
        )
    )
    subject: Reference
    encounter: Reference
    date: str
    author: List[Reference] = Field(default_factory=list)
    title: str = "Outpatient Consultation Intake Record"
    section: List[FHIRCompositionSection] = Field(default_factory=list)


# ============================================================================
# Document Bundle Envelope
# ============================================================================

class FHIRBundleEntry(BaseModel):
    fullUrl: str = Field(..., description="Unique URN or URL for the entry e.g. urn:uuid:...")
    resource: Union[
        FHIRComposition,
        FHIRPatient,
        FHIREncounter,
        FHIRCondition,
        FHIRObservation,
        FHIRMedicationStatement,
        FHIRDiagnosticReport,
        FHIRDocumentReference,
        Dict[str, Any]
    ]


class FHIRBundle(BaseModel):
    """
    HL7 FHIR R4 Document Bundle.
    Per ABDM specifications:
      - bundle.type must be 'document'
      - bundle.entry[0].resource must be 'Composition'
    """
    resourceType: str = "Bundle"
    id: str = Field(default_factory=lambda: f"bundle-{uuid.uuid4().hex}")
    identifier: Optional[Identifier] = None
    type: str = "document"
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    entry: List[FHIRBundleEntry] = Field(default_factory=list)
