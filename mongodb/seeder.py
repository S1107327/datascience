from mongo_utils import MongoDBConnector
from random import randint
from datetime import date
def seeding_no_places(connection: MongoDBConnector):
    restaurants = connection.client['rasa_db']['restaurants'].find({}, {"_id": 0, 'restaurant_id': 1, "name": 1})
    for restaurant in restaurants:
        connection.client['rasa_db']['restaurants'].update_one({"restaurant_id": restaurant['restaurant_id']}, {"max_availabilty": randint(20,150)})

def seeding_reviews(connection: MongoDBConnector):
    restaurants = connection.client['rasa_db']['restaurants'].find({},{"_id":0,'restaurant_id':1, "name":1})
    for restaurant in restaurants:
        reviews = []
        for i in range(1, 11):
            review = dict()
            review['score'] = randint(1,5)
            review['body'] = f"Utente{i} Test Review"
            review['date_review'] = date(2023, 6, randint(1,30)).strftime("%d-%m-%Y")
            review['name'] = f"Utente{i}"
            reviews.append(review)
        connection.client['rasa_db']['restaurants'].update_one({"restaurant_id": restaurant['restaurant_id']}, {"$set": {"reviews": reviews}})

def seeding_reservations(connection: MongoDBConnector):
    collection = connection.client['rasa_db']["reservation"]
    phone_numbers = ["3456789000", "3342176895"]
    for phone_number in phone_numbers:
        for i in range(1,4):
            reservation = dict()
            reservation['people_number'] = randint(1,4)
            if i == 3:
                reservation['date'] = date(2023, 7, randint(6,30)).strftime("%d-%m-%Y")
            else:
                reservation['date'] = date(2023, 6, randint(1, 30)).strftime("%d-%m-%Y")
            reservation['time'] = "19:00"
            reservation['allergies'] = "no"
            reservation['name'] = "Utente1" if phone_number == phone_numbers[0] else "Utente2"
            reservation['phone_number'] = phone_number

            collection.insert_one(reservation)

if __name__ == "__main__":
    client = MongoDBConnector()
    seeding_reviews(client)
    #seeding_reservations(client)