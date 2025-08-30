from sqlalchemy import Column, String, Date, Text, Integer, ForeignKey, Numeric, Boolean, DateTime
from sqlalchemy.sql import func
from config import Base

# Prescription (Đơn thuốc)
class Prescription(Base):
    __tablename__ = "prescription"
    __table_args__ = {"schema": "medication"}

    prescription_id = Column(Integer, primary_key=True, index=True)
    prescription_code = Column(Text, unique=True, nullable=True)

    appointment_id = Column(Integer, nullable=False)

    status = Column(Text, nullable=False, default="CREATED")

    valid_from = Column(DateTime, nullable=False, server_default=func.now())
    valid_to = Column(DateTime, nullable=True)

    notes = Column(Text, nullable=True)

    created_at = Column(DateTime, nullable=False, server_default=func.now())
    created_by = Column(Integer, nullable=True)

    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    updated_by = Column(Integer, nullable=True)

    canceled_at = Column(DateTime, nullable=True)
    canceled_by = Column(Integer, nullable=True)
    canceled_reason = Column(Text, nullable=True)

    def __repr__(self):
        return f"<Prescription(id={self.prescription_id}, appointment={self.appointment_id})>"


# PrescriptionItem (Chi tiết đơn thuốc)
class PrescriptionItem(Base):
    __tablename__ = "prescription_item"
    __table_args__ = {"schema": "medication"}

    item_id = Column(Integer, primary_key=True)
    prescription_id = Column(Integer,
                             ForeignKey("medication.prescription.prescription_id"),
                             nullable=False)
    medication_id = Column(Integer,
                         ForeignKey("medication.medicine.medication_id"),
                         nullable=False)

    quantity_prescribed = Column(Numeric(14, 3), nullable=False)
    unit_prescribed = Column(Text, nullable=True)
    dose = Column(Text, nullable=True)
    frequency = Column(Text, nullable=True)
    duration = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<PrescriptionItem(id={self.item_id}, prescription_id={self.prescription_id}, medication_id={self.medication_id})>"