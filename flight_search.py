import requests
from datetime import datetime, timedelta
from flight_data import FlightData

tomorrow = datetime.now() + timedelta(days=1)
six_months_from_now = datetime.now() + timedelta(days=180)

API_KEY = "my.personal.key"
API_ENDPOINT_QUERY = "https://tequila-api.kiwi.com/locations/query"
API_ENDPOINT_SEARCH = "https://tequila-api.kiwi.com/v2/search"
HEADERS = {
    "apikey": API_KEY
}


class FlightSearch:
    """Returns Flight destination code."""

    def check_flights(self, origin_destination, city_destination_code):
        """Passes the parameters, requests all the flight details from API
        and save only the required ones to print the destination city and the price"""

        params = {
            "fly_from": origin_destination,
            "fly_to": city_destination_code,
            "date_from": tomorrow.strftime("%d/%m/%Y"),
            "date_to": six_months_from_now.strftime("%d/%m/%Y"),
            "nights_in_dst_from": 3,
            "nights_in_dst_to": 16,
            "flight_type": "round",
            "one_for_city": 1,
            "max_stopovers": 0,
            "curr": "EUR"
        }
        flight_response = requests.get(url=API_ENDPOINT_SEARCH, params=params, headers=HEADERS)
        try:
            flight_data = flight_response.json()["data"][0]

        except IndexError:
            params["max_stopovers"] = 2
            flight_response = requests.get(url=API_ENDPOINT_SEARCH, params=params, headers=HEADERS)
            flight_data = flight_response.json()["data"][0]
            current_flight_data = FlightData(
                flight_price=flight_data["price"],
                origin_city=flight_data["route"][0]["cityFrom"],
                origin_airport=flight_data["route"][0]["flyFrom"],
                destination_city=flight_data["cityTo"],
                destination_airport=flight_data["flyTo"],
                destination_country=flight_data["countryTo"]["name"],
                out_date=flight_data["route"][0]["local_departure"].split("T")[0],
                return_date=flight_data["route"][2]["local_departure"].split("T")[0],
                stop_overs=1,
                via_city=flight_data["route"][0]["cityTo"],
                flight_ticket=flight_data["deep_link"]
            )
            return current_flight_data

        else:
            current_flight_data = FlightData(
                flight_price=flight_data["price"],
                origin_city=flight_data["route"][0]["cityFrom"],
                origin_airport=flight_data["route"][0]["flyFrom"],
                destination_city=flight_data["route"][0]["cityTo"],
                destination_airport=flight_data["route"][0]["flyTo"],
                destination_country=flight_data["countryTo"]["name"],
                out_date=flight_data["route"][0]["local_departure"].split("T")[0],
                return_date=flight_data["route"][1]["local_departure"].split("T")[0],
                flight_ticket=flight_data["deep_link"]
            )
            return current_flight_data

    def get_destination_code(self, city_name):
        """Returns the flight code according to the destination's city name"""

        params = {
            "term": city_name,
            "location_types": "city"
        }
        flight_response = requests.get(url=API_ENDPOINT_QUERY, params=params, headers=HEADERS)
        flight_code = flight_response.json()["locations"][0]["code"]
        return flight_code