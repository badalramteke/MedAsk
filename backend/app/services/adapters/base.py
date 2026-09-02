from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from app.models.ai import ModelTaskRequest, ModelTaskResponse


class BaseModelAdapter(ABC):
    """
    Abstract Base Class for all AI Model Providers.
    Ensures capability-based routing and standardized error/latency handling.
    """
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    async def generate_structured(self, request: ModelTaskRequest, system_prompt: str) -> ModelTaskResponse:
        """Execute a text-based or structured generation task."""
        pass

    @abstractmethod
    async def generate_multimodal(self, request: ModelTaskRequest, system_prompt: str) -> ModelTaskResponse:
        """Execute a multimodal image analysis task."""
        pass

    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Verify connectivity and readiness of the provider."""
        pass
