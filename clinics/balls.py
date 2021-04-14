import logging
import os
import re
from datetime import datetime

import requests

from utils import timeout_amount

from . import Clinic


class Balls(Clinic):
    def get_locations(self):
        locations_with_vaccine = []
        locations_without_vaccine = []

        location_data = get_all_location_data()

        valid_location_data = [
            location
            for location in location_data
            if location["available_appointment_dates"] is not None
        ]

        locations_with_vaccine = [
            location
            for location in valid_location_data
            if get_location_available(location)
        ]
        locations_without_vaccine = [
            location
            for location in valid_location_data
            if not get_location_available(location)
        ]

        for location in locations_with_vaccine:
            appointment_dates = location["available_appointment_dates"]
            appointment_dates.sort()
            if len(appointment_dates) > 0:
                location["earliest_appointment_day"] = appointment_dates[0].strftime(
                    "%b %-d"
                )
                location["latest_appointment_day"] = appointment_dates[-1].strftime(
                    "%b %-d"
                )

        return {
            "with_vaccine": locations_with_vaccine,
            "without_vaccine": locations_without_vaccine,
        }


def get_location_available(location):
    return len(location["available_appointment_dates"]) > 0


def get_all_location_data():
    location_index_url = "https://ballsfoodspharmacy.com"
    location_info_regex = '<option value="https:\/\/hipaa.jotform\.com\/(\d{10,20})">(.{1,100}) - .{1,100} - (.{1,100}), (\w{2}) \d{5}<\/option>'
    response = requests.get(location_index_url, timeout=timeout_amount)
    try:
        response.raise_for_status()
        response_body = response.text.replace("â\x80\x93", "-").replace(
            ", Kansas City", " - Kansas City"
        )  # Correct inconsistency
        locations = re.findall(location_info_regex, response_body)

        return [
            {
                "id": "balls-{}".format(location[0]),
                "name": "{} {}".format(location[1], location[2]),
                "state": location[3],
                "link": "https://hipaa.jotform.com/{}".format(location[0]),
                "available_appointment_dates": get_available_appointment_dates(
                    location[0]
                ),
            }
            for location in locations
        ]

    except requests.exceptions.RequestException:
        logging.exception("Bad response from Ball's")

        return []


def timestamp_to_date(timestamp):
    return datetime.strptime(timestamp, "%Y-%m-%d")


def get_available_appointment_dates(location_id):
    url = "https://hipaa.jotform.com/{}".format(location_id)
    response = requests.get(url, timeout=timeout_amount)
    try:
        response.raise_for_status()
        if "All appointments have been filled" in response.text:
            return []

        form_url = "https://hipaa.jotform.com/server.php?action=getAppointments&formID={}&timezone=America%2FChicago%20(GMT-06%3A00)&ncTz=1615050226593&firstAvailableDates".format(
            location_id
        )
        response = requests.get(form_url, timeout=timeout_amount)
        response.raise_for_status()
        data = response.json()["content"]
        if "47" in data:
            return [
                timestamp_to_date(date)
                for date in data["47"].keys()
                if data["47"][date] and any(data["47"][date].values())
            ]
        else:
            logging.error("47 not in Balls data: keys are %s", data.keys())
            return None
    except requests.exceptions.RequestException:
        logging.exception("Bad response from Ball's")
        return None
