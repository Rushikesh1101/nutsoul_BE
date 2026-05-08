import os
from pymongo import MongoClient
from pymongo.server_api import ServerApi


_DEFAULT_URI = "mongodb+srv://nutsoulbharat:nutsoul%40999@nutsoul.zumjlyt.mongodb.net/?appName=NutSoul"
_DEFAULT_DB = "NutSoul"

_client = None


def _get_client(uri):
    global _client
    if _client is None:
        _client = MongoClient(uri, server_api=ServerApi("1"))
    return _client


class MongoDB:
    def __init__(self, uri=None, db_name=None):
        self.uri = uri or os.getenv("MONGO_URI") or _DEFAULT_URI
        self.db_name = db_name or os.getenv("MONGO_DB_NAME") or _DEFAULT_DB

        self.client = _get_client(self.uri)
        self.db = self.client[self.db_name]

        self.users = self.db["users"]
        self.items = self.db["items"]
        self.cart = self.db["cart"]
        self.orders = self.db["orders"]
        self.address = self.db["address"]

    def close(self):
        # Connection is reused across invocations on serverless;
        # leave the singleton open so warm cold-starts stay fast.
        return
