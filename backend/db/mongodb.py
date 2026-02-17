from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from core.config import settings


class MongoDB:
    client: AsyncIOMotorClient | None = None
    db: AsyncIOMotorDatabase | None = None


mongodb = MongoDB()


async def connect_to_mongo():
    mongodb.client = AsyncIOMotorClient(settings.MONGODB_URL)
    mongodb.db = mongodb.client[settings.MONGODB_DB_NAME]

    # Email-keyed collections
    await mongodb.db["users"].create_index("email", unique=True)
    await mongodb.db["resumes"].create_index("email", unique=True)

    print(f"Connected to MongoDB at {settings.MONGODB_URL}")


async def close_mongo_connection():
    if mongodb.client:
        mongodb.client.close()
        print("Closed MongoDB connection")


def get_database() -> AsyncIOMotorDatabase:
    if mongodb.db is None:
        raise RuntimeError("MongoDB is not connected. Did you call connect_to_mongo() on startup?")
    return mongodb.db
