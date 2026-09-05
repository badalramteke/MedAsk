from pydantic import BaseModel, Field
from typing import Optional, List
from .provenance import Provenance

class DashavidhaPariksha(BaseModel):
    """
    Ten-fold Ayurvedic assessment (Dashavidha Pariksha).
    Value codes correspond to ayush_dashavidha_pariksha.json.
    """
    prakriti: Optional[str] = Field(None, description="E.g., PRAKRITI_VATA_PRADHANA, PRAKRITI_VATA_PITTA")
    vikriti: List[str] = Field(default_factory=list, description="E.g., VIKRITI_VATA_VRIDDHI, VIKRITI_DHATU_DUSHTI")
    sara: Optional[str] = Field(None, description="Tissue excellence")
    samhanana: Optional[str] = Field(None, description="Compactness of the body")
    pramana: Optional[str] = Field(None, description="Body proportions")
    satmya: Optional[str] = Field(None, description="Adaptability / Habituation")
    sattva: Optional[str] = Field(None, description="Psychological constitution")
    ahara_shakti: Optional[str] = Field(None, description="Digestive capacity")
    vyayama_shakti: Optional[str] = Field(None, description="Exercise capacity")
    vaya: Optional[str] = Field(None, description="Age/Aging factor")
    provenance: Optional[Provenance] = None

class AyushHistory(BaseModel):
    """
    Container for all AYUSH-related intake structured data.
    """
    dashavidha: Optional[DashavidhaPariksha] = None
    # Future extension points for Ashtavidha, Trividha, etc.
