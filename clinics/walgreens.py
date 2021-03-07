import logging
import os
from datetime import datetime

import requests
from pytz import timezone

from . import Clinic


class Walgreens(Clinic):
    def get_locations(self):
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
                "startDateTime": datetime.now(timezone("US/Central")).strftime(
                    "%Y-%m-%d"
                )
            },
            "radius": max(20, int(os.environ["RADIUS"])),
        }
        response = requests.post(url, headers=headers, json=payload)

        generic_walgreens = {
            "id": "walgreens",
            "name": "Walgreens",
            "link": "https://www.walgreens.com/findcare/vaccination/covid-19/",
            "zip": os.environ["ZIP_CODE"],
        }

        if response.status_code == 200:
            if response.json()["appointmentsAvailable"] is True:
                clinics_with_vaccine = [generic_walgreens]
                clinics_without_vaccine = []
            else:
                clinics_with_vaccine = []
                clinics_without_vaccine = [generic_walgreens]

        else:
            logging.error(
                "Bad response from Walgreens: Code {}: {}".format(
                    response.status_code, response.text
                )
            )
            clinics_with_vaccine = []
            clinics_without_vaccine = []

        return {
            "with_vaccine": clinics_with_vaccine,
            "without_vaccine": clinics_without_vaccine,
        }
