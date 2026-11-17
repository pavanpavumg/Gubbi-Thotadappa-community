from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.notification import NotificationResponse, PublicStatsResponse
from app.repositories.notification_repo import NotificationRepository
from app.core.deps import get_current_user, get_db
from app.models.user import User

router = APIRouter(prefix="/notifications", tags=["Notifications & Stats"])

@router.get("/", response_model=List[NotificationResponse])
async def get_notifications(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Returns the most recent 30 notifications for the authenticated user."""
    repo = NotificationRepository(db)
    return await repo.get_by_user(current_user.id)

@router.patch("/mark-read")
async def mark_all_read(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Marks all unread notifications as read."""
    repo = NotificationRepository(db)
    await repo.mark_all_read(current_user.id)
    return {"status": "ok"}

@router.get("/public-stats", response_model=PublicStatsResponse)
async def get_public_stats(db: AsyncSession = Depends(get_db)):
    """Returns public aggregated metrics for the landing page."""
    repo = NotificationRepository(db)
    return await repo.get_public_stats()
