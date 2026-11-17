from typing import Optional, List
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.repositories.base import BaseRepository
from app.models.opening import Opening

class OpeningRepository(BaseRepository[Opening]):
    def __init__(self, session: AsyncSession):
        super().__init__(Opening, session)

    async def get_active_openings(
        self,
        domain: Optional[str] = None,
        branch: Optional[str] = None,
        company: Optional[str] = None,
        search: Optional[str] = None,
        include_all_for_admin: bool = False
    ) -> List[Opening]:
        stmt = select(Opening)
        if not include_all_for_admin:
            stmt = stmt.where(Opening.status != "removed")
        
        stmt = stmt.order_by(desc(Opening.created_at))
        result = await self.session.execute(stmt)
        openings = list(result.scalars().all())

        # In-memory filter for flexible JSON array/search matching
        filtered = []
        for o in openings:
            if domain and o.domain != domain:
                continue
            if company and o.company != company:
                continue
            if branch and branch not in o.eligible_branches:
                continue
            if search:
                term = search.lower()
                text = f"{o.company} {o.role} {o.description}".lower()
                if term not in text:
                    continue
            filtered.append(o)
        return filtered

    async def get_by_alumni(self, alumni_id: str) -> List[Opening]:
        stmt = select(Opening).where(Opening.alumni_id == alumni_id).order_by(desc(Opening.created_at))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update_referred_count(self, opening_id: str, new_count: int) -> Optional[Opening]:
        opening = await self.get_by_id(opening_id)
        if not opening:
            return None
        opening.referred_count = new_count
        if opening.referred_count >= opening.max_referrals:
            opening.status = "full"
        elif opening.status == "full" and opening.referred_count < opening.max_referrals:
            opening.status = "open"
        await self.session.commit()
        await self.session.refresh(opening)
        return opening
