# backend/api/user.py
from fastapi import APIRouter, status, HTTPException
from db.mongodb import get_database
from services.profile_service import upsert_profile

router = APIRouter(prefix="/user", tags=["User"])


@router.post("/registration", status_code=status.HTTP_201_CREATED)
async def register_user(data: dict):
    try:
        db = get_database()
        result = await upsert_profile(db, data)
        return {
            "message": "Profile saved",
            "data": result,  # { user_id, created, updated }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to save profile")