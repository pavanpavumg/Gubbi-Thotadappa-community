from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.deps import get_current_user, get_storage_service
from app.models.user import User, UserRole
from app.models.profile import Profile, AlumniDetails
from app.models.referral import ReferralRequest
from app.models.opening import Opening
from app.schemas.profile import ProfileUpdate, ProfileResponse, ChooseRoleRequest
from app.services.storage_service import StorageService

router = APIRouter(prefix="/profiles", tags=["Profiles"])

@router.get("/", response_model=ProfileResponse)
async def get_my_profile(current_user: User = Depends(get_current_user)):
    """Fetches the logged-in user's profile."""
    if not current_user.profile:
        raise HTTPException(status_code=404, detail="Profile not found.")
    return current_user.profile

@router.put("/", response_model=ProfileResponse)
async def update_my_profile(
    payload: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Updates user profile information."""
    profile = current_user.profile
    if not profile:
        profile = Profile(id=current_user.id, email=current_user.email)
        db.add(profile)

    update_data = payload.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(profile, field, val)

    await db.commit()
    await db.refresh(profile)
    return profile

@router.post("/resume", response_model=ProfileResponse)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    storage: StorageService = Depends(get_storage_service),
    db: AsyncSession = Depends(get_db)
):
    """Securely uploads and validates a PDF resume (max 5MB, verified magic bytes)."""
    saved_rel_path = await storage.save_resume(current_user.id, file)

    profile = current_user.profile
    profile.resume_path = saved_rel_path
    await db.commit()
    await db.refresh(profile)
    return profile

@router.get("/resume/{student_id}")
async def download_resume(
    student_id: str,
    current_user: User = Depends(get_current_user),
    storage: StorageService = Depends(get_storage_service),
    db: AsyncSession = Depends(get_db)
):
    """
    Downloads resume with IDOR check:
    Accessible ONLY by:
    1. The student owner
    2. Admins
    3. Alumni who received a referral request from this student
    """
    roles = [r.role for r in current_user.roles]
    is_admin = "admin" in roles
    is_owner = current_user.id == student_id

    # If not owner and not admin, check if alumni received application from student
    if not is_owner and not is_admin:
        stmt = (
            select(ReferralRequest)
            .join(Opening, Opening.id == ReferralRequest.opening_id)
            .where(
                ReferralRequest.student_id == student_id,
                Opening.alumni_id == current_user.id
            )
        )
        result = await db.execute(stmt)
        if not result.scalars().first():
            raise HTTPException(status_code=403, detail="Permission denied to access this student's resume.")

    stmt = select(Profile.resume_path).where(Profile.id == student_id)
    result = await db.execute(stmt)
    resume_path = result.scalar()

    if not resume_path:
        raise HTTPException(status_code=404, detail="Resume not found.")

    file_path = storage.get_file_path(resume_path)
    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename="resume.pdf"
    )

@router.post("/choose-role")
async def choose_role(
    payload: ChooseRoleRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Allows OAuth users without a role to select Student or Alumni."""
    if payload.role not in ["student", "alumni"]:
        raise HTTPException(status_code=400, detail="Invalid role choice.")

    roles = [r.role for r in current_user.roles]
    if roles:
        raise HTTPException(status_code=400, detail="Role already chosen.")

    role_entry = UserRole(user_id=current_user.id, role=payload.role)
    db.add(role_entry)

    if payload.details.get("name"):
        if current_user.profile:
            current_user.profile.name = payload.details["name"]

    if payload.role == "alumni":
        alumni = AlumniDetails(
            user_id=current_user.id,
            batch_year=int(payload.details.get("batch_year")) if payload.details.get("batch_year") else None,
            course=payload.details.get("course"),
            company=payload.details.get("company"),
            designation=payload.details.get("designation"),
            work_email=payload.details.get("work_email"),
            verified="pending"
        )
        db.add(alumni)

    await db.commit()
    return {"status": "ok"}
