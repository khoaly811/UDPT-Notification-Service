from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from uuid import UUID

from src.repositories.medicine_repository import MedicineRepository
from src.models.medicine import Medicine
from src.dto.pagination_dto import PaginatedResponseDTO, PaginationRequestDTO
from src.dto.medicine_dto import (
    MedicineCreateDTO,
    MedicineResponseDTO,
    MedicineListItemDTO,
    MedicineUpdateDTO,
)


class MedicineService:
    def __init__(self, db: Session):
        self.repository = MedicineRepository(db)

    # ---------------- Helpers ----------------
    def _to_response(self, medicine: Medicine) -> MedicineResponseDTO:
        return MedicineResponseDTO.model_validate(medicine)

    # ---------------- CREATE ----------------
    def create_medicine(self, data: MedicineCreateDTO) -> MedicineResponseDTO:
        medicine = Medicine(
            atc_code=data.atc_code,
            medicine_name=data.medicine_name,
            generic_name=data.generic_name,
            form=data.form,
            strength=data.strength,
            unit=data.unit,
            stock=data.stock,
            is_active=True,
        )
        created = self.repository.create_medicine(medicine)
        return self._to_response(created)

    # ---------------- DETAIL ----------------
    def get_medicine_by_id(self, medicine_id: UUID) -> MedicineResponseDTO:
        medicine = self.repository.get_medicine_by_id(medicine_id)
        if not medicine:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Medicine with id {medicine_id} not found"
            )
        return self._to_response(medicine)

    # ---------------- LIST ----------------
    def list_medicines(self, pagination: PaginationRequestDTO) -> PaginatedResponseDTO[MedicineListItemDTO]:
        skip = pagination.calc_skip()
        rows = self.repository.get_all_medicines(skip=skip, limit=pagination.page_size)
        total = self.repository.count_medicines()
        data = [MedicineListItemDTO.model_validate(r) for r in rows]
        return PaginatedResponseDTO.create(
            data=data,
            page=pagination.page,
            page_size=pagination.page_size,
            total=total
        )

    # ---------------- UPDATE ----------------
    def update_medicine(self, medicine_id: UUID, data: MedicineUpdateDTO) -> MedicineResponseDTO:
        medicine = self.repository.get_medicine_by_id(medicine_id)
        if not medicine:
            raise HTTPException(status_code=404, detail="Medicine not found")

        if data.atc_code is not None:
            medicine.atc_code = data.atc_code
        if data.medicine_name is not None:
            medicine.medicine_name = data.medicine_name
        if data.generic_name is not None:
            medicine.generic_name = data.generic_name
        if data.form is not None:
            medicine.form = data.form
        if data.strength is not None:
            medicine.strength = data.strength
        if data.unit is not None:
            medicine.unit = data.unit
        if data.stock is not None:
            medicine.stock = data.stock
        if data.is_active is not None:
            medicine.is_active = data.is_active

        updated = self.repository.update_medicine(medicine)
        return self._to_response(updated)

    # ---------------- DELETE / DEACTIVATE ----------------
    def delete_medicine(self, medicine_id: UUID) -> MedicineResponseDTO:
        medicine = self.repository.get_medicine_by_id(medicine_id)
        if not medicine:
            raise HTTPException(status_code=404, detail="Medicine not found")

        # Ở đây có thể "hard delete" hoặc "soft delete" (deactivate)
        # Mình chọn soft delete: set is_active = False
        medicine.is_active = False
        updated = self.repository.update_medicine(medicine)
        return self._to_response(updated)
