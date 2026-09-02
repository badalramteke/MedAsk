import uuid
import hashlib
import json
from datetime import datetime
from typing import Dict, Any, Optional

from app.models.delivery import DeliveryRecord, DeliveryState, DeliveryTarget
from app.services.delivery.base_adapter import BaseDeliveryAdapter


class MockDeliveryAdapter(BaseDeliveryAdapter):
    """
    Deterministic simulated delivery adapter for local testing and CI.
    Always reports is_mock=True to maintain complete truthfulness per PHASES.md line 111.
    """
    def __init__(self):
        super().__init__(target=DeliveryTarget.MOCK)
        self._history: Dict[str, DeliveryRecord] = {}

    async def submit_bundle(self, bundle_dict: Dict[str, Any], session_id: str) -> DeliveryRecord:
        """Simulate consented hand-off to ABDM / Hospital HIS."""
        delivery_id = f"DELIV_MOCK_{uuid.uuid4().hex[:8].upper()}"
        bundle_id = bundle_dict.get("id", f"bundle-{session_id[:8]}")
        
        # Calculate bundle sha256
        bundle_str = json.dumps(bundle_dict, sort_keys=True)
        bundle_hash = hashlib.sha256(bundle_str.encode("utf-8")).hexdigest()
        total_entries = len(bundle_dict.get("entry", []))

        now = datetime.utcnow()
        record = DeliveryRecord(
            delivery_id=delivery_id,
            session_id=session_id,
            state=DeliveryState.ACCEPTED,
            target=DeliveryTarget.MOCK,
            is_mock=True,
            fhir_bundle_id=bundle_id,
            bundle_hash=bundle_hash,
            total_resources=total_entries,
            submitted_at=now,
            completed_at=now,
            response_payload={
                "status": "ACCEPTED",
                "abdm_transaction_id": f"TXN-MOCK-{uuid.uuid4().hex[:12]}",
                "care_context_reference": f"CARE-CTX-MOCK-{session_id[:8]}",
                "acknowledgement": "Consented FHIR document bundle accepted by mock HIS recipient.",
                "is_mock": True
            }
        )
        self._history[delivery_id] = record
        return record

    async def check_status(self, delivery_id: str) -> DeliveryRecord:
        """Retrieve delivery record."""
        return self._history.get(delivery_id) or DeliveryRecord(
            delivery_id=delivery_id,
            session_id="UNKNOWN",
            state=DeliveryState.FAILED,
            target=DeliveryTarget.MOCK,
            is_mock=True,
            error_message="Delivery ID not found in mock store."
        )


mock_delivery_adapter = MockDeliveryAdapter()
