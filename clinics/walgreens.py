import logging
import os
from datetime import datetime

import requests
from pytz import timezone

from . import Clinic


class Walgreens(Clinic):
    def get_locations(self):
        zone = os.environ.get("TIMEZONE", "US/Central")
        url = "https://www.walgreens.com/hcschedulersvc/svc/v1/immunizationLocations/availability"
        headers = {
            "x-xsrf-token": os.environ["WALGREENS_X_XSRF_TOKEN"],
            "cookie": "XSRF-TOKEN={}".format(os.environ["WALGREENS_XSRF_TOKEN_COOKIE"]),
        }
        payload = {
            "serviceId": "99",
            "position": {
                "latitude": float(os.environ["LATITUDE"]),
                "longitude": float(os.environ["LONGITUDE"]),
            },
            "appointmentAvailability": {
                "startDateTime": datetime.now(timezone(zone)).strftime("%Y-%m-%d")
            },
            "radius": min(25, int(os.environ["RADIUS"])),
        }
        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 200:
            data = response.json()
            generic_walgreens = {
                "id": "{}walgreens".format(os.environ.get("CACHE_PREFIX", "")),
                "name": "Walgreens",
                "link": "https://www.walgreens.com/findcare/vaccination/covid-19/",
                "zip": data["zipCode"],
                "appointments_last_fetched": (
                    datetime.now().astimezone(timezone(zone)).strftime("%-I:%M")
                ),
            }
            if data["appointmentsAvailable"] is True:
                locations_with_vaccine = [generic_walgreens]
                locations_without_vaccine = []
            else:
                locations_with_vaccine = []
                locations_without_vaccine = [generic_walgreens]

        else:
            logging.error(
                "Bad response from Walgreens: Code {}: {}".format(
                    response.status_code, response.text
                )
            )
            locations_with_vaccine = []
            locations_without_vaccine = []

        return {
            "with_vaccine": locations_with_vaccine,
            "without_vaccine": locations_without_vaccine,
        }
