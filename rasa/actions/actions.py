import sys
sys.path.append("../")
from datetime import date
from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from typing import Any, Text, Dict, List
from mongodb.mongo_utils import MongoDBConnector
from rasa_sdk.events import SlotSet, AllSlotsReset
from datetime import datetime
import re


### START ACTIONS ###
class ActionStart(Action):
    def name(self) -> Text:
        return "action_start"

    def run(
        self,
        dispatcher: "CollectingDispatcher",
        tracker: Tracker,
        domain: "DomainDict",
    ) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(image="https://dynamic-media-cdn.tripadvisor.com/media/photo-o/27/aa/b0/fd/caption.jpg?w=600&h=-1&s=1")
        return []

### INFO ACTIONS ###
class ActionShowTopRestaurant(Action):
    def name(self) -> Text:
        return "action_top_restaurant_list"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        mongo_db = MongoDBConnector()
        restaurant_json = mongo_db.get_restaurants_ordered_by_score()
        text_to_display = ""
        for restaurant in list(restaurant_json)[:10]:
            text_to_display += f"{restaurant['_id']}\n"
        dispatcher.utter_message(text=text_to_display,
                                 buttons=[{"title": "INFO", "payload": "/restaurant_info"}, {"title": "MORE", "payload": "/all_restaurant_list"}])

        return []

class ActionShowAllRestaurant(Action):
    def name(self) -> Text:
        return "action_all_restaurant_list"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        mongo_db = MongoDBConnector()
        restaurant_json = mongo_db.get_restaurants_ordered_by_score()
        text_to_display = ""
        for restaurant in list(restaurant_json)[10:]:
            text_to_display += f"{restaurant['_id']}\n"
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

class ActionRestaurantOfCuisine(Action, BaseException):
    def name(self) -> Text:
        return "action_restaurant_cuisine"

    def run(
        self,
        dispatcher: "CollectingDispatcher",
        tracker: Tracker,
        domain: "DomainDict",
    ) -> List[Dict[Text, Any]]:
        if len(tracker.latest_message['entities']):
            cuisine = tracker.latest_message['entities'][0]['value']
        else:
            dispatcher.utter_message(text="I can't recognise this type of cuisine. Please check for any typo or spelling error")
            return []
        mongo_db = MongoDBConnector()
        restaurants, count = mongo_db.get_restaurant_of_cuisine(cuisine)
        if count == 0:
            dispatcher.utter_message(text=f"There are no restaurants for {cuisine} cuisine in the service")
        else:
            text_to_display = f"Here are the restaurants of {cuisine} cuisine\n"
            for restaurant in restaurants:
                text_to_display += f"{restaurant['name']}\n"
            dispatcher.utter_message(text=text_to_display)
            return[]


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
        dispatcher.utter_message(text=f"I'll show you more info about {info_restaurant['name']}")
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

### RESERVATIONS ACTIONS ###
#TODO: Inserire validation campi della form di prenotazione di un tavolo
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
        return [AllSlotsReset()]

class ActionShowReservations(Action):
    def name(self) -> Text:
        return "action_get_reservations"

    def run(
        self,
        dispatcher: "CollectingDispatcher",
        tracker: Tracker,
        domain: "DomainDict",
    ) -> List[Dict[Text, Any]]:
        client = tracker.latest_message['entities'][0]['value']
        mongo_db = MongoDBConnector()
        reservations = mongo_db.get_active_client_reservations(client)
        if len(reservations) > 0:
            text_to_display = f"Here are reservations for {client}\n"
            for reservation in reservations:
                if int(reservation['people_number']) > 1:
                    text_to_display += f"{reservation['name']} for {reservation['people_number']} people on {reservation['date']} at {reservation['time']}\n Restaurant: {reservation['restaurant_name']}\n"
                else:
                    text_to_display += f"{reservation['name']} for {reservation['people_number']} person {reservation['date']} at {reservation['time']}\n Restaurant: {reservation['restaurant_name']}\n"
            dispatcher.utter_message(text=text_to_display)
        else:
            dispatcher.utter_message(text=f"There are no active reservations for \"{client}\"")


class ActionClearFormSlots(Action):
    def name(self) -> Text:
        return "action_clear_form_slots"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        return[AllSlotsReset()]


class ActionShowReservationInfo(Action):
    def name(self) -> Text:
        return "action_show_reservation_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        utter_text = "This are your reservation infos:\n"
        utter_text += f"Restaurant: {tracker.get_slot('restaurant_name_reservation')}\n"
        utter_text += f"Number of people: {tracker.get_slot('people_number')}\n"
        utter_text += f"Date: {tracker.get_slot('date')}\n"
        utter_text += f"Reservation time: {tracker.get_slot('time')}\n"
        utter_text += f"Reservation name: {tracker.get_slot('name')}\n"
        utter_text += f"Given phone number: {tracker.get_slot('phone_number')}"
        dispatcher.utter_message(text=utter_text)
        return []

class ValidateReservationForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_reservation_form"

    def validate_restaurant_name_reservation(
        self,
        slot_value: Text,
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
            dispatcher.utter_message(text=f"Sorry but the restaurant {slot_value} is not registered on the service.")
            return {"restaurant_name_reservation": None}
        return {"restaurant_name_reservation": slot_value}

    #TODO: validare anche se il numero di posti disponibili nel db è sufficiente, ancora non fatto lo script
    def validate_people_number(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        mongo_db = MongoDBConnector()
        if not slot_value.isdigit() or not int(slot_value)>0:
            dispatcher.utter_message(text=f"Sorry but specified people number is not correct or valid.")
            return {"people_number": None}
        return {"people_number": slot_value}

    def validate_phone_number(
        self,
        slot_value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        if not len(slot_value) == 10:
            dispatcher.utter_message(text=f"Sorry but specified phone number is not valid! Retry.")
            return {"phone_number": None}
        return {"phone_number": slot_value}

    def validate_date(
        self,
        slot_value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        current_date = datetime.now().date()
        date_format = ["%Y-%m-%d", "%Y%m%d", "%Y/%m/%d", "%d-%m-%Y", "%d/%m/%Y"]
        for format in date_format:
            try:
                formatted_date = datetime.strptime(slot_value, format).date()
                if formatted_date < current_date:
                    dispatcher.utter_message(text="Sorry, reservation date can't be a past date.")
                    return {"date":None}
                else:
                    formatted_date = formatted_date.strftime('%Y-%m-%d')
                    return {"date": formatted_date}
            except Exception:
                pass
        dispatcher.utter_message(text="Inserted date is not correct.")
        return {'date':None}

    def validate_time(
        self,
        slot_value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        time_format = "%H:%M"
        try:
            formatted_time = datetime.strptime(slot_value, time_format)
            return {'time':slot_value}
        except Exception:
            pass
        dispatcher.utter_message(text="Inserted time is not correct. Retry!")
        return {'time':None}

### REVIEW ACTIONS ###
##TODO: Funzioni su mongo per prendere i dati
class ActionReviewRestaurant(Action):
    def name(self) -> Text:
        return "action_review_restaurant"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        mongo_db = MongoDBConnector()
        review = {}
        name = tracker.get_slot("restaurant_name_review")
        review['name'] = tracker.get_slot("name_review")
        review['score'] = int(tracker.get_slot("score_review"))
        review['body'] =  tracker.get_slot("review_body")
        review['date_review'] = date.today().strftime("%d-%m-%Y")
        mongo_db.save_review(name, review)
        return [SlotSet("restaurant_name_review",None), SlotSet("name_review",None), SlotSet("review_body",None), SlotSet("score_review", None)]

class ActionShowReviews(Action):
    def name(self) -> Text:
        return "action_get_reviews"

    def run(
        self,
        dispatcher: "CollectingDispatcher",
        tracker: Tracker,
        domain: "DomainDict",
    ) -> List[Dict[Text, Any]]:
        restaurant = tracker.get_slot("restaurant_name_review_list")
        mongo_db = MongoDBConnector()
        reviews = mongo_db.get_restaurant_reviews(restaurant)
        dispatcher.utter_message(text=f"Here are the 5 latest reviews for {restaurant}\n")
        for review in reviews:
            dispatcher.utter_message(text=f"{review['name']} voted {review['score']} in {review['date_review']}\n \"{review['body']}\"",
                                     button={"title": "MORE REVIEWS", "payload": "/show_all_reviews"})
        return []


class ActionShowReviewInfo(Action):
    def name(self) -> Text:
        return "action_show_review_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        utter_text = "This are your review infos:\n"
        utter_text += f"Restaurant: {tracker.get_slot('restaurant_name_review')}\n"
        utter_text += f"Text: {tracker.get_slot('review')}\n"
        utter_text += f"From: {tracker.get_slot('name_review')}\n"
        dispatcher.utter_message(text=utter_text)
        return []

class ValidateReviewForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_review_form"

    def validate_restaurant_name_review(
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
            dispatcher.utter_message(text=f"Sorry but the restaurant {slot_value} is not registered on the service.")
            return {"restaurant_name_review": None}
        return {"restaurant_name_review": slot_value}

    def validate_score_review(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
        ) -> Dict[Text, Any]:
            pattern = r'^\s*[1-5]\s*$'
            match = re.search(pattern, slot_value)
            if not match:
                dispatcher.utter_message(text=f"Sorry but the given score is not correct or valid.")
                return {"score_review": None}
            return {"score_review": match.group().strip()}

class ActionShowSpecificHelp(Action):
    def name(self) -> Text:
        return "action_show_specific_help"
    
    def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]
    ) -> Dict[Text, Any]:
        user_choice=tracker.get_slot("help_category")
        match user_choice:
            case "info":
                dispatcher.utter_message(text="""I can give you various kinds of information. Specifically:\n
                                         \t- The list of all the restaurants in the area.\n
                                         \t- All of the possibile cuisine types you can choose from.\n
                                         \t- Which restaurants offer a specific type of cuisine.\n
                                         \t- Info about a restaurant you're curious of.""")
            case "reserve":
                dispatcher.utter_message(text="""In order for me to be able to reserve a place for you to eat, 
                                         I will need some information from you:\n
                                         \t- In which place you want to go, of course.\n
                                         \t- How many people you want to reserve for.\n
                                         \t- The date of the reservation.\n
                                         \t- At what time you would like to go eat.\n
                                         \t- Whether you suffer from some allergies.\n
                                         \t- Your name.\n
                                         \t- Your phone number.""")
            case "review":
                dispatcher.utter_message(text="""To leave a review of your experience in a restaurant 
                                         I will need from you:\n
                                         \t- The name of the restaurant you want to leave a review at\n
                                         \t- Your review. Don't be too harsh!\n
                                         \t- Your name\n
                                         \t- A score between 1-5""")
            case _:
                dispatcher.utter_message(text=f"Sorry, i don't recognize {user_choice}...")
