from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.repositories.base import BaseRepository
from app.models.user import User, UserRole, AdminAllowlist
from app.models.profile import Profile, AlumniDetails

class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(User, session)

    async def get_by_email(self, email: str) -> Optional[User]:
        stmt = select(User).where(User.email == email.lower().strip())
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def is_admin_allowlisted(self, email: str) -> bool:
        stmt = select(AdminAllowlist).where(AdminAllowlist.email == email.lower().strip())
        result = await self.session.execute(stmt)
        return result.scalars().first() is not None

    async def add_role(self, user_id: str, role: str) -> UserRole:
        user_role = UserRole(user_id=user_id, role=role)
        self.session.add(user_role)
        await self.session.commit()
        return user_role

    async def get_roles(self, user_id: str) -> List[str]:
        stmt = select(UserRole.role).where(UserRole.user_id == user_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create_profile(self, user_id: str, name: str, email: str) -> Profile:
        profile = Profile(id=user_id, name=name, email=email)
        self.session.add(profile)
        await self.session.commit()
        await self.session.refresh(profile)
        return profile

    async def create_alumni_details(self, user_id: str, **kwargs) -> AlumniDetails:
        alumni = AlumniDetails(user_id=user_id, **kwargs)
        self.session.add(alumni)
        await self.session.commit()
        await self.session.refresh(alumni)
        return alumni
