import os
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = "tournament"

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

matches = db["matches"]
tournament_results = db["tournament_results"]
championship_results = db["championship_results"]

async def close_db():
    client.close()