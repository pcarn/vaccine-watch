import logging
import os
import re
from datetime import date, timedelta

import requests
from dateutil.parser import parse
from icecream import ic

from utils import timeout_amount

from . import TestClinic

DAYS_OUT_TO_CHECK = int(os.environ["DAYS_OUT_TO_CHECK_FOR_TESTS"])

PROXIES = {}
if "PROXY_URL" in os.environ:
    PROXIES["https"] = os.environ["PROXY_URL"]
    PROXIES["http"] = os.environ["PROXY_URL"]


class CVSTests(TestClinic):
    def get_locations(self):
        locations = get_all_location_data()

        locations_with_tests = [
            location
            for location in locations
            if location["available_appointment_dates"] != []
        ]
        locations_without_tests = [
            location
            for location in locations
            if location["available_appointment_dates"] == []
        ]

        return {
            "with_vaccine": locations_with_tests,
            "without_vaccine": locations_without_tests,
        }


def get_available_dates(clinic_id, dates, days_out_to_check):
    """
    available_dates are what days show in the UI to book.
    We then check for available slots to see if there is actually anything there to book.
    """
    max_date = date.today() + timedelta(days=days_out_to_check)
    available_dates = [
        parse(date["date"]).date() for date in dates if date["isSlotAvailable"]
    ]
    available_dates = [date for date in available_dates if date <= max_date]
    available_dates.sort()
    if not available_dates:
        return []
    available_slots_url = "https://www.cvs.com/RETAGPV3/scheduler/V3/getAvailableSlots"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
        "x-application-id": "vaccine-watch",
        "cat": "MCPOCT",  # I don't know what this is for but it returns extra data if you don't have it set
    }
    body = {
        "request": {
            "header": {
                "lineOfBusiness": "RETAIL",
                "appName": "CVS_APP",
                "apiKey": "a2ff75c6-2da7-4299-929d-d670d827ab4a",
                "channelName": "WEB",
                "deviceToken": "d9708df38d23192e",
                "deviceType": "DESKTOP",
                "responseFormat": "JSON",
                "securityType": "apiKey",
                "source": "CVS_WEB",
                "type": "retleg",
            },
            "startDate": available_dates[0].strftime("%m/%d/%Y"),
            "endDate": available_dates[-1].strftime("%m/%d/%Y"),
            "visitCode": "48",
            "clinicId": str(clinic_id),
        }
    }
    response = requests.post(
        available_slots_url,
        headers=headers,
        json=body,
        timeout=timeout_amount,
        proxies=PROXIES,
    )
    try:
        response.raise_for_status()
        data = response.json()
        if (
            "response" not in data
            or data["response"]["header"]["statusDesc"] == "No Slots Found"
        ):
            return []
        else:
            return [
                parse(day["date"]).strftime("%b %d")
                for day in data["response"]["details"]
                if day["availableSlots"] != []
                and parse(day["date"]).date() in available_dates
            ]

    except requests.exceptions.RequestException:
        logging.exception("Bad response for CVS Test available slots data")

        return []


def get_all_location_data():
    main_page_response = requests.get(
        "https://www.cvs.com/minuteclinic/covid-19-testing",
        timeout=timeout_amount,
        proxies=PROXIES,
    )
    if not main_page_response.ok:
        # If main page is shut off (503 with "We have finished testing for the day."), don't go any further
        return []

    location_index_url = "https://www.cvs.com/RETAGPV3/MCscheduler/V1/storeScheduler"
    params = {
        "addressLine": os.environ["ZIP"],
        "mileRadius": int(os.environ["RADIUS"]),
        "maxCount": 100,
    }
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
        "x-application-id": "vaccine-watch",
    }
    body = {
        "request": {
            "header": {
                "lineOfBusiness": "Retail",
                "appName": "CVS_APP",
                "apiKey": "a2ff75c6-2da7-4299-929d-d670d827ab4a",
                "channelName": "WEB",
                "deviceToken": "d9708df38d23192e",
                "deviceType": "DESKTOP",
                "responseFormat": "JSON",
                "securityType": "apiKey",
                "source": "CVS_WEB",
                "type": "retlegget",
            }
        }
    }
    response = requests.post(
        location_index_url,
        params=params,
        headers=headers,
        json=body,
        timeout=timeout_amount,
        proxies=PROXIES,
    )
    try:
        response.raise_for_status()
        data = response.json()
        clinics = {}
        for clinic in data["response"]["clinicDetails"]:
            clinics[clinic["clinicId"]] = clinic
        return [
            {
                "id": "cvs-test-{}".format(location["clinicId"]),
                "name": "CVS {}".format(clinics[location["clinicId"]]["clinicName"]),
                "zip": clinics[location["clinicId"]]["zipCode"],
                "state": clinics[location["clinicId"]]["state"],
                "link": "https://www.cvs.com/minuteclinic/covid-19-testing/covid-scheduler?symptoms=covid",
                "available_appointment_dates": get_available_dates(
                    location["clinicId"], location["dates"], DAYS_OUT_TO_CHECK
                ),
                "test_type": "Rapid Test"
                if clinics[location["clinicId"]]["isRapidTest"] == "Y"
                else "PCR Test",
            }
            for location in response.json()["response"]["details"]["dates"]
        ]

    except requests.exceptions.RequestException as error:
        logging.exception("Bad response for CVS Test data")

        return []
