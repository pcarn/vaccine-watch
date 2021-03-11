import itertools
import logging
import os
import re
from datetime import datetime

import requests

from . import Clinic


class Cosentinos(Clinic):
    def get_locations(self):
        location_index_url = "https://www.cosentinos.com/covid-vaccine"
        location_info_regex = r"<strong>(.{10,50})<\/strong><br \/>[\s\S]{1,50}<br \/>\s*(.{1,30}), (\w{2}) \d{5}<br \/>\s*[\d-]{12}<br(?: \/)?>[\s\S]{1,100}calendarID=(\d{7}).{1,50}Vaccine Availability<\/a>"
        response = requests.get(location_index_url)

        locations_with_vaccine = []
        locations_without_vaccine = []

        if response.status_code == 200:
            locations = re.findall(location_info_regex, response.text)
            for location in locations:
                name, city, state, location_id = location
                location_data = format_data(
                    {
                        "location_id": location_id,
                        "name": name.replace("'", "'"),
                        "city": city,
                        "state": state,
                    }
                )
                if get_availability_for_location(location_id):
                    locations_with_vaccine.append(location_data)
                else:
                    locations_without_vaccine.append(location_data)

        else:
            logging.error(
                "Bad response from Cosentinos: Code {}: {}".format(
                    response.status_code, response.text
                )
            )

        return {
            "with_vaccine": locations_with_vaccine,
            "without_vaccine": locations_without_vaccine,
        }


def get_availability_for_location(location_id):
    current_offset = 0
    more_results = True
    offset_regex = r"offset:(\d{2})[\s\S]{1,100}More Times"

    while more_results is True:
        page_data = get_page(location_id, current_offset)
        # There are two on each page, except last page has zero
        offset_amount = int((re.findall(offset_regex, page_data) or [0])[0])

        if (
            "No upcoming classes are available" in page_data
            or "There are no appointment types available for scheduling" in page_data
        ):
            return False

        has_availability = page_data.count(
            'no <span id="spots-left-text">spots left'
        ) != page_data.count("spots left")
        if has_availability:
            return True

        more_results = "More Times" in page_data
        current_offset += offset_amount

    return False


def get_page(location_id, offset):
    date_url = "https://app.squarespacescheduling.com/schedule.php?action=showCalendar&fulldate=1&owner=21943707&template=class"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    }
    payload = "type=&calendar=&month=&skip=true&options%5Boffset%5D={}&options%5BnumDays%5D=5&ignoreAppointment=&appointmentType=&calendarID={}".format(
        offset, location_id
    )
    response = requests.post(date_url, headers=headers, data=payload)

    if response.status_code == 200:
        return response.text
    else:
        logging.error(
            "Bad Response from Cosentino's Squarespace: {} {}".format(
                response.status_code, response.text
            )
        )
        return ""


def format_data(location):
    return {
        "link": "https://app.squarespacescheduling.com/schedule.php?owner=21943707&calendarID={}".format(
            location["location_id"]
        ),
        "id": "{}cosentinos-{}".format(
            os.environ.get("CACHE_PREFIX", ""), location["location_id"]
        ),
        "name": "{} {}".format(location["name"], location["city"]),
        "state": location["state"],
    }
