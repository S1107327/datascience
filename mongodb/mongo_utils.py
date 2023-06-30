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
    #TODO: inserire metodo per prendere i primi cinque ristoranti per valutazione media
    def get_cuisines(self):
        cuisines = self.client['rasa_db']['restaurants'].find({}, {"cuisine": 1}).distinct('cuisine')
        return cuisines

    def get_restaurant_info(self, name):
        restaurant_info = self.client['rasa_db']['restaurants'].find_one({"name": re.compile(name, re.IGNORECASE)})
        return restaurant_info

    def get_restaurant_of_cuisine(self, cuisine):
        restaurant_cuisine = self.client['rasa_db']['restaurants'].find({"cuisine": re.compile(cuisine, re.IGNORECASE)})
        count = self.client['rasa_db']['restaurants'].count_documents({"cuisine": re.compile(cuisine, re.IGNORECASE)})
        return restaurant_cuisine, count

    def get_active_client_reservations(self, phone_number):
        reservations = self.client['rasa_db']['reservation'].find({"phone_number": phone_number})
        return reservations

    def save_reservation(self, name, reservation):
        restaurant = self.client['rasa_db']['restaurants'].find_one({"name": re.compile(name, re.IGNORECASE)},{"_id":0,'restaurant_id':1, "name":1})
        reservation['restaurant_id'] = restaurant['restaurant_id']
        reservation['restaurant_name'] = restaurant['name']
        collection=self.client['rasa_db']["reservation"]
        collection.insert_one(reservation)
