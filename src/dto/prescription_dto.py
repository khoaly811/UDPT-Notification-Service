from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from decimal import Decimal


# ---------- Request DTOs ----------
class PrescriptionItemCreateDTO(BaseModel):
    medication_id: int
    quantity_prescribed: Decimal
    unit_prescribed: Optional[str] = None
    dose: Optional[str] = None
    frequency: Optional[str] = None
    duration: Optional[str] = None
    notes: Optional[str] = None


class PrescriptionCreateDTO(BaseModel):
    appointment_id: int
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
    notes: Optional[str] = None
    created_by: Optional[int] = None
    items: List[PrescriptionItemCreateDTO]


class PrescriptionUpdateDTO(BaseModel):
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
    notes: Optional[str] = None
    updated_by: Optional[int] = None


# Dùng cho endpoint thêm 1 thuốc vào đơn
class PrescriptionItemAddDTO(BaseModel):
    medication_id: int
    quantity_prescribed: Decimal
    unit_prescribed: Optional[str] = None
    dose: Optional[str] = None
    frequency: Optional[str] = None
    duration: Optional[str] = None
    notes: Optional[str] = None


# Hủy đơn
class CancelPrescriptionDTO(BaseModel):
    reason: str
    canceled_by: int


# ---------- Response DTOs ----------
class PrescriptionItemResponseDTO(BaseModel):
    item_id: int
    medication_id: int
    quantity_prescribed: Decimal
    unit_prescribed: Optional[str]
    dose: Optional[str]
    frequency: Optional[str]
    duration: Optional[str]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PrescriptionResponseDTO(BaseModel):
    prescription_id: int
    prescription_code: Optional[str]
    appointment_id: int
    status: str
    valid_from: datetime
    valid_to: Optional[datetime]
    notes: Optional[str]
    created_at: datetime
    created_by: Optional[int]
    updated_at: datetime
    updated_by: Optional[int]
    canceled_at: Optional[datetime]
    canceled_by: Optional[int]
    canceled_reason: Optional[str]
    items: List[PrescriptionItemResponseDTO]

    class Config:
        from_attributes = True


class PrescriptionListItemDTO(BaseModel):
    prescription_id: int
    prescription_code: Optional[str]
    appointment_id: int
    status: str
    valid_from: datetime
    valid_to: Optional[datetime]
    created_at: datetime
    created_by: Optional[int]
    updated_at: datetime
    updated_by: Optional[int]

    class Config:
        from_attributes = True
