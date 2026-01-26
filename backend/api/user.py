from fastapi import APIRouter, status

router = APIRouter(prefix="/user", tags=["User"])


@router.post("/registration", status_code=status.HTTP_201_CREATED)
async def register_user(data: dict):
    print("Received registration data:")
    print(data)
    return {
        "message": "Registration data received",
        "data": data
    }
