from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ReturnDocument


class ApplicationRepo:
    """
    DB-only repository for job applications.
    Collection: applications
    One user can have many application documents.
    """

    def __init__(self, db: AsyncIOMotorDatabase, collection_name: str = "applications"):
        self.col = db[collection_name]

    @staticmethod
    def _utc_now() -> datetime:
        return datetime.now(timezone.utc)

    @staticmethod
    def _serialize_id(doc: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if not doc:
            return None
        if "_id" in doc:
            doc["_id"] = str(doc["_id"])
        return doc

    @staticmethod
    def _normalize_payload(email: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert frontend modal payload into Mongo-friendly schema.
        Frontend sends camelCase:
          - companyName
          - roleName
          - jobDescription
        """
        now = datetime.now(timezone.utc)

        return {
            "email": email,
            "company_name": payload.get("companyName", "").strip(),
            "role_name": payload.get("roleName", "").strip(),
            "job_description": payload.get("jobDescription", "").strip(),
            "status": payload.get("status", "draft"),
            "created_at": now,
            "updated_at": now,
        }

    async def create(self, email: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        doc = self._normalize_payload(email, payload)
        result = await self.col.insert_one(doc)
        doc["_id"] = str(result.inserted_id)
        return doc

    async def list_by_email(self, email: str) -> List[Dict[str, Any]]:
        docs = await self.col.find({"email": email}).sort("updated_at", -1).to_list(length=200)
        return [self._serialize_id(doc) for doc in docs]

    async def get_by_id(self, application_id: str, email: str) -> Optional[Dict[str, Any]]:
        if not ObjectId.is_valid(application_id):
            return None

        doc = await self.col.find_one(
            {"_id": ObjectId(application_id), "email": email}
        )
        return self._serialize_id(doc)

    async def replace(self, application_id: str, email: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if not ObjectId.is_valid(application_id):
            return None

        existing = await self.col.find_one({"_id": ObjectId(application_id), "email": email})
        if not existing:
            return None

        new_doc = self._normalize_payload(email, payload)
        new_doc["created_at"] = existing.get("created_at", self._utc_now())
        new_doc["updated_at"] = self._utc_now()

        updated = await self.col.find_one_and_update(
            {"_id": ObjectId(application_id), "email": email},
            {"$set": new_doc},
            return_document=ReturnDocument.AFTER,
        )
        return self._serialize_id(updated)

    async def patch(self, application_id: str, email: str, patch: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if not ObjectId.is_valid(application_id):
            return None

        allowed_map = {
            "companyName": "company_name",
            "roleName": "role_name",
            "jobDescription": "job_description",
            "status": "status",
        }

        update_fields: Dict[str, Any] = {}
        for frontend_key, db_key in allowed_map.items():
            if frontend_key in patch:
                value = patch[frontend_key]
                if isinstance(value, str):
                    value = value.strip()
                update_fields[db_key] = value

        if not update_fields:
            return await self.get_by_id(application_id, email)

        update_fields["updated_at"] = self._utc_now()

        updated = await self.col.find_one_and_update(
            {"_id": ObjectId(application_id), "email": email},
            {"$set": update_fields},
            return_document=ReturnDocument.AFTER,
        )
        return self._serialize_id(updated)

    async def delete(self, application_id: str, email: str) -> bool:
        if not ObjectId.is_valid(application_id):
            return False

        res = await self.col.delete_one({"_id": ObjectId(application_id), "email": email})
        return res.deleted_count == 1
