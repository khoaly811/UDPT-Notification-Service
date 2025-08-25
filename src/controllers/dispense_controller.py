from fastapi import APIRouter, Depends, status, Path
from sqlalchemy.orm import Session
from uuid import UUID

from config import get_db
from src.services.dispense_service import DispenseService
from src.dto.dispense_dto import (
    DispenseCreateDTO, DispenseLineCreateDTO, DispenseCompleteDTO,
    DispenseResponseDTO
)

dispense_router = APIRouter(prefix="/dispenses", tags=["dispenses"])

def get_service(db: Session = Depends(get_db)) -> DispenseService:
    return DispenseService(db)

@dispense_router.post(
    "/", response_model=DispenseResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Create a dispense (PENDING)"
)
async def create_dispense(dto: DispenseCreateDTO, service: DispenseService = Depends(get_service)):
    return service.create_dispense(dto)

@dispense_router.post(
    "/{dispense_id}/lines", response_model=DispenseResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="Add a line to a PENDING dispense"
)
async def add_line(dispense_id: UUID, dto: DispenseLineCreateDTO, service: DispenseService = Depends(get_service)):
    return service.add_line(dispense_id, dto)

@dispense_router.post(
    "/{dispense_id}/complete", response_model=DispenseResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="Complete a PENDING dispense"
)
async def complete_dispense(dispense_id: UUID, dto: DispenseCompleteDTO, service: DispenseService = Depends(get_service)):
    return service.complete(dispense_id, dto)

@dispense_router.get(
    "/{dispense_id}", response_model=DispenseResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="Get dispense detail"
)
async def get_dispense(dispense_id: UUID, service: DispenseService = Depends(get_service)):
    return service.get_dispense(dispense_id)
