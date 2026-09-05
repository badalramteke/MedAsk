from pydantic import BaseModel, Field
from typing import Any, List, Optional
from .provenance import Provenance

class JsonPatchOperation(BaseModel):
    op: str = Field(..., description="Operation type: 'add', 'remove', 'replace', 'move', 'copy', or 'test'")
    path: str = Field(..., description="JSON Pointer path")
    value: Optional[Any] = Field(None, description="Value to add, replace or test")

class PatientDataPatch(BaseModel):
    """
    Represents a version-aware patch to be applied to a PatientDataObject.
    """
    base_version: str = Field(..., description="The version of the PDO this patch expects to apply against.")
    operations: List[JsonPatchOperation] = Field(..., description="List of JSON Patch operations (RFC 6902)")
    patch_provenance: Provenance = Field(..., description="Provenance of the actor applying the patch.")
