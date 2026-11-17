from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from app.schemas.opening import OpeningCreate, OpeningUpdate, OpeningResponse
from app.services.opening_service import OpeningService
from app.core.deps import get_opening_service, get_current_user, get_optional_user, require_role
from app.models.user import User

router = APIRouter(prefix="/openings", tags=["Job Openings"])

@router.get("/", response_model=List[OpeningResponse])
async def list_openings(
    domain: Optional[str] = Query(None),
    branch: Optional[str] = Query(None),
    company: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    current_user: Optional[User] = Depends(get_optional_user),
    service: OpeningService = Depends(get_opening_service)
):
    """Retrieves all active openings matching optional filter parameters."""
    return await service.get_all_openings(
        user=current_user,
        domain=domain,
        branch=branch,
        company=company,
        search=search
    )

@router.get("/{id}", response_model=OpeningResponse)
async def get_opening(id: str, service: OpeningService = Depends(get_opening_service)):
    """Retrieves a single opening by its ID."""
    return await service.get_opening(id)

@router.post("/", response_model=OpeningResponse, status_code=status.HTTP_201_CREATED)
async def create_opening(
    payload: OpeningCreate,
    current_user: User = Depends(require_role(["alumni", "admin"])),
    service: OpeningService = Depends(get_opening_service)
):
    """Allows approved alumni and committee admins to post a new opening."""
    return await service.create_opening(payload, current_user)

@router.put("/{id}", response_model=OpeningResponse)
async def update_opening(
    id: str,
    payload: OpeningUpdate,
    current_user: User = Depends(require_role(["alumni", "admin"])),
    service: OpeningService = Depends(get_opening_service)
):
    """Updates opening attributes (status, deadline, description)."""
    return await service.update_opening(id, payload, current_user)
