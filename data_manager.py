import requests

STEINHQ_ENDPOINT = "my.personal.endpoint/prices"
STEINHQ_ENDPOINT_U = "my.personal.endpoint/users"
STEINHQ_HEADER = {"Authorization": "Basic my.personal.key"}


class DataManager:
    """Returns Google Sheet rows in a list."""

    def __init__(self):
        self.sheet_response = requests.get(url=STEINHQ_ENDPOINT, headers=STEINHQ_HEADER)  # for prices
        self.sheet_response_u = requests.get(url=STEINHQ_ENDPOINT_U, headers=STEINHQ_HEADER)  # for users
        self.destination_data = {}

    def get_destination_data(self):
        self.destination_data = self.sheet_response.json()
        return self.destination_data

    def get_email_list(self):
        users_data = self.sheet_response_u.json()
        return