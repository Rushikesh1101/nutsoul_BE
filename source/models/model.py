import os
import certifi
from pymongo import MongoClient
from pymongo.server_api import ServerApi


_DEFAULT_DB = "NutSoul"

_client = None


def _get_client(uri):
    global _client
    if _client is None:
        _client = MongoClient(
            uri,
            server_api=ServerApi("1"),
            tlsCAFile=certifi.where(),
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=10000,
            retryWrites=True,
        )
    return _client


class MongoDB:
    def __init__(self, uri=None, db_name=None):
        self.uri = uri or os.getenv("MONGO_URI")
        if not self.uri:
            raise RuntimeError("MONGO_URI environment variable is not set")
        self.db_name = db_name or os.getenv("MONGO_DB_NAME") or _DEFAULT_DB

        self.client = _get_client(self.uri)
        self.db = self.client[self.db_name]

        self.users = self.db["users"]
        self.items = self.db["items"]
        self.cart = self.db["cart"]
        self.orders = self.db["orders"]
        self.address = self.db["address"]

    def close(self):
        return
