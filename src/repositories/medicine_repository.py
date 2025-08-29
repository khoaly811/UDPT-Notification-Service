from typing import Optional, List

from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy import func

from src.models.medicine import Medicine


class MedicineRepository:
    def __init__(self, db: Session):
        self.db = db

    # -------- Medicine --------

    def get_all_medicines(self, skip: int, limit: int) -> List[Medicine]:
        """Lấy danh sách Medicine với phân trang"""
        return (
            self.db.query(Medicine)
            .order_by(Medicine.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_medicine_by_id(self, medicine_id: int) -> Optional[Medicine]:
        """Lấy Medicine theo ID"""
        return (
            self.db.query(Medicine)
            .filter(Medicine.medication_id == medicine_id)
            .first()
        )

    def create_medicine(self, medicine: Medicine) -> Medicine:
        """Tạo mới một Medicine"""
        try:
            self.db.add(medicine)
            self.db.commit()
            self.db.refresh(medicine)
            return medicine
        except SQLAlchemyError:
            self.db.rollback()
            raise

    def update_medicine(self, medicine: Medicine) -> Medicine:
        """Cập nhật Medicine"""
        try:
            self.db.commit()
            self.db.refresh(medicine)
            return medicine
        except SQLAlchemyError:
            self.db.rollback()
            raise

    def delete_medicine(self, medicine: Medicine) -> None:
        """Xóa cứng 1 record medicine"""
        try:
            self.db.delete(medicine)
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise
        except SQLAlchemyError:
            self.db.rollback()
            raise

    def count_medicines(self) -> int:
        """Đếm tổng số Medicine"""
        return self.db.query(func.count(Medicine.medication_id)).scalar() or 0
