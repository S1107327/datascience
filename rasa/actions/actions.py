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
from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from typing import Any, Text, Dict, List
from mongodb.mongo_utils import MongoDBConnector


class ActionShowRestaurant(Action):
    def name(self) -> Text:
        return "action_restaurant_list"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        mongo_db = MongoDBConnector()
        restaurant_json = mongo_db.get_restaurant_names_list()
        text_to_display = ""
        for restaurant in restaurant_json:
            text_to_display += f"{restaurant['name']}\n"
        dispatcher.utter_message(text=text_to_display,
                                 buttons=[{"title": "MORE", "payload": "/restaurant_info"}])

        return []


class ValidateRestaurantInfoForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_info_restaurant_form"

    def validate_restaurant_name(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        mongo_db = MongoDBConnector()
        restaurants = mongo_db.get_restaurant_names_list()
        restaurant_name_list = []
        for restaurant in restaurants:
            restaurant_name_list.append(str(restaurant['name']).lower())
        if slot_value.lower() not in restaurant_name_list:
            dispatcher.utter_message(text=f"Sorry but the restaurant {slot_value} is not registered on the service")
            return {"restaurant_name": None}
        dispatcher.utter_message(text=f"OK! I'll show you more info about {slot_value} restaurant.")
        return {"restaurant_name": slot_value}


class ActionInfoRestaurant(Action):
    def name(self) -> Text:
        return "action_info_restaurant"

    def run(self, dispatcher: "CollectingDispatcher",
        tracker: Tracker,
        domain: "Dict[Text, Any]",) -> List[Dict[Text, Any]]:
        mongo_db = MongoDBConnector()
        restaurant_name = tracker.get_slot('restaurant_name')
        info_restaurant = mongo_db.get_restaurant_info(restaurant_name)
        address_dict = {"building": info_restaurant["address"]["building"],
                        "lon": f"{info_restaurant['address']['coord'][0]}",
                        "lat:": f"lat: {info_restaurant['address']['coord'][1]}",
                        "street": info_restaurant["address"]["street"],
                        "zipcode": info_restaurant["address"]["zipcode"]}
        mydict = {"name": info_restaurant['name'],
                     "borough": info_restaurant['borough'],
                     "address": f"{address_dict['street']}, {address_dict['zipcode']}, in building {address_dict['building']}",
                     "cuisine": info_restaurant["cuisine"]}
        text_to_display = ""
        for k,v in mydict.items():
            text_to_display += f"{k}: {v}\n"
        dispatcher.utter_message(text=text_to_display,
                                 attachment=f"https://www.google.com/maps/search/?api=1&query={address_dict['lat']}%2C{address_dict['lon']}")

class ActionReserveTable(Action):
    def name(self) -> Text:
        return "action_reserve_table"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        pass

class ActionReviewRestaurant(Action):
    def name(self) -> Text:
        return "action_review_restaurant"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        pass