# backend/services/profile_service.py
from __future__ import annotations

from typing import Any, Dict, Optional
from uuid import uuid4
from datetime import datetime, timezone

from motor.motor_asyncio import AsyncIOMotorDatabase


PROFILES_COLLECTION = "profiles"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


async def upsert_profile(db: AsyncIOMotorDatabase, profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    Upserts by email (simple + practical for MVP).
    Returns { user_id, created, updated }.
    """
    email = (profile.get("personalInfo") or {}).get("email")
    if not email:
        raise ValueError("personalInfo.email is required")

    col = db[PROFILES_COLLECTION]

    existing = await col.find_one({"personalInfo.email": email}, {"user_id": 1})
    user_id = existing["user_id"] if existing and "user_id" in existing else str(uuid4())

    payload = {
        **profile,
        "user_id": user_id,
        "updated_at": _now_iso(),
    }

    # if first time, also store created_at
    if not existing:
        payload["created_at"] = _now_iso()

    await col.update_one(
        {"personalInfo.email": email},
        {"$set": payload},
        upsert=True,
    )

    return {"user_id": user_id, "created": existing is None, "updated": True}


async def get_profile_by_user_id(db: AsyncIOMotorDatabase, user_id: str) -> Optional[Dict[str, Any]]:
    col = db[PROFILES_COLLECTION]
    return await col.find_one({"user_id": user_id}, {"_id": 0})