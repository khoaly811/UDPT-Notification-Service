from fastapi import APIRouter, Depends, Query, status, Path
from sqlalchemy.orm import Session
from src.services.user_service import UserService
from src.dto.user_dto import (
    UserCreateDTO,
    UserUpdateDTO,
    UserResponseDTO,
    UserDetailResponseDTO,
    MessageResponseDTO
)
from src.dto.pagination_dto import PaginatedResponseDTO, PaginationRequestDTO
from config import get_db

router = APIRouter(prefix="/users", tags=["users"])

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    """Dependency để get UserService instance"""
    return UserService(db)

@router.get(
    "/",
    response_model=PaginatedResponseDTO[UserResponseDTO],
    status_code=status.HTTP_200_OK,
    summary="Get users list",
    description="Retrieve a paginated list of all users"
)
async def get_users(
        page: int = Query(1, ge=1, description="Page number (starts from 1)"),
        page_size: int = Query(10, ge=1, le=100, description="Number of items per page (max 100)"),
        service: UserService = Depends(get_user_service)
):
    """
    Lấy danh sách tất cả người dùng với phân trang

    - **page**: Số trang (bắt đầu từ 1)
    - **page_size**: Số lượng items mỗi trang (tối đa 100)

    Returns:
        PaginatedResponseDTO với danh sách users và metadata phân trang
    """
    pagination_request = PaginationRequestDTO(page=page, page_size=page_size)
    return service.get_users_list(pagination_request)

@router.get(
    "/{user_id}",
    response_model=UserDetailResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="Get user by ID",
    description="Retrieve detailed information of a specific user"
)
async def get_user_by_id(
        user_id: int = Path(..., gt=0, description="User ID must be greater than 0"),
        service: UserService = Depends(get_user_service)
):
    """
    Lấy thông tin chi tiết của một người dùng theo ID

    - **user_id**: ID của người dùng cần lấy thông tin

    Returns:
        UserDetailResponseDTO với thông tin chi tiết user
    """
    return service.get_user_by_id(user_id)

@router.post(
    "/",
    response_model=UserResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Create new user",
    description="Create a new user account"
)
async def create_user(
        user_data: UserCreateDTO,
        service: UserService = Depends(get_user_service)
):
    """
    Tạo người dùng mới

    - **username**: Tên đăng nhập (duy nhất, 3-50 ký tự)
    - **password**: Mật khẩu (tối thiểu 6 ký tự)
    - **email**: Email (tùy chọn, duy nhất nếu có)

    Returns:
        UserResponseDTO với thông tin user vừa tạo
    """
    return service.create_user(user_data)

@router.put(
    "/{user_id}",
    response_model=UserResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="Update user",
    description="Update user information"
)
async def update_user(
        user_id: int = Path(..., gt=0, description="User ID must be greater than 0"),
        user_data: UserUpdateDTO = ...,
        service: UserService = Depends(get_user_service)
):
    """
    Cập nhật thông tin người dùng

    - **user_id**: ID của người dùng cần cập nhật
    - **username**: Tên đăng nhập mới (tùy chọn)
    - **password**: Mật khẩu mới (tùy chọn)
    - **email**: Email mới (tùy chọn)

    Returns:
        UserResponseDTO với thông tin user đã cập nhật
    """
    return service.update_user(user_id, user_data)

@router.delete(
    "/{user_id}",
    response_model=MessageResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="Delete user",
    description="Delete a user account"
)
async def delete_user(
        user_id: int = Path(..., gt=0, description="User ID must be greater than 0"),
        service: UserService = Depends(get_user_service)
):
    """
    Xóa người dùng

    - **user_id**: ID của người dùng cần xóa

    Returns:
        MessageResponseDTO xác nhận việc xóa
    """
    success = service.delete_user(user_id)
    if success:
        return MessageResponseDTO(message=f"User with id {user_id} deleted successfully")
    else:
        return MessageResponseDTO(
            message=f"Failed to delete user with id {user_id}",
            status="error"
        )