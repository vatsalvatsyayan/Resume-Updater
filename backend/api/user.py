from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from schemas.profile_import import ProfileImportResponse
from services.profile_import_service import ProfileImportService

router = APIRouter(prefix="/user", tags=["User"])
profile_import_service = ProfileImportService()


@router.post("/registration", status_code=status.HTTP_201_CREATED)
async def register_user(data: dict):
    print("Received registration data:")
    print(data)
    return {"message": "Registration data received", "data": data}


@router.post(
    "/profile-import",
    response_model=ProfileImportResponse,
    status_code=status.HTTP_200_OK,
)
async def import_profile(
    resume_file: UploadFile | None = File(default=None),
    resume_text: str | None = Form(default=None),
):
    if not any([resume_file, resume_text]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide a resume file or resume text.",
        )

    data, warnings, sources = await profile_import_service.import_profile(
        resume_file=resume_file,
        resume_text=resume_text,
    )

    return ProfileImportResponse(
        message="Profile data imported successfully.",
        data=data,
        warnings=warnings,
        sources=sources,
    )
