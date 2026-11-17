from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    course: Optional[str] = None
    branch: Optional[str] = None
    year: Optional[int] = None
    grad_year: Optional[int] = None
    room_no: Optional[str] = None
    interests: Optional[List[str]] = None
    skills: Optional[List[str]] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None

class AlumniDetailsResponse(BaseModel):
    batch_year: Optional[int] = None
    course: Optional[str] = None
    company: Optional[str] = None
    designation: Optional[str] = None
    work_email: Optional[str] = None
    verified: str

    class Config:
        from_attributes = True

class ProfileResponse(BaseModel):
    id: str
    name: str
    email: Optional[str] = None
    course: Optional[str] = None
    branch: Optional[str] = None
    year: Optional[int] = None
    grad_year: Optional[int] = None
    room_no: Optional[str] = None
    interests: List[str] = []
    skills: List[str] = []
    linkedin: Optional[str] = None
    github: Optional[str] = None
    resume_path: Optional[str] = None
    updated_at: datetime

    class Config:
        from_attributes = True

class MeResponse(BaseModel):
    user_id: str
    email: str
    roles: List[str]
    role: Optional[str] = None
    profile: Optional[ProfileResponse] = None
    alumni: Optional[AlumniDetailsResponse] = None

class ChooseRoleRequest(BaseModel):
    role: str
    details: dict = {}
