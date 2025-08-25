from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List
from uuid import UUID

from src.repositories.prescription_repository import PrescriptionRepository
from src.models.prescription import Prescription
from src.models.prescription import PrescriptionItem
from src.dto.pagination_dto import PaginatedResponseDTO, PaginationRequestDTO
from src.dto.prescription_dto import (
    PrescriptionCreateDTO,
    PrescriptionResponseDTO,
    PrescriptionItemResponseDTO,
    PrescriptionListItemDTO,
    PrescriptionUpdateDTO,
    PrescriptionItemAddDTO,     # bạn đã xác nhận DTO ok
    CancelPrescriptionDTO,      # bạn đã xác nhận DTO ok
)


class PrescriptionService:
    def __init__(self, db: Session):
        self.repository = PrescriptionRepository(db)

        # ---------------- Helpers ----------------
    def _to_response(self, prescription: Prescription) -> PrescriptionResponseDTO:
        items_in_db = self.repository.get_items_by_prescription_id(prescription.prescription_id)
        item_dtos = [PrescriptionItemResponseDTO.model_validate(it) for it in items_in_db]
        return PrescriptionResponseDTO(
            prescription_id=prescription.prescription_id,
            prescription_code=prescription.prescription_code,
            patient_id=prescription.patient_id,
            doctor_id=prescription.doctor_id,
            status=prescription.status,
            valid_from=prescription.valid_from,
            valid_to=prescription.valid_to,
            notes=prescription.notes,
            created_at=prescription.created_at,
            updated_at=prescription.updated_at,
            items=item_dtos
        )
    def create_prescription(self, data: PrescriptionCreateDTO) -> PrescriptionResponseDTO:
        """Tạo mới một đơn thuốc cùng các item"""
        if not data.items or len(data.items) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Prescription must have at least one item"
            )

        # Tạo prescription entity
        prescription = Prescription(
            patient_id=data.patient_id,
            doctor_id=data.doctor_id,
            valid_from=data.valid_from,
            valid_to=data.valid_to,
            notes=data.notes,
            status="CREATED",
        )

        # Tạo các prescription item
        items = [
            PrescriptionItem(
                medication_id=item.medication_id,
                quantity_prescribed=item.quantity_prescribed,
                unit_prescribed=item.unit_prescribed,
                dose=item.dose,
                frequency=item.frequency,
                duration=item.duration,
                notes=item.notes,
            )
            for item in data.items
        ]
        # Lưu vào DB
        created = self.repository.create_prescription(prescription, items)
        return self._to_response(created)

    def get_prescription_by_id(self, prescription_id: UUID) -> PrescriptionResponseDTO:
        prescription = self.repository.get_prescription_by_id(prescription_id)
        if not prescription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Prescription with id {prescription_id} not found"
            )
        return self._to_response(prescription)

    def list_prescriptions(self, pagination: PaginationRequestDTO) -> PaginatedResponseDTO[PrescriptionListItemDTO]:
        skip = pagination.calc_skip()
        rows = self.repository.get_all_prescriptions(skip=skip, limit=pagination.page_size)
        total = self.repository.count_prescriptions()
        data = [PrescriptionListItemDTO.model_validate(r) for r in rows]
        return PaginatedResponseDTO.create(
            data=data,
            page=pagination.page,
            page_size=pagination.page_size,
            total=total
        )

    def update_prescription(self, prescription_id: UUID, data: PrescriptionUpdateDTO) -> PrescriptionResponseDTO:
        prescription = self.repository.get_prescription_by_id(prescription_id)
        if not prescription:
            raise HTTPException(status_code=404, detail="Prescription not found")
        if prescription.status == "CANCELED":
            raise HTTPException(status_code=400, detail="Cannot edit a canceled prescription")

        # Mutate các field cho phép
        if data.valid_from is not None:
            prescription.valid_from = data.valid_from
        if data.valid_to is not None:
            prescription.valid_to = data.valid_to
        if data.notes is not None:
            prescription.notes = data.notes

        prescription.status = "UPDATED"
        updated = self.repository.update_prescription(prescription)
        return self._to_response(updated)

    def add_item(self, prescription_id: UUID, dto: PrescriptionItemAddDTO) -> PrescriptionResponseDTO:
        prescription = self.repository.get_prescription_by_id(prescription_id)
        if not prescription:
            raise HTTPException(status_code=404, detail="Prescription not found")
        if prescription.status == "CANCELED":
            raise HTTPException(status_code=400, detail="Cannot add item to a canceled prescription")

        item = PrescriptionItem(
            medication_id=dto.medication_id,
            quantity_prescribed=dto.quantity_prescribed,
            unit_prescribed=dto.unit_prescribed,
            dose=dto.dose,
            frequency=dto.frequency,
            duration=dto.duration,
            notes=dto.notes,
        )
        self.repository.add_item(prescription_id, item)
        return self.get_prescription_by_id(prescription_id)

    def remove_item(self, prescription_id: UUID, item_id: UUID) -> PrescriptionResponseDTO:
        prescription = self.repository.get_prescription_by_id(prescription_id)
        if not prescription:
            raise HTTPException(status_code=404, detail="Prescription not found")
        if prescription.status == "CANCELED":
            raise HTTPException(status_code=400, detail="Cannot remove item from a canceled prescription")

        # kiểm tra tồn tại (để trả 404 đúng nghĩa)
        item = self.repository.get_item_by_id(item_id)
        if not item or item.prescription_id != prescription_id:
            raise HTTPException(status_code=404, detail="Prescription item not found")

        try:
            deleted = self.repository.remove_item_by_id(prescription_id, item_id)
        except IntegrityError as e:
            # Trường hợp dính ràng buộc (ví dụ sau này có dispense_line tham chiếu)
            raise HTTPException(status_code=400, detail="Cannot remove item due to related records") from e

        if deleted == 0:
            # Không xóa được vì không match filter
            raise HTTPException(status_code=404, detail="Prescription item not found")

        # Optionally đánh dấu prescription đã cập nhật
        prescription.status = "UPDATED"
        self.repository.update_prescription(prescription)

        # trả lại chi tiết đơn sau khi xóa
        return self.get_prescription_by_id(prescription_id)

    def cancel_prescription(self, prescription_id: UUID, data: CancelPrescriptionDTO) -> PrescriptionResponseDTO:
        prescription = self.repository.get_prescription_by_id(prescription_id)
        if not prescription:
            raise HTTPException(status_code=404, detail="Prescription not found")
        if prescription.status == "CANCELED":
            return self._to_response(prescription)

        canceled = self.repository.cancel_prescription(
            prescription,
            reason=data.reason,
            canceled_by=data.canceled_by
        )
        return self._to_response(canceled)