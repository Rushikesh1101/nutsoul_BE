from pymongo import MongoClient
import os
import certifi


class MongoDB:
    def __init__(self, uri=None, db_name=None):
        self.uri = "mongodb+srv://nutsoulbharat:nutsoul%40999@nutsoul.zumjlyt.mongodb.net/nutsoul?retryWrites=true&w=majority"
        self.db_name = "NutSoul"
        self.client = MongoClient(
            self.uri,
            tls=True,
            tlsCAFile=certifi.where(),
            serverSelectionTimeoutMS=30000,
            connectTimeoutMS=30000,
            socketTimeoutMS=30000,
            retryWrites=True,
        )
        self.db = self.client[self.db_name]

        self.users = self.db["users"]
        self.items = self.db["items"]
        self.cart = self.db["cart"]
        self.orders = self.db["orders"]
        self.address = self.db["address"]

    def close(self):
        if self.client:
            self.client.close()
