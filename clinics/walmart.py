import logging
import os

import requests

from .vaccine_spotter import VaccineSpotterClinic

WALMART_CID = "f17a2469-c146-7206-e044-001517f43a86"


class Walmart(VaccineSpotterClinic):
    location_config = {}

    def get_brand(self):
        return "walmart"

    def get_location_config(self):
        if not self.location_config:
            self.location_config = get_walmart_config()
        return self.location_config

    def format_data(self, location):
        return {
            "link": "https://www.walmart.com/cp/flu-shots-immunizations/1228302",
            "id": "walmart-{}".format(location["brand_id"]),
            "name": "Walmart {}".format(location["name"]),
            "state": location["state"],
            "zip": location["postal_code"],
        }


def get_walmart_config():
    url = "https://www.walmart.com/pharmacy/v2/storefinder/stores/{}?searchString={}&serviceType=covid_immunizations&filterDistance={}".format(
        WALMART_CID, os.environ["ZIP_CODE"], os.environ["RADIUS"]
    )
    response = requests.get(url)
    config = {}
    if response.status_code == 200:
        locations = response.json()["data"]["storesData"]["stores"]
        for location in locations:
            state = location["address"]["state"]
            config[state] = config.get(state, False) or []  # Initialize array
            config[state].append(location["id"])
        return config
    else:
        logging.error(
            "Bad response from Walmart: Code {}: {}",
            response.status_code,
            response.text,
        )
