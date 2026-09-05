"""
MediKiosk FHIR R4 & ABDM Integration Package.
Provides strongly-typed FHIR models, resource mapper, Composition-first Bundle builder,
and referential integrity validation.
"""
from app.services.fhir.fhir_types import (
    FHIRBundle, FHIRBundleEntry, FHIRComposition, FHIRCompositionSection,
    FHIRPatient, FHIREncounter, FHIRCondition, FHIRObservation,
    FHIRMedicationStatement, FHIRDiagnosticReport, FHIRDocumentReference,
    Reference, Identifier, CodeableConcept, Coding, Attachment, Narrative
)
from app.services.fhir.resource_mapper import FHIRResourceMapper
from app.services.fhir.bundle_builder import FHIRBundleBuilder
from app.services.fhir.validator import FHIRValidator, fhir_validator

__all__ = [
    "FHIRBundle",
    "FHIRBundleEntry",
    "FHIRComposition",
    "FHIRCompositionSection",
    "FHIRPatient",
    "FHIREncounter",
    "FHIRCondition",
    "FHIRObservation",
    "FHIRMedicationStatement",
    "FHIRDiagnosticReport",
    "FHIRDocumentReference",
    "Reference",
    "Identifier",
    "CodeableConcept",
    "Coding",
    "Attachment",
    "Narrative",
    "FHIRResourceMapper",
    "FHIRBundleBuilder",
    "FHIRValidator",
    "fhir_validator",
]
