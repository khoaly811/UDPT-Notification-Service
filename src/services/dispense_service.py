from uuid import UUID
from decimal import Decimal
from typing import List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.repositories.dispense_repository import DispenseRepository
from src.repositories.prescription_repository import PrescriptionRepository
from src.models.dispense import Dispense, DispenseLine
from src.dto.dispense_dto import (
    DispenseCreateDTO, DispenseLineCreateDTO, DispenseCompleteDTO,
    DispenseResponseDTO, DispenseLineResponseDTO
)
from src.messaging.rabbitmq_producer import RabbitMQProducer

class DispenseService:
    def __init__(self, db: Session):
        self.repo = DispenseRepository(db)
        self.prescription_repo = PrescriptionRepository(db)

    # 1) Tạo phiếu cấp phát (PENDING)
    def create_dispense(self, dto: DispenseCreateDTO) -> DispenseResponseDTO:
        pres = self.prescription_repo.get_prescription(dto.prescription_id)
        if not pres:
            raise HTTPException(status_code=404, detail="Prescription not found")
        if pres.status == "DISPENSED":
            raise HTTPException(status_code=400, detail=f"Cannot create dispense for prescription in status {pres.status}")

        entity = Dispense(
            prescription_id=dto.prescription_id,
            notes=dto.notes,
            # created_by=dto.created_by  # nếu cần
        )
        created = self.repo.create_dispense(entity)
        return self._to_dispense_response(created, [])

    # 2) Thêm dòng cấp phát vào phiếu PENDING
    def add_line(self, dispense_id: UUID, dto: DispenseLineCreateDTO) -> DispenseResponseDTO:
        dispense = self.repo.get_dispense(dispense_id)
        if not dispense:
            raise HTTPException(status_code=404, detail="Dispense not found")
        if dispense.status != "PENDING":
            raise HTTPException(status_code=400, detail="Only PENDING dispense can accept lines")

        # Kiểm tra prescription item hợp lệ & thuộc cùng prescription
        pi = self.prescription_repo.get_prescription_item(dto.prescription_item_id)
        if not pi:
            raise HTTPException(status_code=404, detail="Prescription item not found")
        if pi.prescription_id != dispense.prescription_id:
            raise HTTPException(status_code=400, detail="Prescription item does not belong to this prescription")

        if dto.quantity_dispensed <= 0:
            raise HTTPException(status_code=400, detail="quantity_dispensed must be > 0")

        # --- Option A: chặn vượt số lượng kê ngay khi add line ---
        already_completed = self.repo.sum_completed_dispensed_for_item(pi.item_id)              # đã phát ở các phiếu COMPLETED trước
        already_in_this   = self.repo.sum_lines_in_dispense_for_item(dispense.dispense_id, pi.item_id)  # đã thêm vào phiếu hiện tại
        total_after       = Decimal(already_completed) + Decimal(already_in_this) + Decimal(dto.quantity_dispensed)

        if total_after > pi.quantity_prescribed:
            raise HTTPException(
                status_code=400,
                detail=f"Dispensed total ({total_after}) exceeds prescribed ({pi.quantity_prescribed}) for this item"
            )

        # (tuỳ chọn) cảnh báo sớm tồn kho hiện tại – không trừ kho ở đây
        med = self.repo.get_medicine(pi.medication_id)
        if med and med.stock is not None and Decimal(med.stock) < Decimal(dto.quantity_dispensed):
            raise HTTPException(status_code=400, detail="Insufficient stock for this medicine at the moment")

        # Lưu line
        line = DispenseLine(
            dispense_id=dispense.dispense_id,
            prescription_item_id=pi.item_id,
            quantity_dispensed=dto.quantity_dispensed,
            notes=dto.notes
        )
        self.repo.add_line(line)

        # Trả về phiếu + các line hiện có
        lines = self.repo.get_lines_by_dispense(dispense.dispense_id)
        return self._to_dispense_response(dispense, lines)

    # def add_line_by_prescription(self, prescription_id: UUID, dto: DispenseLineCreateDTO) -> DispenseResponseDTO:
    #     # 1) đảm bảo prescription tồn tại & hợp lệ
    #     pres = self.prescription_repo.get_prescription(prescription_id)
    #     if not pres:
    #         raise HTTPException(status_code=404, detail="Prescription not found")
    #     if pres.status == "CANCELED":
    #         raise HTTPException(status_code=400, detail="Cannot add line for a canceled prescription")
    #
    #     # 2) lấy hoặc tạo phiếu PENDING
    #     dispense = self.repo.create_or_get_pending_dispense(prescription_id)
    #
    #     # 3) dùng lại toàn bộ validate của add_line (Option A – chặn vượt số kê + cảnh báo stock)
    #     # copy nguyên phần thân validate từ add_line(...) hiện có:
    #     pi = self.prescription_repo.get_prescription_item(dto.prescription_item_id)
    #     if not pi:
    #         raise HTTPException(status_code=404, detail="Prescription item not found")
    #     if pi.prescription_id != dispense.prescription_id:
    #         raise HTTPException(status_code=400, detail="Prescription item does not belong to this prescription")
    #     if dto.quantity_dispensed <= 0:
    #         raise HTTPException(status_code=400, detail="quantity_dispensed must be > 0")
    #
    #     already_completed = self.repo.sum_completed_dispensed_for_item(pi.item_id)
    #     already_in_this = self.repo.sum_lines_in_dispense_for_item(dispense.dispense_id, pi.item_id)
    #     total_after = Decimal(already_completed) + Decimal(already_in_this) + Decimal(dto.quantity_dispensed)
    #     if total_after > pi.quantity_prescribed:
    #         raise HTTPException(
    #             status_code=400,
    #             detail=f"Dispensed total ({total_after}) exceeds prescribed ({pi.quantity_prescribed}) for this item"
    #         )
    #
    #     med = self.repo.get_medicine(pi.medication_id)
    #     if med and med.stock is not None and Decimal(med.stock) < Decimal(dto.quantity_dispensed):
    #         raise HTTPException(status_code=400, detail="Insufficient stock for this medicine at the moment")
    #
    #     line = DispenseLine(
    #         dispense_id=dispense.dispense_id,
    #         prescription_item_id=pi.item_id,
    #         quantity_dispensed=dto.quantity_dispensed,
    #         lot_number=dto.lot_number,
    #         expiry_date=dto.expiry_date,
    #         notes=dto.notes
    #     )
    #     self.repo.add_line(line)
    #
    #     lines = self.repo.get_lines_by_dispense(dispense.dispense_id)
    #     return self._to_dispense_response(dispense, lines)
    # 3) Hoàn tất phiếu (COMPLETED) và cập nhật prescription nếu đã phát đủ
    def complete(self, dispense_id: UUID, dto: DispenseCompleteDTO) -> DispenseResponseDTO:
        dispense = self.repo.get_dispense(dispense_id)
        if not dispense:
            raise HTTPException(status_code=404, detail="Dispense not found")
        if dispense.status != "PENDING":
            raise HTTPException(status_code=400, detail="Only PENDING dispense can be completed")

        lines = self.repo.get_lines_by_dispense(dispense.dispense_id)
        if not lines:
            raise HTTPException(status_code=400, detail="Cannot complete an empty dispense")

        # ❶ Kiểm tra & trừ kho cho tất cả lines trong phiếu (atomic trong cùng session)
        try:
            self.repo.bulk_check_and_decrement_stock_for_dispense(dispense.dispense_id)
        except Exception as e:
            # có thể map sang HTTP 400 nếu thiếu kho
            raise HTTPException(status_code=400, detail=str(e))

        # ❷ Set COMPLETED + log người phát
        completed = self.repo.complete_dispense(dispense, dto.dispensed_by)

        # ❸ Nếu đơn đã phát đủ hết -> set prescription = DISPENSED
        pres = self.prescription_repo.get_prescription(dispense.prescription_id)
        if self._is_prescription_fully_dispensed(pres.prescription_id):
            self.prescription_repo.set_prescription_status(pres, "DISPENSED")
        elif self._is_prescription_partially_dispensed(pres.prescription_id):
            self.prescription_repo.set_prescription_status(pres, "PARTIALLY_DISPENSED")

        # ❹ Commit một lần để đảm bảo tất cả thay đổi (trừ kho + completed + status đơn)
        self.repo.commit()

        try:
            producer = RabbitMQProducer()
            producer.publish({
                "event": "prescription_ready",
                "prescription_id": str(dispense.prescription_id),
                "dispense_id": str(dispense.dispense_id),
                "patient_id": str(pres.patient_id),
                "status": "READY"
            })
            producer.close()
        except Exception as e:
            # log thôi, không break flow chính
            print(f"⚠️ RabbitMQ publish failed: {e}")

        final_lines = self.repo.get_lines_by_dispense(dispense.dispense_id)
        return self._to_dispense_response(completed, final_lines)


    # 4) Detail
    def get_dispense(self, dispense_id: UUID) -> DispenseResponseDTO:
        dispense = self.repo.get_dispense(dispense_id)
        if not dispense:
            raise HTTPException(status_code=404, detail="Dispense not found")
        lines = self.repo.get_lines_by_dispense(dispense.dispense_id)
        return self._to_dispense_response(dispense, lines)

    # def complete_pending_by_prescription(self, prescription_id: UUID, dto: DispenseCompleteDTO) -> DispenseResponseDTO:
    #     pres = self.prescription_repo.get_prescription(prescription_id)
    #     if not pres:
    #         raise HTTPException(status_code=404, detail="Prescription not found")
    #
    #     dispense = self.repo.get_pending_dispense_by_prescription(prescription_id)
    #     if not dispense:
    #         raise HTTPException(status_code=400, detail="No PENDING dispense for this prescription")
    #
    #     return self.complete(dispense.dispense_id, dto)
    # ---- Helpers ----
    def _is_prescription_fully_dispensed(self, prescription_id: UUID) -> bool:
        items = self.prescription_repo.get_prescription_items(prescription_id)
        if not items:
            return False
        for it in items:
            completed_qty = self.repo.sum_completed_dispensed_for_item(it.item_id)
            if Decimal(completed_qty) < Decimal(it.quantity_prescribed):
                return False
        return True

    def _is_prescription_partially_dispensed(self, prescription_id: UUID) -> bool:
        items=self.prescription_repo.get_prescription_items(prescription_id)
        if not items:
            return False
        any_dispensed = False
        all_fully = True
        for it in items:
            completed_qty = self.repo.sum_completed_dispensed_for_item(it.item_id)
            if Decimal(completed_qty) > 0:
                any_dispensed = True
            if Decimal(completed_qty) < Decimal(it.quantity_prescribed):
                all_fully = False

        return any_dispensed and not all_fully

    def _to_dispense_response(self, dispense: Dispense, lines: List[DispenseLine]) -> DispenseResponseDTO:
        line_dtos = [DispenseLineResponseDTO.model_validate(l) for l in lines]
        return DispenseResponseDTO(
            dispense_id=dispense.dispense_id,
            prescription_id=dispense.prescription_id,
            status=dispense.status,
            dispensed_at=dispense.dispensed_at,
            dispensed_by=dispense.dispensed_by,
            notes=dispense.notes,
            created_at=dispense.created_at,
            updated_at=dispense.updated_at,
            lines=line_dtos
        )
