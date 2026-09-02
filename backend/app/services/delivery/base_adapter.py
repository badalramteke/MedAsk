from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from app.models.delivery import DeliveryRecord, DeliveryTarget


class BaseDeliveryAdapter(ABC):
    """
    Abstract Base Class for external delivery adapters.
    Follows identical pattern as BaseSpeechAdapter and BaseOCRAdapter.
    """
    def __init__(self, target: DeliveryTarget):
        self.target = target

    @abstractmethod
    async def submit_bundle(self, bundle_dict: Dict[str, Any], session_id: str) -> DeliveryRecord:
        """Submit validated FHIR R4 Bundle to the target integration."""
        ...

    @abstractmethod
    async def check_status(self, delivery_id: str) -> DeliveryRecord:
        """Query delivery status from the integration target."""
        ...
