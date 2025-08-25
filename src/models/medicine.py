from sqlalchemy import Column, String, Boolean, Text, DateTime, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from config import Base
import uuid


class Medicine(Base):
    __tablename__ = "medicine"
    __table_args__ = {"schema": "medication"}

    medication_id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())

    atc_code = Column(String, nullable=True)          # mã ATC
    medicine_name = Column(Text, nullable=False)      # tên thuốc
    generic_name = Column(Text, nullable=True)        # tên hoạt chất
    form = Column(Text, nullable=True)                # dạng bào chế
    strength = Column(Text, nullable=True)            # hàm lượng
    unit = Column(Text, nullable=True)                # đơn vị
    stock = Column(Numeric(14, 3), nullable=False, default="0")
    is_active = Column(Boolean, nullable=False, server_default="true")

    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Medicine(id={self.medication_id}, name={self.medicine_name})>"
