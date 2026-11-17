from typing import List
from fastapi import APIRouter, Depends, status
from app.schemas.referral import ReferralCreate, ReferralStatusUpdate, ReferralResponse
from app.services.referral_service import ReferralService
from app.repositories.referral_repo import ReferralRepository
from app.core.deps import get_referral_service, get_current_user, require_role, get_db
from app.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/referrals", tags=["Referrals"])

@router.post("/", response_model=ReferralResponse, status_code=status.HTTP_201_CREATED)
async def request_referral(
    payload: ReferralCreate,
    current_user: User = Depends(require_role(["student"])),
    service: ReferralService = Depends(get_referral_service)
):
    """Student requests a job referral for an opening."""
    return await service.request_referral(payload.opening_id, current_user)

@router.get("/my-requests", response_model=List[ReferralResponse])
async def get_my_requests(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Returns all referral requests submitted by the logged-in student."""
    repo = ReferralRepository(db)
    return await repo.get_by_student(current_user.id)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def withdraw_request(
    id: str,
    current_user: User = Depends(require_role(["student"])),
    service: ReferralService = Depends(get_referral_service)
):
    """Allows student to withdraw a pending referral request."""
    await service.withdraw_request(id, current_user)
    return None

@router.get("/opening/{opening_id}", response_model=List[ReferralResponse])
async def get_opening_applicants(
    opening_id: str,
    current_user: User = Depends(require_role(["alumni", "admin"])),
    db: AsyncSession = Depends(get_db)
):
    """
    Returns applicants for an opening sorted by:
    1. Final-year students first
    2. Higher year
    3. Earliest application date
    """
    repo = ReferralRepository(db)
    return await repo.get_by_opening_sorted(opening_id)

@router.patch("/{id}/status", response_model=ReferralResponse)
async def update_referral_status(
    id: str,
    payload: ReferralStatusUpdate,
    current_user: User = Depends(get_current_user),
    service: ReferralService = Depends(get_referral_service)
):
    """
    Updates referral progress:
    - Alumni/Admin can set 'shortlisted', 'referred', 'rejected', 'placed'.
    - Students can mark themselves 'placed' if they were 'referred'.
    """
    return await service.update_status(id, payload.status, current_user)
