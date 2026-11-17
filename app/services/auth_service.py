from fastapi import HTTPException, status
from app.repositories.user_repo import UserRepository
from app.repositories.notification_repo import NotificationRepository
from app.schemas.auth import UserRegister, UserLogin, TokenResponse
from app.core.security import get_password_hash, verify_password, create_access_token, create_refresh_token, decode_token

class AuthService:
    def __init__(self, user_repo: UserRepository, notif_repo: NotificationRepository):
        self.user_repo = user_repo
        self.notif_repo = notif_repo

    async def register(self, payload: UserRegister) -> TokenResponse:
        existing = await self.user_repo.get_by_email(payload.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An account with this email already exists."
            )

        hashed = get_password_hash(payload.password)
        user = await self.user_repo.create(email=payload.email.lower().strip(), hashed_password=hashed)
        
        # Create base profile
        await self.user_repo.create_profile(user_id=user.id, name=payload.name, email=payload.email)

        # Check Admin Allowlist first
        is_admin = await self.user_repo.is_admin_allowlisted(payload.email)
        assigned_role = "admin" if is_admin else payload.role

        await self.user_repo.add_role(user.id, assigned_role)

        # If alumnus, create alumni details
        if payload.role == "alumni":
            await self.user_repo.create_alumni_details(
                user_id=user.id,
                batch_year=payload.batch_year,
                course=payload.course,
                company=payload.company,
                designation=payload.designation,
                work_email=payload.work_email,
                verified="approved" if is_admin else "pending"
            )
            # Notify admins of pending approval
            if not is_admin:
                await self.notif_repo.notify_admins(
                    title="New alumni awaiting approval",
                    body=f"{payload.name} · {payload.company or 'Alumnus'}",
                    link="/admin/alumni"
                )

        access_token = create_access_token(subject=user.id, claims={"role": assigned_role, "email": user.email})
        refresh_token = create_refresh_token(subject=user.id)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user_id=user.id,
            role=assigned_role
        )

    async def login(self, payload: UserLogin) -> TokenResponse:
        user = await self.user_repo.get_by_email(payload.email)
        if not user or not verify_password(payload.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password."
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is deactivated."
            )

        roles = await self.user_repo.get_roles(user.id)
        primary_role = "admin" if "admin" in roles else ("alumni" if "alumni" in roles else ("student" if "student" in roles else "user"))

        access_token = create_access_token(subject=user.id, claims={"role": primary_role, "email": user.email})
        refresh_token = create_refresh_token(subject=user.id)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user_id=user.id,
            role=primary_role
        )

    async def refresh_token(self, refresh_token: str) -> TokenResponse:
        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token.")

        user_id = payload.get("sub")
        user = await self.user_repo.get_by_id(user_id)
        if not user or not user.is_active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive.")

        roles = await self.user_repo.get_roles(user.id)
        primary_role = "admin" if "admin" in roles else ("alumni" if "alumni" in roles else "student")

        new_access = create_access_token(subject=user.id, claims={"role": primary_role, "email": user.email})
        new_refresh = create_refresh_token(subject=user.id)

        return TokenResponse(
            access_token=new_access,
            refresh_token=new_refresh,
            user_id=user.id,
            role=primary_role
        )
