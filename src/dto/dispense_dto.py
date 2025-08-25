from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from decimal import Decimal
from datetime import datetime

class DispenseCreateDTO(BaseModel):
    prescription_id: UUID
    notes: Optional[str] = None
    created_by: Optional[UUID] = None

class DispenseLineCreateDTO(BaseModel):
    prescription_item_id: UUID
    quantity_dispensed: Decimal
    lot_number: Optional[str] = None
    expiry_date: Optional[datetime] = None
    notes: Optional[str] = None

class DispenseCompleteDTO(BaseModel):
    dispensed_by: UUID

class DispenseLineResponseDTO(BaseModel):
    line_id: UUID
    prescription_item_id: UUID
    quantity_dispensed: Decimal
    lot_number: Optional[str]
    expiry_date: Optional[datetime]
    notes: Optional[str]
    created_at: datetime
    class Config:
        from_attributes = True

class DispenseResponseDTO(BaseModel):
    dispense_id: UUID
    prescription_id: UUID
    status: str
    dispensed_at: Optional[datetime]
    dispensed_by: Optional[UUID]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    lines: List[DispenseLineResponseDTO]
    class Config:
        from_attributes = True
