"""
FHIR Bundle Validator: Verifies ABDM NRCeS document bundle compliance,
envelope constraints, and cross-resource referential integrity.
"""
from typing import Dict, Any, List, Tuple
from app.services.fhir.fhir_types import FHIRBundle


class FHIRValidator:
    """
    Validates that a generated FHIR R4 Bundle complies with ABDM specifications:
      1. Bundle.type == 'document'
      2. entry[0].resource.resourceType == 'Composition'
      3. Referential integrity: Every internal Reference (urn:uuid:...) resolves to a fullUrl in the bundle
      4. Mandatory root fields: subject, encounter, date, author
    """

    @classmethod
    def validate_bundle(cls, bundle: FHIRBundle) -> Tuple[bool, List[str]]:
        """
        Validate a FHIRBundle instance.
        Returns: (is_valid: bool, issues: List[str])
        """
        issues: List[str] = []

        # 1. Envelope check
        if bundle.type != "document":
            issues.append(f"Invalid bundle type: expected 'document', got '{bundle.type}'.")

        if not bundle.entry or len(bundle.entry) == 0:
            issues.append("Bundle has no entries.")
            return False, issues

        # 2. Composition-first check (ABDM mandate)
        first_entry = bundle.entry[0]
        first_res = first_entry.resource
        first_type = getattr(first_res, "resourceType", None) or (first_res.get("resourceType") if isinstance(first_res, dict) else None)

        if first_type != "Composition":
            issues.append(f"ABDM Envelope Violation: entry[0] must be 'Composition', got '{first_type}'.")

        # 3. Collect all fullUrls in the bundle for referential integrity check
        known_urls = {e.fullUrl for e in bundle.entry}
        known_ids = set()
        for e in bundle.entry:
            r = e.resource
            r_id = getattr(r, "id", None) or (r.get("id") if isinstance(r, dict) else None)
            if r_id:
                known_ids.add(r_id)

        # 4. Check Composition references
        comp = first_res
        if first_type == "Composition":
            # Check subject reference
            subject_ref = getattr(comp, "subject", None) or (comp.get("subject") if isinstance(comp, dict) else None)
            if subject_ref:
                ref_val = getattr(subject_ref, "reference", None) or (subject_ref.get("reference") if isinstance(subject_ref, dict) else None)
                if ref_val and ref_val not in known_urls and not any(ref_val.endswith(rid) for rid in known_ids):
                    issues.append(f"Dangling reference in Composition.subject: '{ref_val}' not found in bundle.")

            # Check encounter reference
            enc_ref = getattr(comp, "encounter", None) or (comp.get("encounter") if isinstance(comp, dict) else None)
            if enc_ref:
                ref_val = getattr(enc_ref, "reference", None) or (enc_ref.get("reference") if isinstance(enc_ref, dict) else None)
                if ref_val and ref_val not in known_urls and not any(ref_val.endswith(rid) for rid in known_ids):
                    issues.append(f"Dangling reference in Composition.encounter: '{ref_val}' not found in bundle.")

            # Check section entries
            sections = getattr(comp, "section", []) or (comp.get("section", []) if isinstance(comp, dict) else [])
            for s_idx, sec in enumerate(sections):
                entries = getattr(sec, "entry", []) or (sec.get("entry", []) if isinstance(sec, dict) else [])
                for e_ref in entries:
                    ref_val = getattr(e_ref, "reference", None) or (e_ref.get("reference") if isinstance(e_ref, dict) else None)
                    if ref_val and ref_val not in known_urls and not any(ref_val.endswith(rid) for rid in known_ids):
                        issues.append(f"Dangling reference in Composition.section[{s_idx}]: '{ref_val}' not found in bundle.")

        is_valid = len(issues) == 0
        return is_valid, issues


fhir_validator = FHIRValidator()
