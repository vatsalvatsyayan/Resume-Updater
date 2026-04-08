import logging

from fastapi import APIRouter, Body, Depends, File, Form, Header, HTTPException, UploadFile, status
from pydantic import ValidationError

from db.mongodb import get_database
from models.resume_repo import ResumeRepo
from models.user_repo import UserRepo
from schemas.profile import ResumeProfile
from schemas.profile_import import ProfileImportResponse
from services.profile_import_service import ProfileImportService

router = APIRouter(prefix="/user", tags=["User"])
profile_import_service = ProfileImportService()

def _require_email_header(x_user_email: str | None) -> str:
    if not x_user_email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing X-User-Email header")
    return x_user_email

def _enforce_same_user(caller_email: str, target_email: str) -> None:
    if caller_email.lower() != target_email.lower():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden: email mismatch")

@router.post("/registration", status_code=status.HTTP_200_OK)
async def register_user(
    payload: dict = Body(...),
    db = Depends(get_database),
    x_user_email: str | None = Header(default=None, alias="X-User-Email"),
):
    logger = logging.getLogger("uvicorn.error")

    # 1) require header and inject email into payload if missing
    caller = _require_email_header(x_user_email)
    # Work with the original payload from the frontend (camelCase keys) — don't convert to snake_case here.
    profile_dict = payload or {}

    # ensure some optional collections exist so model won't error on missing keys
    profile_dict.setdefault("education", [])
    profile_dict.setdefault("workExperience", [])
    profile_dict.setdefault("projects", [])
    profile_dict.setdefault("certifications", [])
    profile_dict.setdefault("volunteer", [])
    profile_dict.setdefault("leadership", [])
    profile_dict.setdefault("skills", {
        "programmingLanguages": [],
        "frameworks": [],
        "databases": [],
        "toolsAndTechnologies": [],
        "cloud": [],
        "ai": [],
        "other": [],
    })

    # If frontend omitted top-level email, inject from header before validation
    if not profile_dict.get("email"):
        profile_dict["email"] = caller
    # Also ensure a user_id exists (frontend might set user_id, but use email if not)
    if not profile_dict.get("user_id"):
        profile_dict["user_id"] = profile_dict["email"]

    # 2) Validate using Pydantic model — the model uses camelCase aliases so give it the original frontend payload
    try:
        # Prefer model_validate (pydantic v2) if available:
        if hasattr(ResumeProfile, "model_validate"):
            profile = ResumeProfile.model_validate(profile_dict)
        else:
            profile = ResumeProfile.parse_obj(profile_dict)
    except ValidationError as exc:
        logger.error("ResumeProfile validation failed. payload: %s errors: %s", profile_dict, getattr(exc, "errors", str(exc)))
        # return pydantic errors as 422
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=exc.errors() if hasattr(exc, "errors") else str(exc))

    # enforce caller matches validated profile.email
    _enforce_same_user(caller, profile.email)

    # 3) upsert user and resume via instantiated repos (pass db to constructor)
    user_repo = UserRepo(db)
    resume_repo = ResumeRepo(db)

    # When storing into DB, dump model to snake_case (field names) for internal storage:
    payload_for_db = profile.model_dump(by_alias=False)  # snake_case keys
    if not payload_for_db.get("user_id"):
        payload_for_db["user_id"] = profile.email

    user_doc = await user_repo.upsert(email=profile.email, extra={"name": getattr(profile.personal_info, "full_name", None)})
    profile_doc = await resume_repo.upsert(email=profile.email, payload=payload_for_db)

    # For the response to frontend, give camelCase keys (aliases) so frontend can re-use response to auto-fill
    profile_for_frontend = profile.model_dump(by_alias=True)

    return {
        "message": "Profile submitted successfully",
        "email": profile.email,
        "user": user_doc,
        "profile": profile_for_frontend,
    }

# --- GET endpoint: return camelCase aliases so frontend can auto-fill directly ---
@router.get("/profile/{email}")
async def get_profile(email: str, db = Depends(get_database), x_user_email: str | None = Header(default=None, alias="X-User-Email")):
    caller = _require_email_header(x_user_email)
    _enforce_same_user(caller, email)
    repo = ResumeRepo(db)
    profile_doc = await repo.get(email)
    if not profile_doc:
        raise HTTPException(status_code=404, detail="Profile not found")
    # Validate (or parse) DB doc into model instance and return alias'ed dict
    try:
        if hasattr(ResumeProfile, "model_validate"):
            profile = ResumeProfile.model_validate(profile_doc)
        else:
            profile = ResumeProfile.parse_obj(profile_doc)
    except ValidationError:
        # if DB has slightly different shape, you can optionally return it as-is; but better to normalize
        return profile_doc
    return profile.model_dump(by_alias=True)


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
