import logging
from typing import Dict, Any, Optional, Tuple, List
from fastapi import status

from app.models.core import PatientDataObject
from app.models.delivery import DeliveryRecord, DeliveryState, DeliveryTarget
from app.services.consent_engine import consent_engine
from app.services.fhir.bundle_builder import FHIRBundleBuilder
from app.services.fhir.validator import fhir_validator
from app.services.fhir.fhir_types import FHIRBundle
from app.services.delivery.mock_adapter import mock_delivery_adapter
from app.services.delivery.abdm_sandbox_adapter import abdm_sandbox_adapter
from app.services.delivery.his_adapter import his_adapter
from app.repositories.session_repository import session_repo
from app.repositories.document_repository import document_repo
from app.middleware.error_handler import MediKioskException

logger = logging.getLogger("delivery_service")


class DeliveryService:
    """
    Module D Orchestrator: Coordinates consent enforcement, clinician review gates,
    FHIR R4 document bundle packaging, multi-adapter dispatch, and DPDP-compliant
    ephemeral session data cleanup upon confirmed delivery.
    """
    def __init__(self):
        # In-memory audit receipt log for completed/purged sessions
        self._audit_receipts: Dict[str, DeliveryRecord] = {}

    def prepare_bundle(self, session: PatientDataObject) -> Tuple[FHIRBundle, List[str]]:
        """
        Prepare and validate a FHIR R4 Document Bundle without dispatching.
        Enforces:
          1. Consent Gate: Scope 'HIS_SHARE' must be GRANTED.
          2. Clinician Review Gate: Draft must be ACCEPTED or AMENDED.
        """
        session_id = session.identity.session_id

        # 1. Enforce HIS_SHARE consent
        consent_engine.enforce_consent(
            session=session,
            scope="HIS_SHARE",
            message="Consent to share clinical records with hospital/ABDM ('HIS_SHARE') has not been granted."
        )

        # 2. Enforce Clinician Review Gate
        summary_data = session.summary or {}
        draft_status = summary_data.get("draft_status", "PENDING")
        if draft_status not in ("ACCEPTED", "AMENDED"):
            raise MediKioskException(
                error_code="CLINICIAN_REVIEW_REQUIRED",
                message=f"Clinical summary draft must be reviewed and ACCEPTED or AMENDED by clinician before external delivery (current status: '{draft_status}').",
                status_code=status.HTTP_400_BAD_REQUEST,
                retry_guidance="Have attending physician approve the intake draft via /summary/review before delivery."
            )

        # 3. Build FHIR R4 Bundle
        bundle = FHIRBundleBuilder.build_document_bundle(session)

        # 4. Validate Bundle
        is_valid, issues = fhir_validator.validate_bundle(bundle)
        if not is_valid:
            logger.warning(f"FHIR Bundle validation issues for session {session_id}: {issues}")

        # Record prepared state
        session.integration_status = {
            "state": DeliveryState.PREPARED.value,
            "bundle_id": bundle.id,
            "total_entries": len(bundle.entry),
            "validation_issues": issues
        }
        session_repo.save_session(session)

        return bundle, issues

    async def submit_delivery(
        self,
        session: PatientDataObject,
        target: str = "MOCK"
    ) -> DeliveryRecord:
        """
        Submit validated FHIR R4 bundle to the designated external target.
        Handles post-submission lifecycle:
          - If ACCEPTED: Purge ephemeral session data from kiosk (DPDP Act).
          - If FAILED: Retain minimal error state for clinician inspection/retry.
        """
        session_id = session.identity.session_id

        # Prepare bundle (enforces consent and review gates)
        bundle, _ = self.prepare_bundle(session)
        bundle_dict = bundle.model_dump(by_alias=True)

        # Select adapter
        norm_target = target.upper()
        if norm_target == DeliveryTarget.ABDM_SANDBOX.value:
            adapter = abdm_sandbox_adapter
        elif norm_target == DeliveryTarget.HOSPITAL_HIS.value:
            adapter = his_adapter
        else:
            adapter = mock_delivery_adapter

        # Execute submission
        record = await adapter.submit_bundle(bundle_dict, session_id)

        # Store in audit receipt store
        self._audit_receipts[session_id] = record
        self._audit_receipts[record.delivery_id] = record

        # Post-submission lifecycle
        if record.state == DeliveryState.ACCEPTED:
            logger.info(f"Delivery {record.delivery_id} ACCEPTED. Executing DPDP post-delivery cleanup for session {session_id}.")
            
            # 1. Clear staged document bytes & extractions from repository
            document_repo.clear_session(session_id)

            # 2. Clear ephemeral session data from session repository
            session_repo.delete_session(session_id)

        else:
            logger.warning(f"Delivery {record.delivery_id} {record.state}. Preserving session state for retry.")
            session.integration_status = record.model_dump()
            session_repo.save_session(session)

        return record

    def get_delivery_status(self, session_id: str) -> Optional[DeliveryRecord]:
        """Retrieve delivery receipt for active or completed sessions."""
        # Check active session first
        session = session_repo.get_session(session_id)
        if session and session.integration_status:
            try:
                return DeliveryRecord(**session.integration_status)
            except Exception:
                pass

        # Check audit receipt store (for post-purged sessions)
        return self._audit_receipts.get(session_id)


delivery_service = DeliveryService()
