from fastapi import APIRouter, Depends, status, Path, Query
from sqlalchemy.orm import Session
from src.services.medicine_service import MedicineService
from src.dto.pagination_dto import PaginationRequestDTO, PaginatedResponseDTO
from src.dto.medicine_dto import (
    MedicineCreateDTO,
    MedicineResponseDTO,
    MedicineListItemDTO,
    MedicineUpdateDTO,
)
from config import get_db

medicine_router = APIRouter(
    prefix="/medicines",
    tags=["Medicines"]
)


# ---------------- Dependency ----------------
def get_medicine_service(db: Session = Depends(get_db)) -> MedicineService:
    """Provide MedicineService with active DB session"""
    return MedicineService(db)


# ---------------- CREATE ----------------
@medicine_router.post(
    "",
    response_model=MedicineResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Create new medicine",
    description="Create a new medicine record in the system"
)
async def create_medicine(
    payload: MedicineCreateDTO,
    service: MedicineService = Depends(get_medicine_service)
):
    return service.create_medicine(payload)


# ---------------- GET DETAIL ----------------
@medicine_router.get(
    "/{medicine_id}",
    response_model=MedicineResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="Get medicine by ID",
    description="Retrieve detailed information of a specific medicine by its UUID"
)
async def get_medicine_by_id(
    medicine_id: int = Path(..., description="Medicine unique ID"),
    service: MedicineService = Depends(get_medicine_service)
):
    return service.get_medicine_by_id(medicine_id)


# ---------------- LIST + PAGINATION ----------------
@medicine_router.get(
    "",
    response_model=PaginatedResponseDTO[MedicineListItemDTO],
    status_code=status.HTTP_200_OK,
    summary="List medicines (paginated)",
    description="Retrieve a paginated list of medicines"
)
async def list_medicines(
    page: int = Query(1, ge=1, description="Page number, starts from 1"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    service: MedicineService = Depends(get_medicine_service)
):
    pagination = PaginationRequestDTO(page=page, page_size=page_size)
    return service.list_medicines(pagination)


# ---------------- UPDATE ----------------
@medicine_router.patch(
    "/{medicine_id}",
    response_model=MedicineResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="Update medicine details",
    description="Update selected fields of a medicine by its UUID"
)
async def update_medicine(
    medicine_id: int = Path(..., description="Medicine unique ID"),
    payload: MedicineUpdateDTO = ...,
    service: MedicineService = Depends(get_medicine_service)
):
    return service.update_medicine(medicine_id, payload)


# ---------------- DELETE / DEACTIVATE ----------------
@medicine_router.delete(
    "/{medicine_id}",
    response_model=MedicineResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="Deactivate medicine",
    description="Soft-delete (deactivate) a medicine by setting `is_active = False`"
)
async def delete_medicine(
    medicine_id: int = Path(..., description="Medicine unique ID"),
    service: MedicineService = Depends(get_medicine_service)
):
    return service.delete_medicine(medicine_id)
