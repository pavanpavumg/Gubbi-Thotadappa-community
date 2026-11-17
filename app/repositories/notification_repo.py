from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, desc, func
from app.repositories.base import BaseRepository
from app.models.notification import Notification
from app.models.user import UserRole
from app.models.opening import Opening
from app.models.referral import ReferralRequest
from app.models.profile import AlumniDetails
from datetime import date

class NotificationRepository(BaseRepository[Notification]):
    def __init__(self, session: AsyncSession):
        super().__init__(Notification, session)

    async def get_by_user(self, user_id: str, limit: int = 30) -> List[Notification]:
        stmt = (
            select(Notification)
            .where(Notification.user_id == user_id)
            .order_by(desc(Notification.created_at))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def mark_all_read(self, user_id: str):
        stmt = (
            update(Notification)
            .where(Notification.user_id == user_id, Notification.read == False)
            .values(read=True)
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def notify_admins(self, title: str, body: str, link: Optional[str] = None):
        # Find all admins
        stmt = select(UserRole.user_id).where(UserRole.role == "admin")
        result = await self.session.execute(stmt)
        admin_ids = list(result.scalars().all())
        
        for aid in admin_ids:
            notif = Notification(user_id=aid, title=title, body=body, link=link)
            self.session.add(notif)
        await self.session.commit()

    async def get_public_stats(self) -> dict:
        today = date.today()
        # Students placed (distinct)
        placed_stmt = select(func.count(func.distinct(ReferralRequest.student_id))).where(ReferralRequest.status == "placed")
        placed_res = await self.session.execute(placed_stmt)

        # Referrals made
        ref_stmt = select(func.count(ReferralRequest.id)).where(ReferralRequest.status.in_(["referred", "placed"]))
        ref_res = await self.session.execute(ref_stmt)

        # Open openings
        op_stmt = select(func.count(Opening.id)).where(Opening.status == "open", Opening.deadline >= today)
        op_res = await self.session.execute(op_stmt)

        # Approved alumni
        alumni_stmt = select(func.count(AlumniDetails.user_id)).where(AlumniDetails.verified == "approved")
        alumni_res = await self.session.execute(alumni_stmt)

        # Registered students
        student_stmt = select(func.count(UserRole.id)).where(UserRole.role == "student")
        student_res = await self.session.execute(student_stmt)

        return {
            "students_placed": placed_res.scalar() or 0,
            "referrals_made": ref_res.scalar() or 0,
            "open_openings": op_res.scalar() or 0,
            "alumni": alumni_res.scalar() or 0,
            "students": student_res.scalar() or 0
        }
