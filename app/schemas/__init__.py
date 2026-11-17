from app.schemas.auth import (
    UserRegister, UserLogin, TokenResponse, TokenRefresh, PasswordResetRequest, PasswordResetConfirm
)
from app.schemas.profile import (
    ProfileUpdate, ProfileResponse, AlumniDetailsResponse, MeResponse, ChooseRoleRequest
)
from app.schemas.opening import OpeningCreate, OpeningUpdate, OpeningResponse
from app.schemas.referral import ReferralCreate, ReferralStatusUpdate, ReferralResponse
from app.schemas.notification import NotificationResponse, PublicStatsResponse

__all__ = [
    "UserRegister", "UserLogin", "TokenResponse", "TokenRefresh", "PasswordResetRequest", "PasswordResetConfirm",
    "ProfileUpdate", "ProfileResponse", "AlumniDetailsResponse", "MeResponse", "ChooseRoleRequest",
    "OpeningCreate", "OpeningUpdate", "OpeningResponse",
    "ReferralCreate", "ReferralStatusUpdate", "ReferralResponse",
    "NotificationResponse", "PublicStatsResponse"
]
