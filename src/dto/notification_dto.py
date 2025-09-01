from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class NotificationResponseDTO(BaseModel):
    id: str
    user_id: int
    title: str
    message: str
    prescription_id: Optional[int] = None
    appointment_id: int
    dispense_id: Optional[int] = None
    status: str
    created_at: datetime

class MarkReadDTO(BaseModel):
    notification_id: str
