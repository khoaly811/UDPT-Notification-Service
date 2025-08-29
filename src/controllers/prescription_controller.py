from fastapi import APIRouter, Depends, status, Path, Query, Body
from sqlalchemy.orm import Session

from src.services.prescription_service import PrescriptionService
from src.dto.pagination_dto import PaginationRequestDTO, PaginatedResponseDTO
from src.dto.prescription_dto import (
    PrescriptionCreateDTO,
    PrescriptionResponseDTO,
    PrescriptionListItemDTO,
    PrescriptionUpdateDTO,
    PrescriptionItemAddDTO,
    CancelPrescriptionDTO,
)
from config import get_db


prescription_router = APIRouter(prefix="/prescriptions", tags=["prescriptions"])


def get_prescription_service(db: Session = Depends(get_db)) -> PrescriptionService:
    """Dependency để get PrescriptionService"""
    return PrescriptionService(db)

# ---------------- CREATE ----------------
@prescription_router.post(
    "/",
    response_model=PrescriptionResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Create new prescription",
    description="Create a new prescription with its items"
)
async def create_prescription(
    data: PrescriptionCreateDTO,
    service: PrescriptionService = Depends(get_prescription_service)
):
    return service.create_prescription(data)

# ---------------- DETAIL ----------------
@prescription_router.get(
    "/{prescription_id}",
    response_model=PrescriptionResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="Get prescription by ID",
    description="Retrieve detailed information of a specific prescription including items"
)
async def get_prescription_by_id(
    prescription_id: int = Path(..., description="Prescription ID"),
    service: PrescriptionService = Depends(get_prescription_service)
):
    return service.get_prescription_by_id(prescription_id)

# ---------------- LIST + PAGINATION ----------------
@prescription_router.get(
    "/",
    response_model=PaginatedResponseDTO[PrescriptionListItemDTO],
    status_code=status.HTTP_200_OK,
    summary="List prescriptions (paginated)",
    description="List prescriptions with pagination"
)
async def list_prescriptions(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    service: PrescriptionService = Depends(get_prescription_service)
):
    pagination = PaginationRequestDTO(page=page, page_size=page_size)
    return service.list_prescriptions(pagination)

# ---------------- UPDATE (PATCH) ----------------
@prescription_router.patch(
    "/{prescription_id}",
    response_model=PrescriptionResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="Update a prescription (notes/valid_from/valid_to)"
)
async def update_prescription(
    prescription_id: int,
    data: PrescriptionUpdateDTO,
    service: PrescriptionService = Depends(get_prescription_service)
):
    return service.update_prescription(prescription_id, data)
# ---------------- ADD ONE ITEM ----------------
@prescription_router.post(
    "/{prescription_id}/items",
    response_model=PrescriptionResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="Add one item to a prescription"
)
async def add_item_to_prescription(
    prescription_id: int,
    item: PrescriptionItemAddDTO,
    service: PrescriptionService = Depends(get_prescription_service)
):
    return service.add_item(prescription_id, item)


# ---------------- REMOVE ONE ITEM ----------------
@prescription_router.delete(
    "/{prescription_id}/items/{item_id}",
    response_model=PrescriptionResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="Remove one item from a prescription"
)
async def remove_item_from_prescription(
    prescription_id: int,
    item_id: int,
    service: PrescriptionService = Depends(get_prescription_service)
):
    return service.remove_item(prescription_id, item_id)


# ---------------- CANCEL ----------------
@prescription_router.post(
    "/{prescription_id}/cancel",
    response_model=PrescriptionResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="Cancel a prescription"
)
async def cancel_prescription(
    prescription_id: int,
    payload: CancelPrescriptionDTO = Body(..., description="Cancel reason and user"),
    service: PrescriptionService = Depends(get_prescription_service)
):
    return service.cancel_prescription(prescription_id, payload)