import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

def gen_uuid() -> str:
    return str(uuid.uuid4())

class ReferralRequest(Base):
    __tablename__ = "referral_requests"
    __table_args__ = (UniqueConstraint("opening_id", "student_id", name="uq_opening_student"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    opening_id: Mapped[str] = mapped_column(ForeignKey("openings.id", ondelete="CASCADE"), nullable=False)
    student_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="requested") # 'requested', 'shortlisted', 'referred', 'rejected', 'placed'
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    opening: Mapped["Opening"] = relationship("Opening", back_populates="referral_requests")
    student: Mapped["Profile"] = relationship("Profile", foreign_keys=[student_id], primaryjoin="ReferralRequest.student_id == Profile.id", lazy="selectin")
