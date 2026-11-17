from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc, func
from app.repositories.base import BaseRepository
from app.models.referral import ReferralRequest
from app.models.opening import Opening

def is_final_year(course: Optional[str], year: Optional[int]) -> bool:
    if not course or not year:
        return False
    duration = 4 if course == "BE/BTech" else 2
    return year >= duration

class ReferralRepository(BaseRepository[ReferralRequest]):
    def __init__(self, session: AsyncSession):
        super().__init__(ReferralRequest, session)

    async def get_by_student(self, student_id: str) -> List[ReferralRequest]:
        stmt = (
            select(ReferralRequest)
            .where(ReferralRequest.student_id == student_id)
            .order_by(desc(ReferralRequest.created_at))
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_opening_sorted(self, opening_id: str) -> List[ReferralRequest]:
        stmt = select(ReferralRequest).where(ReferralRequest.opening_id == opening_id)
        result = await self.session.execute(stmt)
        requests = list(result.scalars().all())

        # Final-year students first, then higher year, then earliest application
        def sort_key(req: ReferralRequest):
            student = req.student
            final = 1 if is_final_year(getattr(student, "course", None), getattr(student, "year", None)) else 0
            year = getattr(student, "year", 0) or 0
            created = req.created_at.timestamp() if req.created_at else 0
            return (-final, -year, created)

        requests.sort(key=sort_key)
        return requests

    async def count_referred_or_placed(self, opening_id: str) -> int:
        stmt = (
            select(func.count(ReferralRequest.id))
            .where(
                and_(
                    ReferralRequest.opening_id == opening_id,
                    ReferralRequest.status.in_(["referred", "placed"])
                )
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar() or 0

    async def find_existing(self, opening_id: str, student_id: str) -> Optional[ReferralRequest]:
        stmt = select(ReferralRequest).where(
            and_(
                ReferralRequest.opening_id == opening_id,
                ReferralRequest.student_id == student_id
            )
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()
