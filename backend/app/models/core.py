from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime

from .identity import IdentityContext
from .consent import ConsentContext
from .history import PatientHistory
from .ayush import AyushHistory

class PluginOutput(BaseModel):
    schema_version: str
    data: Dict[str, Any]
    provenance: Dict[str, Any]

class PatientDataObject(BaseModel):
    """
    The canonical data contract for the MediKiosk intake workflow.
    """
    version: str = Field(default="1.0.0", description="Schema version")
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    
    identity: IdentityContext
    consent: ConsentContext
    history: Optional[PatientHistory] = None
    ayush: Optional[AyushHistory] = None
    
    # Other core fields to be expanded (documents, summary, alerts, integration)
    documents: Dict[str, Any] = Field(default_factory=dict)
    summary: Dict[str, Any] = Field(default_factory=dict)
    alerts: Dict[str, Any] = Field(default_factory=dict)
    integration_status: Dict[str, Any] = Field(default_factory=dict)
    
    plugin_outputs: Dict[str, PluginOutput] = Field(
        default_factory=dict, 
        description="Namespaced extension area for plugins."
    )
