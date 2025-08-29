from typing import Optional, List

from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy import func

from src.models.prescription import Prescription
from src.models.prescription import PrescriptionItem


class PrescriptionRepository:
    def __init__(self, db: Session):
        self.db = db

    # -------- Prescription --------
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

    def get_all_prescriptions(self, skip: int, limit: int) -> List[Prescription]:
        """Lấy danh sách Prescription với phân trang"""
        return (
            self.db.query(Prescription)
            .order_by(Prescription.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_prescription_by_id(self, prescription_id: UUID) -> Optional[Prescription]:
        """Lấy Prescription theo ID"""
        return (
            self.db.query(Prescription)
            .filter(Prescription.prescription_id == prescription_id)
            .first()
        )

    def create_prescription(self, prescription: Prescription, items: List[PrescriptionItem]) -> Prescription:
        """Tạo Prescription cùng các PrescriptionItem con"""
        self.db.add(prescription)
        self.db.flush()  # để có prescription_id

        for item in items or []:
            item.prescription_id = prescription.prescription_id
            self.db.add(item)

        self.db.commit()
        self.db.refresh(prescription)
        return prescription


    def update_prescription(self, prescription: Prescription) -> Prescription:
        self.db.commit()
        self.db.refresh(prescription)
        return prescription

    def cancel_prescription(self, prescription: Prescription, reason: str, canceled_by: UUID) -> Prescription:
        """Hủy Prescription"""
        prescription.status = "CANCELED"
        prescription.canceled_reason = reason
        prescription.canceled_by = canceled_by
        prescription.canceled_at = func.now()
        self.db.commit()
        self.db.refresh(prescription)
        return prescription

    # -------- PrescriptionItem --------

    def get_items_by_prescription_id(self, prescription_id: UUID) -> List[PrescriptionItem]:
        """Lấy tất cả item của 1 Prescription"""
        return (
            self.db.query(PrescriptionItem)
            .filter(PrescriptionItem.prescription_id == prescription_id)
            .all()
        )


    def add_item(self, prescription_id: UUID, item: PrescriptionItem) -> PrescriptionItem:
        """
        Thêm một item vào Prescription.
        """
        try:
            item.prescription_id = prescription_id
            self.db.add(item)
            self.db.commit()
            self.db.refresh(item)
            return item
        except SQLAlchemyError:
            self.db.rollback()
            raise

    def remove_item_by_id(self, prescription_id: UUID, item_id: UUID) -> int:
        """
        Xóa 1 item thuộc prescription_id. Trả về số dòng bị xóa (0 hoặc 1).
        Dùng delete theo filter để tránh vấn đề session state.
        """
        try:
            q = (
                self.db.query(PrescriptionItem)
                .filter(
                    PrescriptionItem.item_id == item_id,
                    PrescriptionItem.prescription_id == prescription_id,
                )
            )
            deleted = q.delete(synchronize_session=False)
            self.db.commit()
            return deleted
        except IntegrityError:
            self.db.rollback()
            # ném lại để service map sang 400
            raise
        except SQLAlchemyError:
            self.db.rollback()
            raise

    def count_prescriptions(self) -> int:
        """Đếm tổng số Prescription"""
        return self.db.query(func.count(Prescription.prescription_id)).scalar() or 0