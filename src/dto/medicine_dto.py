from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal


# ---------------- CREATE DTO ----------------
class MedicineCreateDTO(BaseModel):
    atc_code: Optional[str] = Field(None, description="ATC code if applicable")
    medicine_name: str = Field(..., description="Commercial/Display name")
    generic_name: Optional[str] = Field(None, description="Active ingredient name")
    form: Optional[str] = Field(None, description="Dosage form (tablet, capsule, syrup,...)")
    strength: Optional[str] = Field(None, description="Strength (e.g., 500 mg)")
    unit: Optional[str] = Field(None, description="Common measurement unit (e.g., mg, ml)")
    stock: Decimal = Field(0, ge=0, description="Available stock")
    expiry_date: Optional[datetime] = Field(None, description="Expiry date of the medicine")


# ---------------- UPDATE DTO ----------------
class MedicineUpdateDTO(BaseModel):
    atc_code: Optional[str] = None
    medicine_name: Optional[str] = None
    generic_name: Optional[str] = None
    form: Optional[str] = None
    strength: Optional[str] = None
    unit: Optional[str] = None
    stock: Optional[Decimal] = Field(None, ge=0)
    is_active: Optional[bool] = None
    expiry_date: Optional[datetime] = None


# ---------------- LIST ITEM DTO ----------------
class MedicineListItemDTO(BaseModel):
    medication_id: int
    medicine_name: str
    generic_name: Optional[str]
    form: Optional[str]
    strength: Optional[str]
    unit: Optional[str]
    stock: Decimal
    is_active: bool
    expiry_date: Optional[datetime]

    class Config:
        from_attributes = True  # cho SQLAlchemy ORM


# ---------------- RESPONSE DTO ----------------
class MedicineResponseDTO(BaseModel):
    medication_id: int
    atc_code: Optional[str]
    medicine_name: str
    generic_name: Optional[str]
    form: Optional[str]
    strength: Optional[str]
    unit: Optional[str]
    stock: Decimal
    is_active: bool
    expiry_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # map trực tiếp từ SQLAlchemy model
