# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

# This is a simple example for a custom action which utters "Hello World!"

# from typing import Any, Text, Dict, List
#
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []
import json
import sys
sys.path.append("../")
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from typing import Any, Text, Dict, List
from mongodb.mongo_utils import MongoDBConnector
from rasa_sdk.events import AllSlotsReset, SlotSet

class ActionShowRestaurant(Action):
    def name(self) -> Text:
        return "action_restaurant_list"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        mongo_db = MongoDBConnector()
        restaurant_json = mongo_db.get_restaurant_list()
        mydict = dict()
        i = 1
        for restaurant in restaurant_json:
            address_dict = {"building": restaurant["address"]["building"],
                            "coord:": f"lat: {restaurant['address']['coord'][0]} lon: {restaurant['address']['coord'][1]}",
                            "street": restaurant["address"]["street"],
                            "zipcode": restaurant["address"]["zipcode"]}
            mydict[i] = {"name": restaurant['name'],
                           "borough": restaurant['borough'],
                           "address": f"{address_dict['street']}, {address_dict['zipcode']}, in building {address_dict['building']}",
                           "cuisine": restaurant["cuisine"]}
            i += 1
        restaurants = json.dumps(mydict, indent=2, sort_keys=True)
        dispatcher.utter_message(text=restaurants)

        return []

class ActionReserveTable(Action):
    def name(self) -> Text:
        return "action_reserve_table"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        mongo_db = MongoDBConnector()
        reservation = {}
        reservation['restaurant_name'] = tracker.get_slot("restaurant_name")
        reservation['people_number'] = tracker.get_slot("people_number")
        reservation['date'] = tracker.get_slot("date")
        reservation['time'] = tracker.get_slot("time")
        reservation['allergies'] = tracker.get_slot("allergies")
        reservation['name'] = tracker.get_slot("name")
        reservation['phone_number'] = tracker.get_slot("phone_number")
        mongo_db.save_reservation(reservation=reservation)

        return [SlotSet("restaurant_name",None)]


class ActionReviewRestaurant(Action):
    def name(self) -> Text:
        return "action_review_restaurant"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        pass

