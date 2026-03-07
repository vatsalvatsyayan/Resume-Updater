from fastapi import APIRouter, Depends, Header, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from db.mongodb import get_database
from models.application_repo import ApplicationRepo

router = APIRouter(prefix="/applications", tags=["Applications"])


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


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_application(
    data: dict,
    db: AsyncIOMotorDatabase = Depends(get_database),
    x_user_email: str | None = Header(default=None, alias="X-User-Email"),
):
    caller = _require_email_header(x_user_email)

    email = data.get("email")
    if not email or not isinstance(email, str):
        raise HTTPException(status_code=400, detail="Body must include a valid 'email' field")

    _enforce_same_user(caller, email)

    repo = ApplicationRepo(db)
    created = await repo.create(email=email, payload=data)
    return {
        "message": "Application created successfully",
        "application": created,
    }


@router.get("/{email}")
async def list_applications(
    email: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    x_user_email: str | None = Header(default=None, alias="X-User-Email"),
):
    caller = _require_email_header(x_user_email)
    _enforce_same_user(caller, email)

    repo = ApplicationRepo(db)
    docs = await repo.list_by_email(email)
    return {
        "email": email,
        "applications": docs,
    }


@router.get("/{email}/{application_id}")
async def get_application(
    email: str,
    application_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    x_user_email: str | None = Header(default=None, alias="X-User-Email"),
):
    caller = _require_email_header(x_user_email)
    _enforce_same_user(caller, email)

    repo = ApplicationRepo(db)
    doc = await repo.get_by_id(application_id, email)
    if not doc:
        raise HTTPException(status_code=404, detail="Application not found")
    return doc


@router.put("/{email}/{application_id}")
async def replace_application(
    email: str,
    application_id: str,
    data: dict,
    db: AsyncIOMotorDatabase = Depends(get_database),
    x_user_email: str | None = Header(default=None, alias="X-User-Email"),
):
    caller = _require_email_header(x_user_email)
    _enforce_same_user(caller, email)

    if "email" in data and isinstance(data["email"], str) and data["email"].lower() != email.lower():
        raise HTTPException(status_code=400, detail="If provided, body.email must match path email")

    repo = ApplicationRepo(db)
    updated = await repo.replace(application_id=application_id, email=email, payload=data)
    if not updated:
        raise HTTPException(status_code=404, detail="Application not found")
    return updated


@router.patch("/{email}/{application_id}")
async def patch_application(
    email: str,
    application_id: str,
    patch: dict,
    db: AsyncIOMotorDatabase = Depends(get_database),
    x_user_email: str | None = Header(default=None, alias="X-User-Email"),
):
    caller = _require_email_header(x_user_email)
    _enforce_same_user(caller, email)

    repo = ApplicationRepo(db)
    updated = await repo.patch(application_id=application_id, email=email, patch=patch)
    if not updated:
        raise HTTPException(status_code=404, detail="Application not found")
    return updated


@router.delete("/{email}/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_application(
    email: str,
    application_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    x_user_email: str | None = Header(default=None, alias="X-User-Email"),
):
    caller = _require_email_header(x_user_email)
    _enforce_same_user(caller, email)

    repo = ApplicationRepo(db)
    deleted = await repo.delete(application_id=application_id, email=email)
    if not deleted:
        raise HTTPException(status_code=404, detail="Application not found")
    return None
