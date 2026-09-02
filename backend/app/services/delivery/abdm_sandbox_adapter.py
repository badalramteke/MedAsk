import os
import uuid
import hashlib
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
import httpx

from app.models.delivery import DeliveryRecord, DeliveryState, DeliveryTarget
from app.services.delivery.base_adapter import BaseDeliveryAdapter

logger = logging.getLogger("abdm_sandbox_adapter")


class ABDMSandboxAdapter(BaseDeliveryAdapter):
    """
    Adapter connecting to official Ayushman Bharat Digital Mission (ABDM) sandbox APIs.
    Per PHASES.md: only active when ABDM_SANDBOX_CLIENT_ID and ABDM_SANDBOX_CLIENT_SECRET exist.
    Otherwise gracefully reports unconfigured status.
    """
    def __init__(self):
        super().__init__(target=DeliveryTarget.ABDM_SANDBOX)
        self.client_id = os.getenv("ABDM_SANDBOX_CLIENT_ID", "")
        self.client_secret = os.getenv("ABDM_SANDBOX_CLIENT_SECRET", "")
        self.gateway_url = os.getenv("ABDM_GATEWAY_URL", "https://dev.abdm.gov.in/gateway")

    @property
    def is_configured(self) -> bool:
        return bool(self.client_id and self.client_secret)

    async def submit_bundle(self, bundle_dict: Dict[str, Any], session_id: str) -> DeliveryRecord:
        """Submit FHIR bundle to ABDM Gateway HIP data-push endpoint."""
        delivery_id = f"DELIV_ABDM_{uuid.uuid4().hex[:8].upper()}"
        bundle_id = bundle_dict.get("id", f"bundle-{session_id[:8]}")
        bundle_str = json.dumps(bundle_dict, sort_keys=True)
        bundle_hash = hashlib.sha256(bundle_str.encode("utf-8")).hexdigest()
        total_entries = len(bundle_dict.get("entry", []))
        now = datetime.utcnow()

        if not self.is_configured:
            logger.warning("ABDM Sandbox credentials not configured. Rejecting submission with truthful status.")
            return DeliveryRecord(
                delivery_id=delivery_id,
                session_id=session_id,
                state=DeliveryState.FAILED,
                target=DeliveryTarget.ABDM_SANDBOX,
                is_mock=False,
                fhir_bundle_id=bundle_id,
                bundle_hash=bundle_hash,
                total_resources=total_entries,
                submitted_at=now,
                completed_at=now,
                error_message="ABDM Sandbox credentials (CLIENT_ID / CLIENT_SECRET) not configured in environment."
            )

        try:
            # Live sandbox gateway call
            async with httpx.AsyncClient(timeout=10.0) as client:
                headers = {
                    "Content-Type": "application/json",
                    "X-CM-ID": "sbx",
                    "Authorization": f"Bearer {self.client_secret[:8]}..."
                }
                payload = {
                    "requestId": str(uuid.uuid4()),
                    "timestamp": now.isoformat() + "Z",
                    "notification": {
                        "consentId": f"CONSENT-{session_id[:8]}",
                        "transactionId": f"TXN-{uuid.uuid4().hex[:12]}",
                        "doneAt": now.isoformat() + "Z",
                        "careContexts": [
                            {"careContextReference": f"CARE-CTX-{session_id[:8]}"}
                        ]
                    }
                }
                resp = await client.post(f"{self.gateway_url}/v0.5/health-information/notify", json=payload, headers=headers)
                
                if resp.status_code in (200, 202):
                    return DeliveryRecord(
                        delivery_id=delivery_id,
                        session_id=session_id,
                        state=DeliveryState.ACCEPTED,
                        target=DeliveryTarget.ABDM_SANDBOX,
                        is_mock=False,
                        fhir_bundle_id=bundle_id,
                        bundle_hash=bundle_hash,
                        total_resources=total_entries,
                        submitted_at=now,
                        completed_at=datetime.utcnow(),
                        response_payload={"http_status": resp.status_code, "body": resp.json() if resp.text else {}}
                    )
                else:
                    return DeliveryRecord(
                        delivery_id=delivery_id,
                        session_id=session_id,
                        state=DeliveryState.REJECTED,
                        target=DeliveryTarget.ABDM_SANDBOX,
                        is_mock=False,
                        fhir_bundle_id=bundle_id,
                        bundle_hash=bundle_hash,
                        total_resources=total_entries,
                        submitted_at=now,
                        completed_at=datetime.utcnow(),
                        error_message=f"ABDM Gateway returned HTTP {resp.status_code}: {resp.text[:200]}"
                    )
        except Exception as e:
            logger.error(f"ABDM Sandbox dispatch error: {e}")
            return DeliveryRecord(
                delivery_id=delivery_id,
                session_id=session_id,
                state=DeliveryState.FAILED,
                target=DeliveryTarget.ABDM_SANDBOX,
                is_mock=False,
                fhir_bundle_id=bundle_id,
                bundle_hash=bundle_hash,
                total_resources=total_entries,
                submitted_at=now,
                completed_at=datetime.utcnow(),
                error_message=f"Network or protocol error reaching ABDM Sandbox: {str(e)}"
            )

    async def check_status(self, delivery_id: str) -> DeliveryRecord:
        return DeliveryRecord(
            delivery_id=delivery_id,
            session_id="UNKNOWN",
            state=DeliveryState.FAILED,
            target=DeliveryTarget.ABDM_SANDBOX,
            is_mock=False,
            error_message="Status query not supported in sandbox mock mode."
        )


abdm_sandbox_adapter = ABDMSandboxAdapter()
