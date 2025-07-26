from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional

from src.models.user import User

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all_users(self, skip: int = 0, limit: int = 100) -> list[type[User]]:
        """Lấy danh sách tất cả người dùng với phân trang"""
        return self.db.query(User).offset(skip).limit(limit).all()

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Lấy người dùng theo ID"""
        return self.db.query(User).filter(User.id == user_id).first()

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Lấy người dùng theo username"""
        return self.db.query(User).filter(User.username == username).first()

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Lấy người dùng theo email"""
        return self.db.query(User).filter(User.email == email).first()

    def count_users(self) -> int:
        """Đếm tổng số người dùng"""
        return self.db.query(func.count(User.id)).scalar()

    def create_user(self, user: User) -> User:
        """Tạo người dùng mới"""
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_user(self, user: User) -> User:
        """Cập nhật thông tin người dùng"""
        self.db.commit()
        self.db.refresh(user)
        return user

    def delete_user(self, user: User) -> bool:
        """Xóa người dùng"""
        try:
            self.db.delete(user)
            self.db.commit()
            return True
        except SQLAlchemyError:
            self.db.rollback()
            return False