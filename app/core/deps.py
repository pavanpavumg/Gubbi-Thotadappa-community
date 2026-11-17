from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import decode_token
from app.models.user import User
from app.repositories.user_repo import UserRepository
from app.repositories.opening_repo import OpeningRepository
from app.repositories.referral_repo import ReferralRepository
from app.repositories.notification_repo import NotificationRepository
from app.services.auth_service import AuthService
from app.services.opening_service import OpeningService
from app.services.referral_service import ReferralService
from app.services.storage_service import StorageService

security_bearer = HTTPBearer(auto_error=False)

# --- Database & User Dependencies ---

async def get_current_user(
    auth: HTTPAuthorizationCredentials = Depends(security_bearer),
    db: AsyncSession = Depends(get_db)
) -> User:
    if not auth or not auth.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token required.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_token(auth.credentials)
    if not payload or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id)

    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User account inactive or missing.")

    return user

async def get_optional_user(
    auth: HTTPAuthorizationCredentials = Depends(security_bearer),
    db: AsyncSession = Depends(get_db)
) -> User | None:
    if not auth or not auth.credentials:
        return None
    payload = decode_token(auth.credentials)
    if not payload or payload.get("type") != "access":
        return None
    user_id = payload.get("sub")
    user_repo = UserRepository(db)
    return await user_repo.get_by_id(user_id)

def require_role(allowed_roles: list[str]):
    """Role-Based Access Control (RBAC) Guard."""
    def role_checker(current_user: User = Depends(get_current_user)):
        user_roles = [r.role for r in current_user.roles]
        if not any(role in user_roles for role in allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access forbidden: Requires one of {allowed_roles} roles."
            )
        return current_user
    return role_checker

# --- Service Injectors ---

def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(UserRepository(db), NotificationRepository(db))

def get_opening_service(db: AsyncSession = Depends(get_db)) -> OpeningService:
    return OpeningService(OpeningRepository(db))

def get_referral_service(db: AsyncSession = Depends(get_db)) -> ReferralService:
    return ReferralService(ReferralRepository(db), OpeningRepository(db), NotificationRepository(db))

def get_storage_service() -> StorageService:
    return StorageService()
