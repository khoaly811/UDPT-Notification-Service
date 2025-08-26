from sqlalchemy import Column, Text, DateTime, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from config import Base
import uuid

class Dispense(Base):
    __tablename__ = "dispense"
    __table_args__ = {"schema": "medication"}

    dispense_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    prescription_id = Column(UUID(as_uuid=True),
                             ForeignKey("medication.prescription.prescription_id"),
                             nullable=False)

    status = Column(Text, nullable=False, default="PENDING")  # 'PENDING' | 'COMPLETED'
    dispensed_at = Column(DateTime, nullable=True)
    dispensed_by = Column(UUID(as_uuid=True), nullable=True)

    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    created_by = Column(UUID(as_uuid=True), nullable=True)
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    updated_by = Column(UUID(as_uuid=True), nullable=True)

    def __repr__(self):
        return f"<Dispense(id={self.dispense_id}, prescription_id={self.prescription_id}, status={self.status})>"


class DispenseLine(Base):
    __tablename__ = "dispense_line"
    __table_args__ = {"schema": "medication"}

    line_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dispense_id = Column(UUID(as_uuid=True),
                         ForeignKey("medication.dispense.dispense_id"),
                         nullable=False)
    prescription_item_id = Column(UUID(as_uuid=True),
                                  ForeignKey("medication.prescription_item.item_id"),
                                  nullable=False)

    quantity_dispensed = Column(Numeric(14, 3), nullable=False)
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime, nullable=False, server_default=func.now())

    def __repr__(self):
        return f"<DispenseLine(id={self.line_id}, dispense_id={self.dispense_id}, item_id={self.prescription_item_id})>"