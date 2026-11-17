import os
import uuid
from pathlib import Path
from fastapi import UploadFile, HTTPException, status
from app.core.config import settings

class StorageService:
    """Service handling secure file storage and vulnerability defenses."""

    def __init__(self):
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    async def save_resume(self, user_id: str, file: UploadFile) -> str:
        # Defense 1: Check Content-Type & Extension
        if not file.filename or not file.filename.lower().endswith(".pdf"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file type. Only PDF files are permitted."
            )
        if file.content_type != "application/pdf":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="MIME type mismatch. File is not a valid PDF."
            )

        # Defense 2: Read contents and check magic bytes (%PDF-)
        content = await file.read()
        if not content.startswith(b"%PDF-"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File content does not match a valid PDF header."
            )

        # Defense 3: Enforce strict file size limit (5MB)
        if len(content) > settings.MAX_UPLOAD_SIZE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE_BYTES // (1024*1024)} MB."
            )

        # Defense 4: Path traversal prevention - UUID-based filename isolated per user
        user_dir = self.upload_dir / user_id
        user_dir.mkdir(parents=True, exist_ok=True)
        
        safe_filename = f"resume_{uuid.uuid4().hex[:12]}.pdf"
        target_path = user_dir / safe_filename

        with open(target_path, "wb") as f:
            f.write(content)

        # Return relative storage path
        return str(Path(user_id) / safe_filename).replace("\\", "/")

    def get_file_path(self, relative_path: str) -> Path:
        """Resolves file path while preventing directory traversal attacks."""
        target = (self.upload_dir / relative_path).resolve()
        # Ensure target is strictly within upload_dir
        if not str(target).startswith(str(self.upload_dir.resolve())):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Directory traversal detected."
            )
        if not target.is_file():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Requested file was not found."
            )
        return target
