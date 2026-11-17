import uuid
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import String, Integer, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

class Profile(Base):
    __tablename__ = "profiles"

    id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), default="")
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    course: Mapped[Optional[str]] = mapped_column(String(100), nullable=True) # BE/BTech, MCA, MBA, MTech
    branch: Mapped[Optional[str]] = mapped_column(String(100), nullable=True) # CSE, ISE, ECE, etc.
    year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    grad_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    room_no: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    interests: Mapped[List[str]] = mapped_column(JSON, default=list)
    skills: Mapped[List[str]] = mapped_column(JSON, default=list)
    linkedin: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    github: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    resume_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user: Mapped["User"] = relationship("User", back_populates="profile")

class AlumniDetails(Base):
    __tablename__ = "alumni_details"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    batch_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    course: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    company: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    designation: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    work_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    verified: Mapped[str] = mapped_column(String(20), default="pending") # 'pending', 'approved', 'rejected'
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user: Mapped["User"] = relationship("User", back_populates="alumni_details")
