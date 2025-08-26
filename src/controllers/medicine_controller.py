from fastapi import APIRouter, Depends, status, Path, Query
from sqlalchemy.orm import Session
from uuid import UUID

from src.services.medicine_service import MedicineService
from src.dto.pagination_dto import PaginationRequestDTO, PaginatedResponseDTO
from src.dto.medicine_dto import (
    MedicineCreateDTO,
    MedicineResponseDTO,
    MedicineListItemDTO,
    MedicineUpdateDTO,
)
from config import get_db

medicine_router = APIRouter(prefix="/medicines", tags=["medicines"])


def get_medicine_service(db: Session = Depends(get_db)) -> MedicineService:
    """Dependency để get MedicineService"""
    return MedicineService(db)


# ---------------- CREATE ----------------
@medicine_router.post(
    "/",
    response_model=MedicineResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Create new medicine",
    description="Create a new medicine record"
)
async def create_medicine(
    data: MedicineCreateDTO,
    service: MedicineService = Depends(get_medicine_service)
):
    return service.create_medicine(data)


# ---------------- DETAIL ----------------
@medicine_router.get(
    "/{medicine_id}",
    response_model=MedicineResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="Get medicine by ID",
    description="Retrieve detailed information of a specific medicine"
)
async def get_medicine_by_id(
    medicine_id: UUID = Path(..., description="Medicine ID"),
    service: MedicineService = Depends(get_medicine_service)
):
    return service.get_medicine_by_id(medicine_id)


# ---------------- LIST + PAGINATION ----------------
@medicine_router.get(
    "/",
    response_model=PaginatedResponseDTO[MedicineListItemDTO],
    status_code=status.HTTP_200_OK,
    summary="List medicines (paginated)",
    description="List medicines with pagination"
)
async def list_medicines(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    service: MedicineService = Depends(get_medicine_service)
):
    pagination = PaginationRequestDTO(page=page, page_size=page_size)
    return service.list_medicines(pagination)


# ---------------- UPDATE ----------------
@medicine_router.patch(
    "/{medicine_id}",
    response_model=MedicineResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="Update a medicine"
)
async def update_medicine(
    medicine_id: UUID,
    data: MedicineUpdateDTO,
    service: MedicineService = Depends(get_medicine_service)
):
    return service.update_medicine(medicine_id, data)


# ---------------- DELETE / DEACTIVATE ----------------
@medicine_router.delete(
    "/{medicine_id}",
    response_model=MedicineResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="Delete (deactivate) a medicine"
)
async def delete_medicine(
    medicine_id: UUID,
    service: MedicineService = Depends(get_medicine_service)
):
    return service.delete_medicine(medicine_id)
