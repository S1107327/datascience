from pymongo import MongoClient
import re

class MongoDBConnector:
    def __init__(self):
        # Provide the mongodb atlas url to connect python to mongodb using pymongo
        self.CONNECTION_STRING = "localhost:27017"
        # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
        self.client = MongoClient(self.CONNECTION_STRING)

    def get_restaurant_names_list(self):
        restaurants = self.client['rasa_db']['restaurants'].find({}, {"name": 1})
        return restaurants

    def get_cuisines(self):
        cuisines = self.client['rasa_db']['restaurants'].find({}, {"cuisine": 1}).distinct('cuisine')
        return cuisines

    def get_restaurant_info(self, name):
        restaurant_info = self.client['rasa_db']['restaurants'].find_one({"name": re.compile(name, re.IGNORECASE)})
        return restaurant_info
