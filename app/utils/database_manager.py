from pymongo import MongoClient
from app.config.config import MONGODB_URI, MONGODB_DB_NAME, MONGODB_COLLECTION_NAME


class DatabaseManager:
    def __init__(self):
        self.client = MongoClient(MONGODB_URI)
        self.db = self.client[MONGODB_DB_NAME]
        self.collection = self.db[MONGODB_COLLECTION_NAME]

    def close(self):
        self.client.close()


db_manager = DatabaseManager()