from pymongo import MongoClient

class MongoDBConnector:
    def __init__(self):
        # Provide the mongodb atlas url to connect python to mongodb using pymongo
        self.CONNECTION_STRING = "localhost:27017"
        # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
        self.client = MongoClient(self.CONNECTION_STRING)

    def get_restaurant_names_list(self):
        restaurants = self.client['rasa_db']['restaurants'].find({}, {"name": 1})
        return restaurants

    def get_restaurant_info(self, name):
        restaurant_info = self.client['rasa_db']['restaurants'].find({"name": name}).distinct("name")
        return restaurant_info
