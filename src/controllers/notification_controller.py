from fastapi import APIRouter, Body
from src.services.notification_service import NotificationService
from src.dto.notification_dto import NotificationResponseDTO, MarkReadDTO

import smtplib
from email.mime.text import MIMEText

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

@router.post("/send-email")
def send_email(to: str = Body(...), subject: str = Body(...), text: str = Body(...)):
    sender = "dangkhoaly431@gmail.com"
    password = "fjpl nyoi fcfa wzjs"

    msg = MIMEText(text)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = to

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, password)
            server.sendmail(sender, [to], msg.as_string())
        return {"message": "Email sent successfully!"}
    except Exception as e:
        return {"error": str(e)}
