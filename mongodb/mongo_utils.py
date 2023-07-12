from pymongo import MongoClient
from datetime import datetime
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

    def get_restaurants_ordered_by_score(self):
        restaurants_ordered_by_avg_score = self.client['rasa_db']['restaurants'].aggregate([{ "$unwind": "$reviews" },
                                                                                            { "$group": { "_id": "$name", "avgScore": { "$avg": "$reviews.score" }}},
                                                                                            { "$sort": {"avgScore": -1}}])
        return restaurants_ordered_by_avg_score


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

    def get_restaurant_of_borough(self, borough):
        restaurant_borough = self.client['rasa_db']['restaurants'].find({"borough": re.compile(borough, re.IGNORECASE)})
        count = self.client['rasa_db']['restaurants'].count_documents({"borough": re.compile(borough, re.IGNORECASE)})
        return restaurant_borough, count


    def get_client_reservations(self, phone_number, active=True):
        reservations = self.client['rasa_db']['reservation'].find({"phone_number": phone_number})
        list_reservation = list(reservations)
        if active:
            active_reservation = list(filter(lambda x: datetime.strptime(x['date'], "%Y-%m-%d") >= datetime.today(), list_reservation))
            return active_reservation
        else:
            past_reservation = list(filter(lambda x: datetime.strptime(x['date'], "%Y-%m-%d") < datetime.today(), list_reservation))
            return past_reservation
    
    ##TODO: Recupero della collezione dal documento (SOLO SE SI MODIFICA SOTTO)
    ##TODO: prenderne 10
    def get_restaurant_reviews(self, name, limit=True):
        reviews = []
        if limit:
            restaurant_reviews = self.client['rasa_db']['restaurants'].aggregate([{"$match": {"name": re.compile(name, re.IGNORECASE)}},
                                                                                  {"$unwind": "$reviews" },
                                                                                  {"$sort": {"reviews.date_review": -1}},
                                                                                  {"$project": {"reviews":1}},
                                                                                  {"$limit": 5}])
        else:
            restaurant_reviews = self.client['rasa_db']['restaurants'].aggregate([{"$match": {"name": re.compile(name, re.IGNORECASE)}},
                                                                                  {"$unwind": "$reviews"},
                                                                                  {"$sort": {"reviews.date_review": -1}},
                                                                                  {"$project": {"reviews": 1}}])
        for review in restaurant_reviews:
            reviews.append(review['reviews'])
        return reviews

    def save_reservation(self, name, reservation):
        restaurant = self.client['rasa_db']['restaurants'].find_one({"name": re.compile(name, re.IGNORECASE)},{"_id":0,'restaurant_id':1, "name":1})
        reservation['restaurant_id'] = restaurant['restaurant_id']
        reservation['restaurant_name'] = restaurant['name']
        collection=self.client['rasa_db']["reservation"]
        collection.insert_one(reservation)

    def save_review(self, name, review):
        restaurant = self.client['rasa_db']['restaurants'].find_one({"name": re.compile(name, re.IGNORECASE)},{"_id":0,'restaurant_id':1, "name":1, "reviews":1})
        collection = self.client['rasa_db']["restaurants"]
        collection.update_one({"restaurant_id": restaurant['restaurant_id']}, {"$push": {"reviews": review}})

