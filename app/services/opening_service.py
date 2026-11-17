from datetime import date
from typing import List, Optional
from fastapi import HTTPException, status
from app.repositories.opening_repo import OpeningRepository
from app.models.opening import Opening
from app.models.user import User
from app.schemas.opening import OpeningCreate, OpeningUpdate

class OpeningService:
    def __init__(self, opening_repo: OpeningRepository):
        self.opening_repo = opening_repo

    async def get_all_openings(self, user: Optional[User], **filters) -> List[Opening]:
        is_admin = False
        if user:
            roles = [r.role for r in user.roles]
            is_admin = "admin" in roles

        return await self.opening_repo.get_active_openings(
            include_all_for_admin=is_admin,
            **filters
        )

    async def get_opening(self, opening_id: str) -> Opening:
        opening = await self.opening_repo.get_by_id(opening_id)
        if not opening:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Opening not found.")
        return opening

    async def create_opening(self, payload: OpeningCreate, current_user: User) -> Opening:
        # Check if user is approved alumni or admin
        roles = [r.role for r in current_user.roles]
        is_admin = "admin" in roles
        is_alumni = "alumni" in roles

        if not is_admin and not is_alumni:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only alumni can post openings.")

        if is_alumni and not is_admin:
            if not current_user.alumni_details or current_user.alumni_details.verified != "approved":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Your alumni account must be approved by the committee before posting."
                )

        if payload.deadline < date.today():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Deadline cannot be in the past.")

        profile_name = current_user.profile.name if current_user.profile else "Alumnus"
        poster_batch = current_user.alumni_details.batch_year if current_user.alumni_details else None

        opening = await self.opening_repo.create(
            alumni_id=current_user.id,
            poster_name=profile_name,
            poster_batch=poster_batch,
            company=payload.company,
            role=payload.role,
            domain=payload.domain,
            location=payload.location,
            experience=payload.experience,
            eligible_branches=payload.eligible_branches,
            apply_link=payload.apply_link,
            deadline=payload.deadline,
            description=payload.description,
            max_referrals=payload.max_referrals,
            referred_count=0,
            status="open"
        )
        return opening

    async def update_opening(self, opening_id: str, payload: OpeningUpdate, current_user: User) -> Opening:
        opening = await self.get_opening(opening_id)
        roles = [r.role for r in current_user.roles]
        is_admin = "admin" in roles

        # IDOR prevention: only owner or admin can update
        if not is_admin and opening.alumni_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied.")

        update_dict = payload.model_dump(exclude_unset=True)
        # Non-admins cannot set 'removed' status
        if "status" in update_dict and update_dict["status"] == "removed" and not is_admin:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can remove openings.")

        updated = await self.opening_repo.update(opening_id, **update_dict)
        return updated
