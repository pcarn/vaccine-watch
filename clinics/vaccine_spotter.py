import logging
from datetime import datetime

import requests

from . import Clinic


class VaccineSpotterClinic(Clinic):
    # Example: "walmart"
    def get_brand(self):
        raise NotImplementedError()

    # Returns a dict with keys states, values brand_id of stores in the state
    # Example: {'MO': [326, 61]}
    def get_location_config(self):
        raise NotImplementedError()

    # Formats the data into the return format (dict)
    def format_data(location):
        raise NotImplementedError()

    def get_locations(self):
        locations_with_vaccine = []
        locations_without_vaccine = []
        vaccine_spotter_api_url_template = (
            "https://www.vaccinespotter.org/api/v0/stores/{}/{}.json"
        )

        for state in self.get_location_config().keys():
            response = requests.get(
                vaccine_spotter_api_url_template.format(state, self.get_brand())
            )
            if response.status_code == 200:
                data = response.json()
                for location_id in self.get_location_config()[state]:
                    matching_location = (
                        [
                            location
                            for location in data
                            if location["brand_id"] == str(location_id)
                        ]
                        or [None]
                    )[0]
                    if matching_location:
                        formatted_location = self.format_data(matching_location)
                        if matching_location["appointments_available"]:
                            matching_location["appointments"].sort()
                            formatted_location[
                                "earliest_appointment_day"
                            ] = date_from_iso(matching_location["appointments"][0])
                            formatted_location[
                                "latest_appointment_day"
                            ] = date_from_iso(matching_location["appointments"][-1])

                            locations_with_vaccine.append(formatted_location)
                        else:
                            locations_without_vaccine.append(formatted_location)
                    else:
                        logging.error(
                            "Walmart #{} not in Vaccine Spotter data".format(
                                location_id
                            )
                        )
            else:
                logging.error(
                    "Bad response from Vaccine Spotter: Code {}: {}",
                    response.status_code,
                    response.text,
                )

        return {
            "with_vaccine": locations_with_vaccine,
            "without_vaccine": locations_without_vaccine,
        }


def date_from_iso(iso):
    return datetime.fromisoformat(iso).strftime("%b %-d")
