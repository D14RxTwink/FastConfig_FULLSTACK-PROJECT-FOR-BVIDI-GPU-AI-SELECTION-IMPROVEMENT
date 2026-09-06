from pydantic import BaseModel, ConfigDict
from typing import Optional

class ArchitectureSchema(BaseModel):
    id: int
    family_name: str
    architecture: str
    generation_series: str

    model_config = ConfigDict(from_attributes=True)

class GpuSchema(BaseModel):
    id: int
    full_name: str
    vram_gb: int
    memory_type: Optional[str] = None
    bus_width_bits: Optional[int] = None
    architecture_id: Optional[int] = None
    
    for_games: bool
    for_3d: bool
    for_ml: bool
    for_office: bool
    budget_tier: str

    arch_info: Optional[ArchitectureSchema] = None

    model_config = ConfigDict(from_attributes=True)