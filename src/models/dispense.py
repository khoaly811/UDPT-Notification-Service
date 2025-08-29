from sqlalchemy import Column, Text, DateTime, ForeignKey, Numeric, Integer
from sqlalchemy.sql import func
from config import Base

class Dispense(Base):
    __tablename__ = "dispense"
    __table_args__ = {"schema": "medication"}

    id = Column(Integer, primary_key=True)
    prescription_id = Column(Integer,
                             ForeignKey("medication.prescription.id"),
                             nullable=False)

    status = Column(Text, nullable=False, default="PENDING")  # 'PENDING' | 'COMPLETED'
    dispensed_at = Column(DateTime, nullable=True)
    dispensed_by = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)

    def __repr__(self):
        return f"<Dispense(id={self.id}, prescription_id={self.prescription_id}, status={self.status})>"


class DispenseLine(Base):
    __tablename__ = "dispense_line"
    __table_args__ = {"schema": "medication"}

    id = Column(Integer, primary_key=True)
    dispense_id = Column(Integer,
                         ForeignKey("medication.dispense.id"),
                         nullable=False)
    prescription_item_id = Column(Integer,
                                  ForeignKey("medication.prescription_item.id"),
                                  nullable=False)

    quantity_dispensed = Column(Numeric(14, 3), nullable=False)
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime, nullable=False, server_default=func.now())

    def __repr__(self):
        return f"<DispenseLine(id={self.id}, dispense_id={self.dispense_id}, item_id={self.prescription_item_id})>"