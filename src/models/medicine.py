from sqlalchemy import Column, String, Boolean, Text, DateTime, ForeignKey, Numeric, Integer
from sqlalchemy.sql import func
from config import Base
import uuid


class Medicine(Base):
    __tablename__ = "medicine"
    __table_args__ = {"schema": "medication"}

    medication_id = Column(Integer, primary_key=True, index=True)

    atc_code = Column(String, nullable=True)          # mã ATC
    medicine_name = Column(Text, nullable=False)      # tên thuốc
    generic_name = Column(Text, nullable=True)        # tên hoạt chất
    form = Column(Text, nullable=True)                # dạng bào chế
    strength = Column(Text, nullable=True)            # hàm lượng
    unit = Column(Text, nullable=True)                # đơn vị
    stock = Column(Numeric(14, 3), nullable=False, default="0")
    is_active = Column(Boolean, nullable=False, server_default="true")
    expiry_date = Column(DateTime, nullable=False, server_default=func.now())
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Medicine(id={self.medication_id}, name={self.medicine_name})>"