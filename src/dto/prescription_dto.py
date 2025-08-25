from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from uuid import UUID
from decimal import Decimal

# ---------- Request DTOs ----------
class PrescriptionItemCreateDTO(BaseModel):
    medication_id: UUID
    quantity_prescribed: Decimal
    unit_prescribed: Optional[str] = None
    dose: Optional[str] = None
    frequency: Optional[str] = None
    duration: Optional[str] = None
    notes: Optional[str] = None

class PrescriptionCreateDTO(BaseModel):
    patient_id: UUID
    doctor_id: UUID
    valid_from: datetime
    valid_to: Optional[datetime] = None
    notes: Optional[str] = None
    items: List[PrescriptionItemCreateDTO]

class PrescriptionUpdateDTO(BaseModel):
    # KHÔNG sửa items ở đây để tránh nhập nhằng
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
    notes: Optional[str] = None

# Dùng cho endpoint thêm 1 thuốc vào đơn (có thể tái dùng PrescriptionItemCreateDTO)
class PrescriptionItemAddDTO(BaseModel):
    medication_id: UUID
    quantity_prescribed: Decimal
    unit_prescribed: Optional[str] = None
    dose: Optional[str] = None
    frequency: Optional[str] = None
    duration: Optional[str] = None
    notes: Optional[str] = None

# Hủy đơn
class CancelPrescriptionDTO(BaseModel):
    reason: str
    canceled_by: UUID

# ---------- Response DTOs ----------
class PrescriptionItemResponseDTO(BaseModel):
    item_id: UUID
    medication_id: UUID
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
    prescription_id: UUID
    prescription_code: Optional[str]
    patient_id: UUID
    doctor_id: UUID
    status: str                        # <-- thêm trường này
    valid_from: datetime
    valid_to: Optional[datetime]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    items: List[PrescriptionItemResponseDTO]

    class Config:
        from_attributes = True

class PrescriptionListItemDTO(BaseModel):
    prescription_id: UUID
    prescription_code: Optional[str]
    patient_id: UUID
    doctor_id: UUID
    status: str
    valid_from: datetime
    valid_to: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
