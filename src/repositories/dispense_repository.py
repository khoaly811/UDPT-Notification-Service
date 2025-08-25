from typing import List, Optional
from uuid import UUID
from decimal import Decimal
from collections import defaultdict

from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError

from src.models.dispense import Dispense, DispenseLine
from src.models.prescription import Prescription, PrescriptionItem
from src.models.medicine import Medicine

class DispenseRepository:
    def __init__(self, db: Session):
        self.db = db

    # -------- Prescription helpers --------
    def get_prescription(self, prescription_id: UUID) -> Optional[Prescription]:
        return (
            self.db.query(Prescription)
            .filter(Prescription.prescription_id == prescription_id)
            .first()
        )

    def get_prescription_item(self, item_id: UUID) -> Optional[PrescriptionItem]:
        return (
            self.db.query(PrescriptionItem)
            .filter(PrescriptionItem.item_id == item_id)
            .first()
        )

    def get_prescription_items(self, prescription_id: UUID) -> List[PrescriptionItem]:
        return (
            self.db.query(PrescriptionItem)
            .filter(PrescriptionItem.prescription_id == prescription_id)
            .all()
        )

    def set_prescription_status(self, prescription: Prescription, status_value: str) -> None:
        prescription.status = status_value
        self.db.add(prescription)

    # -------- Dispense --------
    def create_dispense(self, entity: Dispense) -> Dispense:
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        return entity

    def get_dispense(self, dispense_id: UUID) -> Optional[Dispense]:
        return (
            self.db.query(Dispense)
            .filter(Dispense.dispense_id == dispense_id)
            .first()
        )

    def add_line(self, line: DispenseLine) -> DispenseLine:
        self.db.add(line)
        self.db.commit()
        self.db.refresh(line)
        return line

    def get_lines_by_dispense(self, dispense_id: UUID) -> List[DispenseLine]:
        return (
            self.db.query(DispenseLine)
            .filter(DispenseLine.dispense_id == dispense_id)
            .all()
        )

    def complete_dispense(self, dispense: Dispense, dispensed_by: UUID) -> Dispense:
        dispense.status = "COMPLETED"
        dispense.dispensed_by = dispensed_by
        dispense.dispensed_at = func.now()
        self.db.add(dispense)
        self.db.flush()
        return dispense

    # -------- Stock --------
    def bulk_check_and_decrement_stock_for_dispense(self, dispense_id: UUID):
        lines = self.get_lines_by_dispense(dispense_id)
        if not lines:
            return

        # lấy PrescriptionItem map theo item_id
        pi_map = {pi.item_id: pi for pi in self.db.query(PrescriptionItem).filter(
            PrescriptionItem.item_id.in_([l.prescription_item_id for l in lines])
        ).all()}

        need_by_med = defaultdict(Decimal)
        for l in lines:
            pi = pi_map.get(l.prescription_item_id)
            if not pi:
                raise SQLAlchemyError("PrescriptionItem not found during stock calculation")
            need_by_med[pi.medication_id] += Decimal(l.quantity_dispensed)

        meds = self.db.query(Medicine).filter(Medicine.medication_id.in_(list(need_by_med.keys()))).with_for_update().all()
        med_map = {m.medication_id: m for m in meds}

        # check stock
        for med_id, need_qty in need_by_med.items():
            med = med_map.get(med_id)
            if not med:
                raise SQLAlchemyError(f"Medicine {med_id} not found")
            current = Decimal(med.stock or 0)
            if current < need_qty:
                raise SQLAlchemyError(f"Not enough stock for medicine {med_id}: have {current}, need {need_qty}")

        # decrement
        for med_id, need_qty in need_by_med.items():
            med = med_map[med_id]
            med.stock = Decimal(med.stock or 0) - need_qty
            self.db.add(med)

    def sum_completed_dispensed_for_item(self, prescription_item_id: UUID) -> Decimal:
        """
        Tổng số lượng đã phát (chỉ tính các phiếu COMPLETED) cho 1 prescription_item.
        """
        total = (
            self.db.query(func.coalesce(func.sum(DispenseLine.quantity_dispensed), 0))
            .join(Dispense, DispenseLine.dispense_id == Dispense.dispense_id)
            .filter(
                DispenseLine.prescription_item_id == prescription_item_id,
                Dispense.status == "COMPLETED",
            )
            .scalar()
        )
        return Decimal(total or 0)

    def sum_lines_in_dispense_for_item(self, dispense_id: UUID, prescription_item_id: UUID) -> Decimal:
        """
        Tổng số lượng của cùng item đã thêm VÀO CHÍNH PHIẾU NÀY (PENDING).
        """
        total = (
            self.db.query(func.coalesce(func.sum(DispenseLine.quantity_dispensed), 0))
            .filter(
                DispenseLine.dispense_id == dispense_id,
                DispenseLine.prescription_item_id == prescription_item_id,
            )
            .scalar()
        )
        return Decimal(total or 0)
    def commit(self):
        self.db.commit()
