from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import AsyncMongoClient

#MONGO_URL = "mongodb://localhost:27017"
MONGO_URL = "mongodb+srv://cesarenappa_db_user:ogGknHucqHIWqAhi@apipublishers.qzfrfsp.mongodb.net/?appName=APIpublishers"
DB_NAME = "tournament"
COOKIE_SECRET = "super_secret_key_change_me"
PORT = 8888

#client = AsyncIOMotorClient(MONGO_URL)
client = AsyncMongoClient(MONGO_URL)
db = client[DB_NAME]

matches = db["matches"]
tournament_results = db["tournament_results"]
championship_results = db["championship_results"]
