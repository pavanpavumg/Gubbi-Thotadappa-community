from typing import List, Dict, Any
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.core.deps import require_role, get_db
from app.models.user import User, UserRole
from app.models.profile import Profile, AlumniDetails
from app.models.opening import Opening
from app.models.referral import ReferralRequest
from app.models.notification import Notification

router = APIRouter(prefix="/admin", tags=["Admin Operations"], dependencies=[Depends(require_role(["admin"]))])

class AlumniReviewRequest(BaseModel):
    status: str = Field(..., pattern="^(approved|rejected)$")

@router.get("/alumni")
async def list_alumni(db: AsyncSession = Depends(get_db)):
    """Lists all alumni with their verification status and profiles."""
    stmt = (
        select(AlumniDetails, Profile)
        .join(Profile, Profile.id == AlumniDetails.user_id)
        .order_by(desc(AlumniDetails.created_at))
    )
    result = await db.execute(stmt)
    rows = result.all()

    alumni_list = []
    for details, profile in rows:
        alumni_list.append({
            "user_id": details.user_id,
            "company": details.company,
            "designation": details.designation,
            "batch_year": details.batch_year,
            "course": details.course,
            "work_email": details.work_email,
            "verified": details.verified,
            "created_at": details.created_at,
            "name": profile.name,
            "login_email": profile.email,
            "linkedin": profile.linkedin
        })
    return alumni_list

@router.patch("/alumni/{user_id}/review")
async def review_alumni(
    user_id: str,
    payload: AlumniReviewRequest,
    db: AsyncSession = Depends(get_db)
):
    """Hostel committee approves or rejects an alumnus registration."""
    stmt = select(AlumniDetails).where(AlumniDetails.user_id == user_id)
    result = await db.execute(stmt)
    alumni = result.scalars().first()

    if not alumni:
        raise HTTPException(status_code=404, detail="Alumnus not found.")

    alumni.verified = payload.status
    alumni.reviewed_at = datetime.now(timezone.utc)

    # Notify alumnus
    body_msg = (
        "You can now post openings and refer hostel juniors."
        if payload.status == "approved"
        else "Contact the hostel committee if you think this is a mistake."
    )
    notif = Notification(
        user_id=user_id,
        title=f"Your alumni account was {payload.status}",
        body=body_msg,
        link="/alumni"
    )
    db.add(notif)
    await db.commit()

    return {"status": "ok", "verified": payload.status}

@router.get("/analytics")
async def get_admin_analytics(db: AsyncSession = Depends(get_db)):
    """Computes placement distribution across engineering and PG branches."""
    # Fetch all placed referrals
    stmt = (
        select(ReferralRequest, Profile)
        .join(Profile, Profile.id == ReferralRequest.student_id)
        .where(ReferralRequest.status == "placed")
    )
    result = await db.execute(stmt)
    rows = result.all()

    by_branch: Dict[str, int] = {}
    for _, profile in rows:
        key = profile.branch if profile.course == "BE/BTech" else (profile.course or "Unknown")
        by_branch[key] = by_branch.get(key, 0) + 1

    return {
        "placements_by_branch": by_branch
    }
