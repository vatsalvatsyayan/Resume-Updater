# models/resume_repo.py  (replace existing class with this implementation)
from __future__ import annotations
from typing import Any, Dict, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError
from datetime import datetime

DEFAULT_SKILLS = {
    "programming_languages": [],
    "frameworks": [],
    "databases": [],
    "tools": [],
    "cloud": [],
    "ai_ml": [],
    "other": [],
}

class ResumeRepo:
    def __init__(self, db: AsyncIOMotorDatabase, collection_name: str = "resumes"):
        self.col = db[collection_name]

    @staticmethod
    def _ensure_defaults(payload: Dict[str, Any]) -> Dict[str, Any]:

        # define this FIRST (outside the dict)
        vol_list = payload.get(
            "volunteer_experience",
            payload.get("volunteer", [])
        )

        doc = {
            "user_id": payload.get("user_id") or payload.get("email"),
            "email": payload.get("email"),
            "personal_info": payload.get("personal_info", {"full_name": "", "email": payload.get("email")}),
            "education": payload.get("education", []),
            "work_experience": payload.get("work_experience", []),
            "projects": payload.get("projects", []),
            "skills": payload.get("skills", DEFAULT_SKILLS.copy()),
            "certifications": payload.get("certifications", []),

            # now use the variable
            "volunteer_experience": vol_list,
            "volunteer": vol_list,  # <-- THIS is the added line

            "leadership_experience": payload.get("leadership_experience", []),
        }

        return doc

    async def create(self, email: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        doc = self._ensure_defaults(payload)
        doc["created_at"] = datetime.utcnow().isoformat()
        doc["updated_at"] = doc["created_at"]
        try:
            await self.col.insert_one(doc)
        except DuplicateKeyError:
            return None
        doc.pop("_id", None)
        return doc

    async def get(self, email: str) -> Optional[Dict[str, Any]]:
        return await self.col.find_one({"email": email}, {"_id": 0})

    async def upsert(self, email: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        # Upsert full profile (replace/merge as desired). We will set defaults for missing sections.
        doc = self._ensure_defaults(payload)
        now = datetime.utcnow().isoformat()
        doc["updated_at"] = now
        # If profile does not exist, set created_at
        updated = await self.col.find_one_and_update(
            {"email": email},
            {"$set": doc, "$setOnInsert": {"created_at": now}},
            projection={"_id": 0},
            return_document=ReturnDocument.AFTER,
            upsert=True,
        )
        return updated

    async def replace(self, email: str, payload: Dict[str, Any], upsert: bool = False) -> Optional[Dict[str, Any]]:
        doc = self._ensure_defaults(payload)
        now = datetime.utcnow().isoformat()
        doc["updated_at"] = now
        if upsert:
            doc.setdefault("created_at", now)
        updated = await self.col.find_one_and_update(
            {"email": email},
            {"$set": doc},
            projection={"_id": 0},
            return_document=ReturnDocument.AFTER,
            upsert=upsert,
        )
        return updated

    async def patch(self, email: str, patch: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Partial update. Accepts keys that are top-level document fields:
        personal_info, education, work_experience, projects, skills,
        certifications, volunteer_experience, leadership_experience.
        """
        allowed = {
            "personal_info",
            "education",
            "work_experience",
            "projects",
            "skills",
            "certifications",
            "volunteer_experience",   # keep for backwards compatibility
            "volunteer",              # add this so patching 'volunteer' works
            "leadership_experience",
        }
        update_fields = {k: v for k, v in patch.items() if k in allowed}
        if not update_fields:
            return await self.get(email)
        update_fields["updated_at"] = datetime.utcnow().isoformat()

        updated = await self.col.find_one_and_update(
            {"email": email},
            {"$set": update_fields},
            projection={"_id": 0},
            return_document=ReturnDocument.AFTER,
        )
        return updated

    async def delete(self, email: str) -> bool:
        res = await self.col.delete_one({"email": email})
        return res.deleted_count == 1