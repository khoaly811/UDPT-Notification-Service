from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from config import Base

# SQLAlchemy Model (Database only)
class User(Base):
    __tablename__ = "user"
    __table_args__ = {"schema": "admin"}

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    email = Column(String(100), unique=True, nullable=True, index=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"