import logging
import os
import re
from datetime import datetime

import requests

from utils import timeout_amount

from . import Clinic

manufacturer_ids = [21799679, 21707847]


class RapidTestKC(Clinic):
    def get_locations(self):
        url = "https://app.acuityscheduling.com/schedule.php"
        params = (
            ("action", "showCalendar"),
            ("fulldate", "1"),
            ("owner", "22547753"),
            ("template", "weekly"),
        )

        appointment_dates = []
        for manufacturer_id in manufacturer_ids:
            data = {
                "type": manufacturer_id,
                "calendar": "any",
                "skip": "true",
                "options[qty]": "1",
                "options[numDays]": "5",
            }
            response = requests.post(
                url, params=params, data=data, timeout=timeout_amount
            )
            try:
                response.raise_for_status()
                date_regex = (
                    '<div class="date-secondary babel-ignore">([\w\s]{1,10})<\/div>'
                )
                dates = re.findall(date_regex, response.text)
                for date in dates:
                    appointment_dates.append(datetime.strptime(date, "%B %d"))
            except requests.exceptions.RequestException:
                logging.exception("Bad response from RapidTestKC")

        location = {
            "link": "https://www.vaccinekansascity.com/schedule-your-vaccine",
            "id": "rapidtestkc",
            "name": "Rapid Test KC - Overland Park",
            "state": "KS",
        }

        if appointment_dates:
            appointment_dates.sort()
            return {
                "with_vaccine": [
                    {
                        **location,
                        "earliest_appointment_day": appointment_dates[0].strftime(
                            "%b %-d"
                        ),
                        "latest_appointment_day": appointment_dates[-1].strftime(
                            "%b %-d"
                        ),
                    }
                ],
                "without_vaccine": [],
            }
        else:
            return {"with_vaccine": [], "without_vaccine": [location]}
