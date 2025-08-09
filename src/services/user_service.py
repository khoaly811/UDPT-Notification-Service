from sqlalchemy.orm import Session
from src.repositories.user_repository import UserRepository
from src.models.user import User
from src.dto.user_dto import (
    UserCreateDTO,
    UserUpdateDTO,
    UserResponseDTO,
    UserDetailResponseDTO
)
from src.dto.pagination_dto import PaginatedResponseDTO, PaginationRequestDTO
from fastapi import HTTPException, status
import hashlib

class UserService:
    def __init__(self, db: Session):
        self.repository = UserRepository(db)

    def get_users_list(self, pagination_request: PaginationRequestDTO) -> PaginatedResponseDTO[UserResponseDTO]:
        """Lấy danh sách người dùng với phân trang"""
        skip = pagination_request.calc_skip()

        # Lấy danh sách users và tổng số
        users = self.repository.get_all_users(skip=skip, limit=pagination_request.page_size)
        total = self.repository.count_users()
        if total == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Users not found."
            )

        if skip >= total:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Page number exceeds total number of pages"
            )

        # Convert sang UserResponseDTO
        user_responses = [UserResponseDTO.model_validate(user) for user in users]

        return PaginatedResponseDTO.create(
            data=user_responses,
            page=pagination_request.page,
            page_size=pagination_request.page_size,
            total=total
        )

    def get_user_by_id(self, user_id: int) -> UserDetailResponseDTO:
        """Lấy thông tin chi tiết người dùng theo ID"""
        user = self.repository.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found"
            )

        return UserDetailResponseDTO.model_validate(user)

    def create_user(self, user_data: UserCreateDTO) -> UserResponseDTO:
        """Tạo người dùng mới"""
        # Kiểm tra username đã tồn tại
        existing_user = self.repository.get_user_by_username(user_data.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )

        # Kiểm tra email đã tồn tại (nếu có)
        if user_data.email:
            existing_email = self.repository.get_user_by_email(str(user_data.email))
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already exists"
                )

        # Hash password
        hashed_password = self._hash_password(user_data.password)

        # Tạo user object
        user = User(
            username=user_data.username,
            email=str(user_data.email) if user_data.email else None,
            password=hashed_password
        )

        # Lưu vào database
        created_user = self.repository.create_user(user)

        return UserResponseDTO.model_validate(created_user)

    def update_user(self, user_id: int, user_data: UserUpdateDTO) -> UserResponseDTO:
        """Cập nhật thông tin người dùng"""
        user = self.validate_user_exists(user_id)

        # Kiểm tra username đã tồn tại (nếu có thay đổi)
        if user_data.username and user_data.username != user.username:
            existing_user = self.repository.get_user_by_username(user_data.username)
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already exists"
                )
            user.username = user_data.username

        # Kiểm tra email đã tồn tại (nếu có thay đổi)
        if user_data.email and str(user_data.email) != user.email:
            existing_email = self.repository.get_user_by_email(str(user_data.email))
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already exists"
                )
            user.email = str(user_data.email)

        # Cập nhật password (nếu có)
        if user_data.password:
            user.password = self._hash_password(user_data.password)

        # Lưu thay đổi
        updated_user = self.repository.update_user(user)

        return UserResponseDTO.model_validate(updated_user)

    def delete_user(self, user_id: int) -> bool:
        """Xóa người dùng"""
        user = self.validate_user_exists(user_id)
        return self.repository.delete_user(user)

    @staticmethod
    def _hash_password(password: str) -> str:
        """Hash password sử dụng SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()

    def validate_user_exists(self, user_id: int) -> User:
        """Validate và trả về user nếu tồn tại"""
        user = self.repository.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found"
            )
        return user