# scripts/migrate_resumes.py
from pymongo import MongoClient
from datetime import datetime
from core.config import settings

client = MongoClient(settings.MONGODB_URL)
db = client[settings.MONGODB_DB_NAME]
col = db["resumes"]

DEFAULT_SKILLS = {
    "programming_languages": [],
    "frameworks": [],
    "databases": [],
    "tools": [],
    "cloud": [],
    "ai_ml": [],
    "other": [],
}

count = 0
for doc in col.find({}):
    updates = {}
    if "personal_info" not in doc:
        updates["personal_info"] = {"full_name": "", "email": doc.get("email", "")}
    for arr in ("education", "work_experience", "projects", "certifications", "volunteer_experience", "leadership_experience"):
        if arr not in doc:
            updates[arr] = []
    if "skills" not in doc:
        updates["skills"] = DEFAULT_SKILLS.copy()
    if "user_id" not in doc:
        updates["user_id"] = doc.get("email")
    if "created_at" not in doc:
        updates["created_at"] = datetime.utcnow().isoformat()
    updates["updated_at"] = datetime.utcnow().isoformat()
    if updates:
        col.update_one({"_id": doc["_id"]}, {"$set": updates})
        count += 1

print(f"Migration complete. Updated {count} documents.")
