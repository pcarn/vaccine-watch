import itertools
import logging
import os
import re
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from . import Clinic


class Balls(Clinic):
    def get_locations(self):
        clinics_with_vaccine = []
        clinics_without_vaccine = []

        location_data = get_all_location_data()

        clinics_with_vaccine = [
            clinic for clinic in location_data if get_clinic_available(clinic)
        ]
        clinics_without_vaccine = [
            clinic for clinic in location_data if not get_clinic_available(clinic)
        ]

        for clinic in clinics_with_vaccine:
            appointment_dates = clinic["available_appointment_dates"]
            appointment_dates.sort()
            if len(appointment_dates) > 0:
                clinic["earliest_appointment_day"] = appointment_dates[0].strftime(
                    "%b %-d"
                )
                clinic["latest_appointment_day"] = appointment_dates[-1].strftime(
                    "%b %-d"
                )

        return {
            "with_vaccine": clinics_with_vaccine,
            "without_vaccine": clinics_without_vaccine,
        }


def get_clinic_available(clinic):
    return clinic["enabled"] and len(clinic["available_appointment_dates"]) > 0


def get_all_location_data():
    clinic_index_url = "https://ballsfoodspharmacy.com"
    clinic_info_regex = '<option value="https:\/\/hipaa.jotform\.com\/(\d{10,20})">(.{1,100}) - .{1,100} - (.{1,100}), (\w{2}) \d{5}<\/option>'
    response = requests.get(clinic_index_url)
    if response.status_code == 200:
        clinics = re.findall(clinic_info_regex, response.text)
        page_data = BeautifulSoup(response.text, "html.parser")
        enabled_options = page_data.find_all("option")

        return [
            {
                "id": "balls-{}".format(clinic[0]),
                "name": "{} {}".format(clinic[1], clinic[2]),
                "state": clinic[3],
                "enabled": any(
                    [clinic[0] in str(option) for option in enabled_options]
                ),
                "link": "https://hipaa.jotform.com/{}".format(clinic[0]),
                "available_appointment_dates": get_available_appointment_dates(
                    clinic[0]
                ),
            }
            for clinic in clinics
        ]

    else:
        logging.error(
            "Bad response from Ball's: Code {}: {}".format(
                response.status_code, response.text
            )
        )

        return []


def timestamp_to_date(timestamp):
    return datetime.strptime(timestamp, "%Y-%m-%d")


def get_available_appointment_dates(location_id):
    url = "https://hipaa.jotform.com/{}".format(location_id)
    response = requests.get(url)
    if response.status_code == 200:
        if "All appointments have been filled" in response.text:
            return []
        else:
            api_url = "https://hipaa.jotform.com/server.php?action=getAppointments&formID={}&timezone=America%2FChicago%20(GMT-06%3A00)&ncTz=1615050226593&firstAvailableDates".format(
                location_id
            )
            response = requests.get(api_url)
            if response.status_code == 200:
                data = response.json()["content"]
                if "47" in data:
                    return [
                        timestamp_to_date(date)
                        for date in data["47"].keys()
                        if data["47"][date] and any(data["47"][date].values())
                    ]
                else:
                    logging.error(
                        "47 not in Balls data: keys are {}".format(data.keys())
                    )
                    return []
    else:
        return []
