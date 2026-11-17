from datetime import date
from typing import List
from fastapi import HTTPException, status
from app.repositories.referral_repo import ReferralRepository
from app.repositories.opening_repo import OpeningRepository
from app.repositories.notification_repo import NotificationRepository
from app.models.referral import ReferralRequest
from app.models.user import User

class ReferralService:
    def __init__(
        self,
        referral_repo: ReferralRepository,
        opening_repo: OpeningRepository,
        notif_repo: NotificationRepository
    ):
        self.referral_repo = referral_repo
        self.opening_repo = opening_repo
        self.notif_repo = notif_repo

    async def request_referral(self, opening_id: str, student_user: User) -> ReferralRequest:
        profile = student_user.profile
        if not profile:
            raise HTTPException(status_code=400, detail="Profile not found. Please complete profile.")

        opening = await self.opening_repo.get_by_id(opening_id)
        if not opening:
            raise HTTPException(status_code=404, detail="Opening not found.")

        # Business Rule 1: Opening status & deadline
        if opening.status != "open":
            raise HTTPException(status_code=400, detail="This opening is no longer open for referrals.")
        if opening.deadline < date.today():
            raise HTTPException(status_code=400, detail="The deadline for this opening has passed.")

        # Business Rule 2: Slots availability
        if opening.referred_count >= opening.max_referrals:
            raise HTTPException(status_code=400, detail="All referral slots for this opening are full.")

        # Business Rule 3: Branch eligibility
        if opening.eligible_branches:
            branch_key = profile.branch if profile.course == "BE/BTech" else profile.course
            if not branch_key or branch_key not in opening.eligible_branches:
                raise HTTPException(status_code=400, detail="Your course/branch is not eligible for this opening.")

        # Business Rule 4: Resume presence
        if not profile.resume_path:
            raise HTTPException(status_code=400, detail="Upload your resume in Profile before requesting a referral.")

        # Business Rule 5: Duplicate prevention
        existing = await self.referral_repo.find_existing(opening_id, student_user.id)
        if existing:
            raise HTTPException(status_code=400, detail="You have already requested a referral for this opening.")

        request = await self.referral_repo.create(
            opening_id=opening_id,
            student_id=student_user.id,
            status="requested"
        )

        # Notify the alumni owner
        if opening.alumni_id:
            await self.notif_repo.create(
                user_id=opening.alumni_id,
                title="New referral request",
                body=f"{profile.name or 'A student'} requested a referral for {opening.role} at {opening.company}.",
                link=f"/manage/{opening.id}"
            )

        return request

    async def update_status(self, request_id: str, new_status: str, current_user: User) -> ReferralRequest:
        req = await self.referral_repo.get_by_id(request_id)
        if not req:
            raise HTTPException(status_code=404, detail="Referral request not found.")

        opening = await self.opening_repo.get_by_id(req.opening_id)
        roles = [r.role for r in current_user.roles]
        is_admin = "admin" in roles
        is_owner = opening.alumni_id == current_user.id

        # Rule for students: Can only self-report 'placed' if status is currently 'referred'
        if not is_admin and not is_owner:
            if req.student_id == current_user.id and new_status == "placed" and req.status == "referred":
                pass
            else:
                raise HTTPException(status_code=403, detail="Permission denied.")

        # Slot limit validation when marking 'referred' or 'placed'
        if new_status in ["referred", "placed"] and req.status not in ["referred", "placed"]:
            if opening.referred_count >= opening.max_referrals:
                raise HTTPException(status_code=400, detail="All referral slots for this opening are filled.")

        updated = await self.referral_repo.update(request_id, status=new_status)

        # Recompute opening referred count
        new_count = await self.referral_repo.count_referred_or_placed(req.opening_id)
        await self.opening_repo.update_referred_count(req.opening_id, new_count)

        # Notify the student
        await self.notif_repo.create(
            user_id=req.student_id,
            title=f"Referral status: {new_status.capitalize()}",
            body=f"{opening.role} at {opening.company} is now {new_status.capitalize()}.",
            link="/requests"
        )

        return updated

    async def withdraw_request(self, request_id: str, student_user: User):
        req = await self.referral_repo.get_by_id(request_id)
        if not req:
            raise HTTPException(status_code=404, detail="Request not found.")
        if req.student_id != student_user.id:
            raise HTTPException(status_code=403, detail="Permission denied.")
        if req.status != "requested":
            raise HTTPException(status_code=400, detail="Only pending requests can be withdrawn.")

        await self.referral_repo.delete(request_id)
        new_count = await self.referral_repo.count_referred_or_placed(req.opening_id)
        await self.opening_repo.update_referred_count(req.opening_id, new_count)
