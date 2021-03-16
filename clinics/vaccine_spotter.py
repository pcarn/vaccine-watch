import json
import logging
import os
from datetime import datetime

import requests

from . import Clinic


class VaccineSpotterClinic(Clinic):
    def __init__(self):
        self.states = json.loads(os.environ["STATES"])

    # Takes a dict of location data from the API (data['features'])
    # returns True or False, if location should be included
    def should_include_location(self, location):
        raise NotImplementedError()

    # Formats the data into the return format (dict)
    def format_data(location):
        raise NotImplementedError()

    def get_locations(self):
        locations_with_vaccine = []
        locations_without_vaccine = []
        vaccine_spotter_api_url_template = (
            "https://www.vaccinespotter.org/api/v0/states/{}.json"
        )

        for state in self.states:
            response = requests.get(vaccine_spotter_api_url_template.format(state))
            if response.status_code == 200:
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
            else:
                logging.error(
                    "Bad response from Vaccine Spotter: Code {}",
                    response.status_code,
                )

        return {
            "with_vaccine": locations_with_vaccine,
            "without_vaccine": locations_without_vaccine,
        }


def date_from_iso(iso):
    return datetime.fromisoformat(iso).strftime("%b %-d")
