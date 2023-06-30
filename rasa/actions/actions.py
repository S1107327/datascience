import sys
sys.path.append("../")
from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from typing import Any, Text, Dict, List
from mongodb.mongo_utils import MongoDBConnector
from rasa_sdk.events import SlotSet


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
                                 buttons=[{"title": "INFO", "payload": "/restaurant_info"}])

        return []

class ActionShowCuisines(Action):
    def name(self) -> Text:
        return "action_cuisines_list"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        mongo_db = MongoDBConnector()
        cuisines = mongo_db.get_cuisines()
        text_to_display = "There are these cuisines available in our restaurants\n"
        for cuisine in cuisines:
            text_to_display += f"{cuisine}\n"
        dispatcher.utter_message(text=text_to_display)

        return []
#TODO: Inserire validation campi della form di prenotazione di un tavolo
class ValidateRestaurantInfoForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_info_restaurant_form"

    def validate_restaurant_name_info(
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
            return {"restaurant_name_info": None}
        return {"restaurant_name_info": slot_value}


class ActionInfoRestaurant(Action):
    def name(self) -> Text:
        return "action_info_restaurant"

    def run(self, dispatcher: "CollectingDispatcher",
        tracker: Tracker,
        domain: "Dict[Text, Any]",) -> List[Dict[Text, Any]]:
        mongo_db = MongoDBConnector()
        restaurant_name = tracker.get_slot('restaurant_name_info')
        info_restaurant = mongo_db.get_restaurant_info(restaurant_name)
        address_dict = {"building": info_restaurant["address"]["building"],
                        "lon": f"{info_restaurant['address']['coord'][0]}",
                        "lat": f"{info_restaurant['address']['coord'][1]}",
                        "street": info_restaurant["address"]["street"],
                        "zipcode": info_restaurant["address"]["zipcode"]}
        mydict = {"Name": info_restaurant['name'],
                     "Borough": info_restaurant['borough'],
                     "Address": f"{address_dict['street']}, {address_dict['zipcode']}, in building {address_dict['building']}",
                     "Cuisine": info_restaurant["cuisine"]}
        text_to_display = ""
        for k,v in mydict.items():
            text_to_display += f"{k}: {v}\n"
        text_to_display += f"View it on Google Maps: https://www.google.com/maps/search/?api=1&query={address_dict['lat']}%2C{address_dict['lon']}"
        dispatcher.utter_message(text=text_to_display)
        return [SlotSet("restaurant_name_info", None)]

class ActionReserveTable(Action):
    def name(self) -> Text:
        return "action_reserve_table"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        mongo_db = MongoDBConnector()
        reservation = {}
        name = tracker.get_slot("restaurant_name_reservation")
        reservation['people_number'] = tracker.get_slot("people_number")
        reservation['date'] = tracker.get_slot("date")
        reservation['time'] = tracker.get_slot("time")
        reservation['allergies'] = tracker.get_slot("allergies")
        reservation['name'] = tracker.get_slot("name")
        reservation['phone_number'] = tracker.get_slot("phone_number")
        mongo_db.save_reservation(name, reservation)
        #TODO: Inserire messaggio conferma prenotazione
        return [SlotSet("restaurant_name_reservation",None)]


class ActionReviewRestaurant(Action):
    def name(self) -> Text:
        return "action_review_restaurant"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        pass

