from src.repositories.notification_repository import NotificationRepository
from src.models.notification import Notification
from datetime import datetime
from typing import Optional

class NotificationService:
    def create_notification(
        self,
        user_id: int,
        appointment_id: Optional[int] = None,
        prescription_id: Optional[int] = None,
        dispense_id: Optional[int] = None,
        prescription_code: Optional[str] = None,
        title: Optional[str] = None,
        message: Optional[str] = None
    ):
        notif = Notification(
            user_id=user_id,
            title=title or "Đơn thuốc đã sẵn sàng",
            message=message or f"Đơn thuốc {prescription_code} đã sẵn sàng để nhận",
            prescription_id=prescription_id,
            appointment_id=appointment_id,
            dispense_id=dispense_id,
            status="UNREAD",
            created_at=datetime.utcnow()
        )
        return NotificationRepository.save(notif.dict(exclude_none=True))

    def get_notifications_for_user(self, user_id: int):
        return NotificationRepository.find_by_user(user_id)

    def mark_as_read(self, notification_id: str):
        NotificationRepository.mark_as_read(notification_id)
