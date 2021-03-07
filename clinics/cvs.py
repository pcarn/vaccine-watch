import logging
import os
from datetime import datetime

import requests

from . import Clinic


class CVS(Clinic):
    def get_locations(self):
        url = "https://www.cvs.com/Services/ICEAGPV1/immunization/1.0.0/getIMZStores"
        headers = {
            "content-type": "application/json",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.192 Safari/537.36",
        }
        payload = {
            "requestMetaData": {
                "appName": "CVS_WEB",
                "lineOfBusiness": "RETAIL",
                "channelName": "WEB",
                "deviceType": "DESKTOP",
                "deviceToken": "7777",
                "apiKey": "a2ff75c6-2da7-4299-929d-d670d827ab4a",
                "source": "ICE_WEB",
                "securityType": "apiKey",
                "responseFormat": "JSON",
                "type": "cn-dep",
            },
            "requestPayloadData": {
                "selectedImmunization": ["CVD"],
                "distanceInMiles": int(os.environ["RADIUS"]),
                "imzData": [{"imzType": "CVD", "allocationType": "1"}],
                "searchCriteria": {"addressLine": os.environ["ZIP_CODE"]},
            },
        }
        response = requests.post(url, headers=headers, json=payload)

        generic_cvs = {
            "id": "cvs",
            "name": "CVS",
            "link": "https://www.cvs.com/vaccine/intake/store/cvd-schedule?icid=coronavirus-lp-vaccine-mo-statetool",
            "zip": os.environ["ZIP_CODE"],
        }

        if response.status_code == 200:
            data = response.json()
            if data["responseMetaData"]["statusCode"] == "0000":
                appointment_dates = data["responsePayloadData"]["availableDates"]
                appointment_dates.sort()

                clinics_with_vaccine = [
                    {**generic_cvs, **get_available_date_info(appointment_dates)}
                ]
                clinics_without_vaccine = []
            else:
                clinics_with_vaccine = []
                clinics_without_vaccine = [generic_cvs]

        else:
            logging.error(
                "Bad response from CVS: Code {}: {}".format(
                    response.status_code, response.text
                )
            )
            clinics_with_vaccine = []
            clinics_without_vaccine = []

        return {
            "with_vaccine": clinics_with_vaccine,
            "without_vaccine": clinics_without_vaccine,
        }


def timestamp_to_date(timestamp):
    return datetime.strptime(timestamp, "%Y-%m-%d")


# Takes a list of strings in date format "YYYY-MM-DD"
def get_available_date_info(dates):
    return {
        "earliest_appointment_day": timestamp_to_date(dates[0]).strftime("%b %-d"),
        "latest_appointment_day": timestamp_to_date(dates[-1]).strftime("%b %-d"),
    }
