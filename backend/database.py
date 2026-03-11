from motor.motor_asyncio import AsyncIOMotorClient
from config import get_settings

settings = get_settings()

client: AsyncIOMotorClient = None
db = None


async def connect_db():
    global client, db
    client = AsyncIOMotorClient(settings.mongodb_url)
    db = client[settings.database_name]
    # Drop stale geo index on plain `location` field if it exists
    try:
        await db.crimes.drop_index("location_2dsphere")
    except Exception:
        pass
    # Create indexes
    await db.crimes.create_index([("location_point", "2dsphere")])
    await db.crimes.create_index([("category", 1)])
    await db.crimes.create_index([("created_at", -1)])
    await db.users.create_index([("email", 1)], unique=True)
    await db.users.create_index([("username", 1)], unique=True)
    await db.notes.create_index([("crime_id", 1)])
    print("✅ Connected to MongoDB Atlas")


async def close_db():
    global client
    if client:
        client.close()
        print("🔌 Disconnected from MongoDB")


def get_db():
    return db
