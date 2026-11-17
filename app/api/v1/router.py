from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.profiles import router as profiles_router
from app.api.v1.openings import router as openings_router
from app.api.v1.referrals import router as referrals_router
from app.api.v1.notifications import router as notifications_router
from app.api.v1.admin import router as admin_router

api_v1_router = APIRouter(prefix="/api/v1")

api_v1_router.include_router(auth_router)
api_v1_router.include_router(profiles_router)
api_v1_router.include_router(openings_router)
api_v1_router.include_router(referrals_router)
api_v1_router.include_router(notifications_router)
api_v1_router.include_router(admin_router)
