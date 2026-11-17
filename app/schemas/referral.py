from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.schemas.profile import ProfileResponse
from app.schemas.opening import OpeningResponse

class ReferralCreate(BaseModel):
    opening_id: str

class ReferralStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(requested|shortlisted|referred|rejected|placed)$")

class ReferralResponse(BaseModel):
    id: str
    opening_id: str
    student_id: str
    status: str
    created_at: datetime
    updated_at: datetime
    opening: Optional[OpeningResponse] = None
    student: Optional[ProfileResponse] = None

    class Config:
        from_attributes = True
