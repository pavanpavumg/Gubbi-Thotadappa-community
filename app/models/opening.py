import uuid
from datetime import datetime, date, timezone
from typing import Optional, List
from sqlalchemy import String, Integer, DateTime, Date, ForeignKey, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

def gen_uuid() -> str:
    return str(uuid.uuid4())

class Opening(Base):
    __tablename__ = "openings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    alumni_id: Mapped[Optional[str]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    poster_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    poster_batch: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    company: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(255), nullable=False)
    domain: Mapped[str] = mapped_column(String(100), default="Software")
    location: Mapped[str] = mapped_column(String(255), default="Bengaluru")
    experience: Mapped[str] = mapped_column(String(100), default="Fresher")
    eligible_branches: Mapped[List[str]] = mapped_column(JSON, default=list)
    apply_link: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    deadline: Mapped[date] = mapped_column(Date, nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    max_referrals: Mapped[int] = mapped_column(Integer, default=5)
    referred_count: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(20), default="open") # 'open', 'full', 'closed', 'removed'
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    referral_requests: Mapped[list["ReferralRequest"]] = relationship("ReferralRequest", back_populates="opening", cascade="all, delete-orphan", lazy="selectin")
