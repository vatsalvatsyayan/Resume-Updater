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


@router.post("/registration", status_code=status.HTTP_201_CREATED)
async def register_user(
    data: dict,
    db: AsyncIOMotorDatabase = Depends(get_database),
    x_user_email: str | None = Header(default=None, alias="X-User-Email"),
):
    """
    Register a user and initialize their resume/profile.
    Expects JSON body with at least: { "email": "...", education/work_experience/projects/skills... }
    """
    caller = _require_email_header(x_user_email)

    email = data.get("email")
    if not email or not isinstance(email, str):
        raise HTTPException(status_code=400, detail="Body must include a valid 'email' field (string).")

    _enforce_same_user(caller, email)

    user_repo = UserRepo(db)
    resume_repo = ResumeRepo(db)

    # Create user if not exists (ignore duplicate)
    created_user = await user_repo.create(email=email)  # None if already exists

    # Create resume if not exists (ignore duplicate)
    created_resume = await resume_repo.create(email=email, payload=data)  # None if already exists

    # Return the current resume (source of truth)
    profile = await resume_repo.get(email=email)

    return {
        "message": "Registration successful" if (created_user or created_resume) else "Already registered",
        "email": email,
        "profile": profile,
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


@router.put("/profile/{email}")
async def replace_profile(
    email: str,
    data: dict,
    db: AsyncIOMotorDatabase = Depends(get_database),
    x_user_email: str | None = Header(default=None, alias="X-User-Email"),
):
    caller = _require_email_header(x_user_email)
    _enforce_same_user(caller, email)

    # Optional: enforce email in body if present
    if "email" in data and isinstance(data["email"], str) and data["email"].lower() != email.lower():
        raise HTTPException(status_code=400, detail="If provided, body.email must match path email")

    repo = ResumeRepo(db)
    updated = await repo.replace(email=email, payload=data, upsert=False)
    if not updated:
        raise HTTPException(status_code=404, detail="Profile not found")
    return updated


@router.patch("/profile/{email}")
async def patch_profile(
    email: str,
    patch: dict,
    db: AsyncIOMotorDatabase = Depends(get_database),
    x_user_email: str | None = Header(default=None, alias="X-User-Email"),
):
    caller = _require_email_header(x_user_email)
    _enforce_same_user(caller, email)

    repo = ResumeRepo(db)
    updated = await repo.patch(email=email, patch=patch)
    if not updated:
        raise HTTPException(status_code=404, detail="Profile not found")
    return updated


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

