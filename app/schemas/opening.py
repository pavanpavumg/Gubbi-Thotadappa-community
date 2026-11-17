from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
from datetime import date, datetime

class OpeningCreate(BaseModel):
    company: str = Field(..., min_length=1)
    role: str = Field(..., min_length=1)
    domain: str = "Software"
    location: str = "Bengaluru"
    experience: str = "Fresher"
    eligible_branches: List[str] = Field(..., min_items=1)
    apply_link: Optional[str] = None
    deadline: date
    description: str = ""
    max_referrals: int = Field(5, ge=1, le=500)

class OpeningUpdate(BaseModel):
    company: Optional[str] = None
    role: Optional[str] = None
    domain: Optional[str] = None
    location: Optional[str] = None
    experience: Optional[str] = None
    eligible_branches: Optional[List[str]] = None
    apply_link: Optional[str] = None
    deadline: Optional[date] = None
    description: Optional[str] = None
    max_referrals: Optional[int] = None
    status: Optional[str] = Field(None, pattern="^(open|full|closed|removed)$")

class OpeningResponse(BaseModel):
    id: str
    alumni_id: Optional[str] = None
    poster_name: Optional[str] = None
    poster_batch: Optional[int] = None
    company: str
    role: str
    domain: str
    location: str
    experience: str
    eligible_branches: List[str]
    apply_link: Optional[str] = None
    deadline: date
    description: str
    max_referrals: int
    referred_count: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
