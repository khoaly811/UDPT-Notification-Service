from fastapi import APIRouter
from src.services.notification_service import NotificationService
from src.dto.notification_dto import NotificationResponseDTO, MarkReadDTO

router = APIRouter(prefix="/notifications", tags=["notifications"])
service = NotificationService()

@router.get("/{user_id}", response_model=list[NotificationResponseDTO])
def list_notifications(user_id: int):
    docs = service.get_notifications_for_user(user_id)
    return [
        NotificationResponseDTO(
            id=str(doc["_id"]),
            user_id=doc["user_id"],
            title=doc["title"],
            message=doc["message"],
            prescription_id=doc["prescription_id"],
            appointment_id=doc["appointment_id"],
            dispense_id=doc["dispense_id"],
            status=doc["status"],
            created_at=doc["created_at"]
        )
        for doc in docs
    ]

@router.post("/read")
def mark_read(dto: MarkReadDTO):
    service.mark_as_read(dto.notification_id)
    return {"status": "ok"}
