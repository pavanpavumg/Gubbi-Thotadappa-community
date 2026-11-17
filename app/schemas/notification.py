from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class NotificationResponse(BaseModel):
    id: str
    user_id: str
    title: str
    body: str
    link: Optional[str] = None
    read: bool
    created_at: datetime

    class Config:
        from_attributes = True

class PublicStatsResponse(BaseModel):
    students_placed: int
    referrals_made: int
    open_openings: int
    alumni: int
    students: int
