from fastapi import APIRouter, Depends, Header, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from db.mongodb import get_database
from models.user_repo import UserRepo
from models.resume_repo import ResumeRepo

router = APIRouter(prefix="/user", tags=["User"])


def _require_email_header(x_user_email: str | None) -> str:
    if not x_user_email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-User-Email header",
        )
    return x_user_email


def _enforce_same_user(caller_email: str, target_email: str) -> None:
    if caller_email.lower() != target_email.lower():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: email mismatch",
        )


@router.post("/registration", status_code=status.HTTP_200_OK)
async def register_user(
    data: dict,
    db: AsyncIOMotorDatabase = Depends(get_database),
    x_user_email: str | None = Header(default=None, alias="X-User-Email"),
):
    """
    Frontend submit-profile entrypoint.

    Behavior:
    - If user/profile does not exist -> create
    - If user/profile already exists -> update
    - Always return the latest stored profile
    """
    caller = _require_email_header(x_user_email)

    email = data.get("email")
    if not email or not isinstance(email, str):
        raise HTTPException(
            status_code=400,
            detail="Body must include a valid 'email' field (string).",
        )

    _enforce_same_user(caller, email)

    user_repo = UserRepo(db)
    resume_repo = ResumeRepo(db)

    # Optional user-level fields you want to keep in users collection
    # Add more fields here if frontend sends them
    user_extra = {}
    for key in ["name", "phone", "location"]:
        if key in data:
            user_extra[key] = data[key]

    # Upsert both collections
    user_doc = await user_repo.upsert(email=email, extra=user_extra)
    profile_doc = await resume_repo.upsert(email=email, payload=data)

    return {
        "message": "Profile submitted successfully",
        "email": email,
        "user": user_doc,
        "profile": profile_doc,
    }


@router.get("/profile/{email}")
async def get_profile(
    email: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    x_user_email: str | None = Header(default=None, alias="X-User-Email"),
):
    caller = _require_email_header(x_user_email)
    _enforce_same_user(caller, email)

    repo = ResumeRepo(db)
    doc = await repo.get(email)
    if not doc:
        raise HTTPException(status_code=404, detail="Profile not found")
    return doc


@router.delete("/profile/{email}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile(
    email: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    x_user_email: str | None = Header(default=None, alias="X-User-Email"),
):
    caller = _require_email_header(x_user_email)
    _enforce_same_user(caller, email)

    user_repo = UserRepo(db)
    resume_repo = ResumeRepo(db)

    deleted_resume = await resume_repo.delete(email)
    deleted_user = await user_repo.delete(email)

    if not deleted_resume and not deleted_user:
        raise HTTPException(status_code=404, detail="Nothing to delete (user/profile not found)")
    return None