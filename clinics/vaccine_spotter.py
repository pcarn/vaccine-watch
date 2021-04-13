import json
import logging
import os
from datetime import datetime

import requests
from geopy.distance import distance
from pytz import timezone

from utils import timeout_amount

from . import Clinic

# These are blocked because they're implemented separately in this repo, and check more often
PROVIDER_BRAND_BLOCK_LIST = ["cvs", "hyvee"]


class VaccineSpotter(Clinic):
    def __init__(self):
        self.here = (os.environ["LATITUDE"], os.environ["LONGITUDE"])
        self.states = json.loads(os.environ["STATES"])

    # Takes a dict of location data from the API (data['features'])
    # returns True or False, if location should be included
    def should_include_location(self, location):
        coordinates = location["geometry"]["coordinates"]
        longitude, latitude = coordinates

        return location["properties"][
            "provider_brand"
        ] not in PROVIDER_BRAND_BLOCK_LIST and distance(
            self.here, (latitude, longitude)
        ).miles < int(
            os.environ["RADIUS"]
        )

    # Formats the data into the return format (dict)
    def format_data(self, location):
        zone = os.environ.get("TIMEZONE", "US/Central")
        try:
            if location["properties"]["appointments_last_fetched"]:
                appointments_last_fetched = (
                    datetime.fromisoformat(
                        location["properties"]["appointments_last_fetched"]
                    )
                    .astimezone(timezone(zone))
                    .strftime("%-I:%M")
                )
            else:
                appointments_last_fetched = None
        except (
            ValueError,
            TypeError,
        ) as e:  # Python doesn't like 2 digits for decimal fraction of second
            appointments_last_fetched = None

        return {
            "link": location["properties"]["url"],
            "id": "{}{}-{}".format(
                os.environ.get("CACHE_PREFIX", ""),
                location["properties"]["provider_brand"],
                location["properties"]["id"],
            ),
            "name": "{} {} {}".format(
                location["properties"]["provider_brand_name"],
                location["properties"]["name"],
                " ".join(
                    [
                        word.capitalize()
                        for word in location["properties"]["city"].split(" ")
                    ]
                ),
            ),
            "state": location["properties"]["state"],
            "zip": location["properties"]["postal_code"],
            "appointments_last_fetched": appointments_last_fetched,
        }

    def get_locations(self):
        locations_with_vaccine = []
        locations_without_vaccine = []
        vaccine_spotter_api_url_template = (
            "https://www.vaccinespotter.org/api/v0/states/{}.json"
        )

        for state in self.states:
            response = requests.get(
                vaccine_spotter_api_url_template.format(state), timeout=timeout_amount
            )
            try:
                response.raise_for_status()
                data = response.json()

                matching_locations = [
                    location
                    for location in data["features"]
                    if self.should_include_location(location)
                ]
                for location in matching_locations:
                    formatted_location = self.format_data(location)
                    if location["properties"]["appointments_available"]:
                        appointment_times = [
                            appointment["time"]
                            for appointment in location["properties"]["appointments"]
                        ]
                        appointment_times.sort()
                        formatted_location["earliest_appointment_day"] = date_from_iso(
                            appointment_times[0]
                        )
                        formatted_location["latest_appointment_day"] = date_from_iso(
                            appointment_times[-1]
                        )

                        locations_with_vaccine.append(formatted_location)
                    else:
                        locations_without_vaccine.append(formatted_location)
            except requests.exceptions.RequestException:
                logging.exception(
                    "Bad response from Vaccine Spotter",
                )

        return {
            "with_vaccine": locations_with_vaccine,
            "without_vaccine": locations_without_vaccine,
        }


def date_from_iso(iso):
    return datetime.fromisoformat(iso).strftime("%b %-d")
