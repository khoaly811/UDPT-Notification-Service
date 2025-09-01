from datetime import datetime
from pydantic import BaseModel
from bson import ObjectId
from typing import Optional


class Notification(BaseModel):
    id: str | None = None
    user_id: int
    title: str
    message: str
    prescription_id: Optional[int] = None
    appointment_id: int
    dispense_id: Optional[int] = None
    status: str = "UNREAD"  # UNREAD | READ
    created_at: datetime = datetime.utcnow()
