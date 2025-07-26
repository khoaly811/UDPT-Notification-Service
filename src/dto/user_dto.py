from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List

# Base DTO
class UserBaseDTO(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Username must be between 3-50 characters")
    email: Optional[EmailStr] = Field(None, description="Valid email address")

# Request DTOs
class UserCreateDTO(UserBaseDTO):
    password: str = Field(..., min_length=6, max_length=255, description="Password must be at least 6 characters")

class UserUpdateDTO(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="Username must be between 3-50 characters")
    email: Optional[EmailStr] = Field(None, description="Valid email address")
    password: Optional[str] = Field(None, min_length=6, max_length=255, description="Password must be at least 6 characters")

# Response DTOs
class UserResponseDTO(UserBaseDTO):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserListResponseDTO(BaseModel):
    users: List[UserResponseDTO]
    total: int
    page: int
    page_size: int
    total_pages: int

class UserDetailResponseDTO(UserResponseDTO):
    """Extended user response with additional details if needed"""
    pass

# Common Response DTOs
class MessageResponseDTO(BaseModel):
    message: str
    status: str = "success"

class ErrorResponseDTO(BaseModel):
    message: str
    status: str = "error"
    error_code: Optional[str] = None