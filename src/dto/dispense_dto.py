from pydantic import BaseModel
from typing import Optional, List
from decimal import Decimal
from datetime import datetime

class DispenseCreateDTO(BaseModel):
    prescription_id: id
    notes: Optional[str] = None
    created_by: Optional[UUID] = None

class DispenseLineCreateDTO(BaseModel):
    prescription_item_id: id
    quantity_dispensed: Decimal
    notes: Optional[str] = None

class DispenseCompleteDTO(BaseModel):
    dispensed_by: int

class DispenseLineResponseDTO(BaseModel):
    id: int
    prescription_item_id: int
    quantity_dispensed: Decimal
    notes: Optional[str]
    created_at: datetime
    class Config:
        from_attributes = True

class DispenseResponseDTO(BaseModel):
    id: int
    prescription_id: int
    status: str
    dispensed_at: Optional[datetime]
    dispensed_by: int
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    lines: List[DispenseLineResponseDTO]
    class Config:
        from_attributes = True
