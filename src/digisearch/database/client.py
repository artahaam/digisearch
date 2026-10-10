from pymongo import MongoClient
from digisearch.config import MONGO_DB, MONGO_URI

_client: MongoClient | None = None

def get_db_client() -> MongoClient:
    global _client
    if _client is None:
        _client = MongoClient(MONGO_URI)
    return _client

def get_db():
    return get_db_client()[MONGO_DB]
