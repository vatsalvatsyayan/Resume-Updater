from __future__ import annotations

from typing import Any, Dict, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import DuplicateKeyError


class UserRepo:
    """
    DB-only repository for users.
    Collection: users
    Key: email (unique)
    """

    def __init__(self, db: AsyncIOMotorDatabase, collection_name: str = "users"):
        self.col = db[collection_name]

    async def create(self, email: str, extra: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        doc: Dict[str, Any] = {"email": email}
        if extra:
            doc.update(extra)

        try:
            await self.col.insert_one(doc)
        except DuplicateKeyError:
            return None

        doc.pop("_id", None)
        return doc

    async def get(self, email: str) -> Optional[Dict[str, Any]]:
        return await self.col.find_one({"email": email}, {"_id": 0})

    async def delete(self, email: str) -> bool:
        res = await self.col.delete_one({"email": email})
        return res.deleted_count == 1

