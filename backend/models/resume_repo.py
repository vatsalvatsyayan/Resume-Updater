from __future__ import annotations

from typing import Any, Dict, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError


class ResumeRepo:
    """
    DB-only repository.
    Collection: resumes
    Key: email (unique)
    Document fields: education, work_experience, projects, skills (JSON-friendly).
    """

    def __init__(self, db: AsyncIOMotorDatabase, collection_name: str = "resumes"):
        self.col = db[collection_name]

    @staticmethod
    def _normalize_payload(email: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        # Keep Mongo schema stable: always store lists for these fields.
        return {
            "email": email,
            "education": payload.get("education", []),
            "work_experience": payload.get("work_experience", []),
            "projects": payload.get("projects", []),
            "skills": payload.get("skills", []),
        }

    async def create(self, email: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create a new resume for email. Returns doc (without _id) or None if duplicate.
        """
        doc = self._normalize_payload(email, payload)
        try:
            await self.col.insert_one(doc)
        except DuplicateKeyError:
            return None
        doc.pop("_id", None)
        return doc

    async def get(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Read resume by email. Returns doc (without _id) or None.
        """
        return await self.col.find_one({"email": email}, {"_id": 0})

    async def replace(self, email: str, payload: Dict[str, Any], upsert: bool = False) -> Optional[Dict[str, Any]]:
        """
        Replace entire resume document. If upsert=True, create if missing.
        Returns updated doc (without _id), or None if missing and upsert=False.
        """
        doc = self._normalize_payload(email, payload)

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
        Partial update. Only updates allowed fields if present in patch.
        Returns updated doc (without _id) or None if not found.
        """
        allowed = {"education", "work_experience", "projects", "skills"}
        update_fields = {k: v for k, v in patch.items() if k in allowed}

        if not update_fields:
            return await self.get(email)

        updated = await self.col.find_one_and_update(
            {"email": email},
            {"$set": update_fields},
            projection={"_id": 0},
            return_document=ReturnDocument.AFTER,
        )
        return updated

    async def delete(self, email: str) -> bool:
        """
        Delete by email. Returns True if deleted.
        """
        res = await self.col.delete_one({"email": email})
        return res.deleted_count == 1

