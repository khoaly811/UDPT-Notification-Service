from pymongo import MongoClient
from config.settings import settings

mongo_cfg = settings.mongo
client = MongoClient(
    host=mongo_cfg.host,
    port=mongo_cfg.port,
    username=mongo_cfg.username,
    password=mongo_cfg.password
)
db = client[mongo_cfg.database]
collection = db["notifications"]

class NotificationRepository:
    @staticmethod
    def save(notification: dict):
        result = collection.insert_one(notification)
        return str(result.inserted_id)

    @staticmethod
    def find_by_user(user_id: int):
        docs = collection.find({"user_id": user_id}).sort("created_at", -1)
        return list(docs)

    @staticmethod
    def mark_as_read(notification_id: str):
        from bson import ObjectId
        collection.update_one({"_id": ObjectId(notification_id)}, {"$set": {"status": "READ"}})
