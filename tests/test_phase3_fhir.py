import json
import unittest
from pathlib import Path

# Allowed FHIR R4 resource types in Phase 3
ALLOWED_RESOURCE_TYPES = {
    "Patient",
    "Encounter",
    "Condition",
    "Observation",
    "MedicationStatement",
    "DocumentReference",
    "Consent"
}


class TestPhase3FHIR(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Load mock_fhir_bundles.json from test fixtures directory."""
        possible_paths = [
            Path(__file__).parent / "fixtures" / "mock_fhir_bundles.json",
            Path("tests/fixtures/mock_fhir_bundles.json"),
            Path("MedAsk/tests/fixtures/mock_fhir_bundles.json")
        ]
        
        cls.fixture_path = None
        for p in possible_paths:
            if p.is_file():
                cls.fixture_path = p
                break

        if cls.fixture_path is None:
            raise FileNotFoundError(f"mock_fhir_bundles.json not found in expected paths: {possible_paths}")
        
        with open(cls.fixture_path, "r", encoding="utf-8") as f:
            cls.fhir_fixture_data = json.load(f)

    def test_01_json_structure_and_top_level_schema(self):
        """Verify top-level metadata and schema attributes."""
        data = self.fhir_fixture_data
        self.assertIsInstance(data, dict, "Top-level JSON structure must be an object")
        self.assertEqual(data.get("schema_version"), "1.0.0", "schema_version must be '1.0.0'")
        self.assertEqual(data.get("dataset_id"), "mock_fhir_bundles", "dataset_id must be 'mock_fhir_bundles'")
        self.assertEqual(data.get("fhir_version"), "4.0.1", "fhir_version must be '4.0.1'")
        self.assertIs(data.get("synthetic"), True, "synthetic must be True")
        self.assertIn("bundles", data, "Top-level JSON must contain 'bundles' key")
        self.assertIsInstance(data["bundles"], list, "'bundles' must be a list")
        self.assertGreaterEqual(len(data["bundles"]), 4, "Must contain at least 4 FHIR bundle scenarios")

    def test_02_bundle_uniqueness(self):
        """Ensure all bundle_ids are unique across the dataset."""
        bundle_ids = [b.get("bundle_id") for b in self.fhir_fixture_data["bundles"]]
        self.assertEqual(len(bundle_ids), len(set(bundle_ids)), f"Duplicate bundle_id found in: {bundle_ids}")

    def test_03_bundle_and_resource_types(self):
        """Verify every bundle is a valid FHIR Bundle and all entries contain allowed resource types."""
        for bundle in self.fhir_fixture_data["bundles"]:
            bundle_id = bundle.get("bundle_id", "UNKNOWN")
            self.assertEqual(bundle.get("resourceType"), "Bundle", f"Bundle {bundle_id} resourceType must be 'Bundle'")
            self.assertEqual(bundle.get("type"), "collection", f"Bundle {bundle_id} type must be 'collection'")
            
            entries = bundle.get("entry", [])
            self.assertGreater(len(entries), 0, f"Bundle {bundle_id} entry list cannot be empty")

            for idx, entry in enumerate(entries):
                resource = entry.get("resource", {})
                resource_type = resource.get("resourceType")
                self.assertIsNotNone(resource_type, f"Missing resourceType at index {idx} in Bundle {bundle_id}")
                self.assertIn(
                    resource_type,
                    ALLOWED_RESOURCE_TYPES,
                    f"Invalid resourceType '{resource_type}' at index {idx} in Bundle {bundle_id}. "
                    f"Expected one of {ALLOWED_RESOURCE_TYPES}"
                )

    def test_04_resource_id_uniqueness_within_bundles(self):
        """Ensure no duplicate resource IDs exist within any single bundle."""
        for bundle in self.fhir_fixture_data["bundles"]:
            bundle_id = bundle.get("bundle_id", "UNKNOWN")
            resource_ids = set()
            full_urls = set()

            for entry in bundle.get("entry", []):
                full_url = entry.get("fullUrl")
                if full_url:
                    self.assertNotIn(full_url, full_urls, f"Duplicate fullUrl '{full_url}' in Bundle {bundle_id}")
                    full_urls.add(full_url)

                resource = entry.get("resource", {})
                res_id = resource.get("id")
                if res_id:
                    self.assertNotIn(res_id, resource_ids, f"Duplicate resource id '{res_id}' in Bundle {bundle_id}")
                    resource_ids.add(res_id)

    def test_05_referential_integrity(self):
        """Verify all internal references (subject, patient, encounter) resolve within the same bundle."""
        for bundle in self.fhir_fixture_data["bundles"]:
            bundle_id = bundle.get("bundle_id", "UNKNOWN")
            
            valid_targets = set()
            for entry in bundle.get("entry", []):
                full_url = entry.get("fullUrl")
                if full_url:
                    valid_targets.add(full_url)
                
                res = entry.get("resource", {})
                res_type = res.get("resourceType")
                res_id = res.get("id")
                if res_type and res_id:
                    valid_targets.add(f"{res_type}/{res_id}")
                    valid_targets.add(res_id)

            references_to_check = []
            def find_references(obj):
                if isinstance(obj, dict):
                    for k, v in obj.items():
                        if k == "reference" and isinstance(v, str):
                            references_to_check.append(v)
                        else:
                            find_references(v)
                elif isinstance(obj, list):
                    for item in obj:
                        find_references(item)

            for entry in bundle.get("entry", []):
                find_references(entry.get("resource", {}))

            for ref in references_to_check:
                self.assertIn(
                    ref,
                    valid_targets,
                    f"Broken reference '{ref}' in Bundle '{bundle_id}'. "
                    f"Valid targets in bundle: {sorted(list(valid_targets))}"
                )


if __name__ == "__main__":
    unittest.main()
