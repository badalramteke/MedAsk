from pydantic import BaseModel, Field, model_validator
from datetime import datetime
from typing import Optional, Literal, Dict, Any
from enum import Enum


class ConsentScopeEnum(str, Enum):
    INTAKE = "INTAKE"
    DOCUMENTS = "DOCUMENTS"
    SUMMARY = "SUMMARY"
    HIS_SHARE = "HIS_SHARE"


class ConsentStatusEnum(str, Enum):
    GRANTED = "GRANTED"
    REVOKED = "REVOKED"
    PENDING = "PENDING"
    EXPIRED = "EXPIRED"


class ScopeConsentDetail(BaseModel):
    """
    Granular audit tracking for an individual consent scope.
    """
    scope: str = Field(..., description="INTAKE | DOCUMENTS | SUMMARY | HIS_SHARE")
    status: str = Field(default="PENDING", description="GRANTED | REVOKED | PENDING | EXPIRED")
    granted_at: Optional[datetime] = None
    revoked_at: Optional[datetime] = None
    interaction_mode: str = Field(default="TOUCH_SCREEN", description="TOUCH_SCREEN | VOICE_CONFIRMED")
    evidence_reference: Optional[str] = None
    policy_version: str = Field(default="v1.0", description="DPDP policy version presented to patient")


class ConsentContext(BaseModel):
    """
    Manages consent scopes and lifecycle for the session.
    Supports both legacy composite scopes (for backward compatibility)
    and granular 4-scope DPDP architecture (Phase 9 Module D).
    """
    scope: str = Field(
        default="INTAKE_AND_SUMMARY",
        description="Active composite or primary scope (e.g. INTAKE_AND_SUMMARY, DOCUMENTS_PROCESSING, FULL_HIS_SHARE, INTAKE, HIS_SHARE)"
    )
    status: str = Field(
        default="GRANTED",
        description="Overall session consent status (GRANTED | REVOKED | PENDING | EXPIRED)"
    )
    evidence_reference: Optional[str] = Field(
        None, description="Reference to signed document, digital signature, or audit log."
    )
    granted_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = Field(None)
    
    # Phase 9: Multi-Scope Granular Map
    scopes: Dict[str, ScopeConsentDetail] = Field(
        default_factory=dict,
        description="Detailed per-scope status map (INTAKE, DOCUMENTS, SUMMARY, HIS_SHARE)"
    )

    @model_validator(mode="after")
    def sync_granular_scopes(self) -> "ConsentContext":
        """
        Synchronize granular scope map with top-level scope/status if empty.
        Ensures 100% backward compatibility with existing tests and fixtures.
        """
        if not self.scopes:
            now = self.granted_at or datetime.utcnow()
            ev_ref = self.evidence_reference or "DEFAULT_CONSENT_REF"
            
            # Default all to pending first
            for s in [ConsentScopeEnum.INTAKE.value, ConsentScopeEnum.DOCUMENTS.value, ConsentScopeEnum.SUMMARY.value, ConsentScopeEnum.HIS_SHARE.value]:
                self.scopes[s] = ScopeConsentDetail(
                    scope=s,
                    status=ConsentStatusEnum.PENDING.value,
                    evidence_reference=ev_ref
                )

            # Map legacy composite scope to granular scopes
            if self.status == "GRANTED":
                if self.scope in ("FULL_HIS_SHARE", "HIS_SHARE"):
                    for s in [ConsentScopeEnum.INTAKE.value, ConsentScopeEnum.DOCUMENTS.value, ConsentScopeEnum.SUMMARY.value, ConsentScopeEnum.HIS_SHARE.value]:
                        self.scopes[s].status = "GRANTED"
                        self.scopes[s].granted_at = now
                elif self.scope in ("INTAKE_AND_SUMMARY",):
                    self.scopes[ConsentScopeEnum.INTAKE.value].status = "GRANTED"
                    self.scopes[ConsentScopeEnum.INTAKE.value].granted_at = now
                    self.scopes[ConsentScopeEnum.SUMMARY.value].status = "GRANTED"
                    self.scopes[ConsentScopeEnum.SUMMARY.value].granted_at = now
                elif self.scope in ("DOCUMENTS_PROCESSING", "DOCUMENTS"):
                    self.scopes[ConsentScopeEnum.DOCUMENTS.value].status = "GRANTED"
                    self.scopes[ConsentScopeEnum.DOCUMENTS.value].granted_at = now
                elif self.scope in ("INTAKE_ONLY", "INTAKE"):
                    self.scopes[ConsentScopeEnum.INTAKE.value].status = "GRANTED"
                    self.scopes[ConsentScopeEnum.INTAKE.value].granted_at = now
            elif self.status == "REVOKED":
                for s in self.scopes.values():
                    s.status = "REVOKED"
                    s.revoked_at = now

        return self

    def is_scope_granted(self, scope_name: str) -> bool:
        """Check if a specific granular scope is currently GRANTED."""
        norm_scope = scope_name.upper()
        # Direct check on granular map
        if norm_scope in self.scopes:
            return self.scopes[norm_scope].status == "GRANTED"
        
        # Legacy fallback checks
        if self.status != "GRANTED":
            return False
        if self.scope == "FULL_HIS_SHARE":
            return True
        if norm_scope == "DOCUMENTS" and self.scope in ("DOCUMENTS_PROCESSING", "FULL_HIS_SHARE"):
            return True
        if norm_scope in ("INTAKE", "SUMMARY") and self.scope in ("INTAKE_AND_SUMMARY", "FULL_HIS_SHARE"):
            return True
        if norm_scope == "HIS_SHARE" and self.scope == "FULL_HIS_SHARE":
            return True
        return False
