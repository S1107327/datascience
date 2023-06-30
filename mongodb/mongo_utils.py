from pymongo import MongoClient

class MongoDBConnector:
    def __init__(self):
        # Provide the mongodb atlas url to connect python to mongodb using pymongo
        self.CONNECTION_STRING = "localhost:27017"
        # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
        self.client = MongoClient(self.CONNECTION_STRING)

    def get_restaurant_list(self):
        restaurants = self.client['rasa_db']['restaurants'].find().limit(5)
        return restaurants

    def save_reservation(self, reservation):
        restaurant_name = reservation['restaurant_name']
        restaurant_id = self.client['rasa_db']['restaurants'].find_one({"name":restaurant_name},{"_id":0,'restaurant_id':1})
        reservation['restaurant_id'] = restaurant_id['restaurant_id']
        collection=self.client['rasa_db']["reservation"]
        collection.insert_one(reservation)


