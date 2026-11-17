from fastapi import APIRouter, Depends, status
from app.schemas.auth import UserRegister, UserLogin, TokenResponse, TokenRefresh
from app.schemas.profile import MeResponse, ProfileResponse, AlumniDetailsResponse
from app.services.auth_service import AuthService
from app.core.deps import get_auth_service, get_current_user
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def signup(payload: UserRegister, service: AuthService = Depends(get_auth_service)):
    """Registers a new resident student or alumnus."""
    return await service.register(payload)

@router.post("/login", response_model=TokenResponse)
async def login(payload: UserLogin, service: AuthService = Depends(get_auth_service)):
    """Authenticates credentials and returns JWT tokens."""
    return await service.login(payload)

@router.post("/refresh", response_model=TokenResponse)
async def refresh(payload: TokenRefresh, service: AuthService = Depends(get_auth_service)):
    """Rotates refresh token and returns a fresh access token."""
    return await service.refresh_token(payload.refresh_token)

@router.get("/me", response_model=MeResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Returns currently authenticated user profile, roles, and alumni status."""
    roles = [r.role for r in current_user.roles]
    primary_role = "admin" if "admin" in roles else ("alumni" if "alumni" in roles else ("student" if "student" in roles else None))

    profile_data = None
    if current_user.profile:
        profile_data = ProfileResponse.model_validate(current_user.profile)

    alumni_data = None
    if current_user.alumni_details:
        alumni_data = AlumniDetailsResponse.model_validate(current_user.alumni_details)

    return MeResponse(
        user_id=current_user.id,
        email=current_user.email,
        roles=roles,
        role=primary_role,
        profile=profile_data,
        alumni=alumni_data
    )
