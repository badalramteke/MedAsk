import os
import uuid
import hashlib
import json
import logging
from datetime import datetime
from typing import Dict, Any
import httpx

from app.models.delivery import DeliveryRecord, DeliveryState, DeliveryTarget
from app.services.delivery.base_adapter import BaseDeliveryAdapter

logger = logging.getLogger("his_adapter")


class HISAdapter(BaseDeliveryAdapter):
    """
    Direct hospital EMR / HIS webhook delivery adapter.
    Dispatches consented FHIR R4 bundles to configured hospital endpoints.
    """
    def __init__(self):
        super().__init__(target=DeliveryTarget.HOSPITAL_HIS)
        self.endpoint_url = os.getenv("HIS_ENDPOINT_URL", "")
        self.api_key = os.getenv("HIS_API_KEY", "")

    @property
    def is_configured(self) -> bool:
        return bool(self.endpoint_url)

    async def submit_bundle(self, bundle_dict: Dict[str, Any], session_id: str) -> DeliveryRecord:
        """Submit FHIR bundle to hospital EMR endpoint."""
        delivery_id = f"DELIV_HIS_{uuid.uuid4().hex[:8].upper()}"
        bundle_id = bundle_dict.get("id", f"bundle-{session_id[:8]}")
        bundle_str = json.dumps(bundle_dict, sort_keys=True)
        bundle_hash = hashlib.sha256(bundle_str.encode("utf-8")).hexdigest()
        total_entries = len(bundle_dict.get("entry", []))
        now = datetime.utcnow()

        if not self.is_configured:
            return DeliveryRecord(
                delivery_id=delivery_id,
                session_id=session_id,
                state=DeliveryState.FAILED,
                target=DeliveryTarget.HOSPITAL_HIS,
                is_mock=False,
                fhir_bundle_id=bundle_id,
                bundle_hash=bundle_hash,
                total_resources=total_entries,
                submitted_at=now,
                completed_at=now,
                error_message="HIS_ENDPOINT_URL not configured in environment."
            )

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                headers = {
                    "Content-Type": "application/fhir+json",
                    "X-MediKiosk-Session": session_id,
                    "X-Api-Key": self.api_key
                }
                resp = await client.post(self.endpoint_url, json=bundle_dict, headers=headers)
                
                if resp.status_code in (200, 201, 202):
                    return DeliveryRecord(
                        delivery_id=delivery_id,
                        session_id=session_id,
                        state=DeliveryState.ACCEPTED,
                        target=DeliveryTarget.HOSPITAL_HIS,
                        is_mock=False,
                        fhir_bundle_id=bundle_id,
                        bundle_hash=bundle_hash,
                        total_resources=total_entries,
                        submitted_at=now,
                        completed_at=datetime.utcnow(),
                        response_payload={"status_code": resp.status_code, "his_receipt": resp.text[:200]}
                    )
                else:
                    return DeliveryRecord(
                        delivery_id=delivery_id,
                        session_id=session_id,
                        state=DeliveryState.REJECTED,
                        target=DeliveryTarget.HOSPITAL_HIS,
                        is_mock=False,
                        fhir_bundle_id=bundle_id,
                        bundle_hash=bundle_hash,
                        total_resources=total_entries,
                        submitted_at=now,
                        completed_at=datetime.utcnow(),
                        error_message=f"Hospital HIS returned HTTP {resp.status_code}: {resp.text[:200]}"
                    )
        except Exception as e:
            logger.error(f"Hospital HIS delivery error: {e}")
            return DeliveryRecord(
                delivery_id=delivery_id,
                session_id=session_id,
                state=DeliveryState.FAILED,
                target=DeliveryTarget.HOSPITAL_HIS,
                is_mock=False,
                fhir_bundle_id=bundle_id,
                bundle_hash=bundle_hash,
                total_resources=total_entries,
                submitted_at=now,
                completed_at=datetime.utcnow(),
                error_message=f"Network error contacting Hospital HIS: {str(e)}"
            )

    async def check_status(self, delivery_id: str) -> DeliveryRecord:
        return DeliveryRecord(
            delivery_id=delivery_id,
            session_id="UNKNOWN",
            state=DeliveryState.FAILED,
            target=DeliveryTarget.HOSPITAL_HIS,
            is_mock=False,
            error_message="Status query not supported on generic HIS adapter."
        )


his_adapter = HISAdapter()
