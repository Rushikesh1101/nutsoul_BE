from pymongo import MongoClient
from pymongo.server_api import ServerApi
import os
import certifi


class MongoDB:
    def __init__(self, uri=None, db_name=None):
        self.uri = (
            "mongodb+srv://nutsoulbharat:nutsoul%40999@nutsoul.zumjlyt.mongodb.net/"
        )
        self.db_name = "NutSoul"
        self.client = MongoClient(self.uri, server_api=ServerApi("1"))
        self.db = self.client[self.db_name]

        self.users = self.db["users"]
        self.items = self.db["items"]
        self.cart = self.db["cart"]
        self.orders = self.db["orders"]
        self.address = self.db["address"]

    def close(self):
        if self.client:
            self.client.close()
