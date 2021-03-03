import itertools
import logging
import os
from datetime import datetime

import requests

HYVEE_URL = "https://www.hy-vee.com/my-pharmacy/api/graphql"
HEADERS = {"content-type": "application/json"}


def timestamp_to_date(timestamp):
    return datetime.strptime(timestamp, "%m/%d/%Y %H:%M:%S %z")


def get_appointment_info(location_id):
    available_manufacturer_ids = get_available_manufacturer_ids(location_id)
    available_appointment_times = [
        get_available_appointment_times(location_id, manufacturer_id)
        for manufacturer_id in available_manufacturer_ids
    ]
    flat_times = list(itertools.chain(*available_appointment_times))
    flat_times.sort()

    if len(flat_times) > 0:
        return {
            "earliest_appointment_day": timestamp_to_date(flat_times[0]).strftime(
                "%b %-d"
            ),
            "latest_appointment_day": timestamp_to_date(flat_times[-1]).strftime(
                "%b %-d"
            ),
        }
    else:
        return {}


def format_hyvee_data(clinic):
    return {
        "link": "https://www.hy-vee.com/my-pharmacy/covid-vaccine-consent",
        "id": "hyvee-{}".format(clinic["location"]["locationId"]),
        "name": "Hy-Vee {}".format(clinic["location"]["name"]),
        "state": clinic["location"]["address"]["state"],
        "zip": clinic["location"]["address"]["zip"],
    }


def get_hyvee_clinics():
    payload = {
        "operationName": "SearchPharmaciesNearPointWithCovidVaccineAvailability",
        "variables": {
            "radius": int(os.environ["HYVEE_RADIUS"]),
            "latitude": float(os.environ["HYVEE_LATITUDE"]),
            "longitude": float(os.environ["HYVEE_LONGITUDE"]),
        },
        "query": "query SearchPharmaciesNearPointWithCovidVaccineAvailability($latitude: Float\u0021, $longitude: Float\u0021, $radius: Int\u0021) {searchPharmaciesNearPoint(latitude: $latitude, longitude: $longitude, radius: $radius) {location {locationId name isCovidVaccineAvailable address {state zip}}}}",
    }
    response = requests.post(HYVEE_URL, headers=HEADERS, json=payload)

    if response.status_code == 200:
        clinics = response.json()["data"]["searchPharmaciesNearPoint"]
        if isinstance(clinics, list):
            clinics_with_vaccine = [
                {
                    **format_hyvee_data(clinic),
                    **get_appointment_info(clinic["location"]["locationId"]),
                }
                for clinic in clinics
                if clinic["location"]["isCovidVaccineAvailable"] is True
            ]
            clinics_without_vaccine = [
                format_hyvee_data(clinic)
                for clinic in clinics
                if clinic["location"]["isCovidVaccineAvailable"] is False
            ]
        else:
            logging.error("Bad response from Hy-Vee, no list in response")
            clinics_with_vaccine = []
            clinics_without_vaccine = []

    else:
        logging.error(
            "Bad response from Hy-Vee: Code {}: {}", response.status_code, response.text
        )
        clinics_with_vaccine = []
        clinics_without_vaccine = []

    return {
        "with_vaccine": clinics_with_vaccine,
        "without_vaccine": clinics_without_vaccine,
    }


def get_available_manufacturer_ids(location_id):
    payload = {
        "operationName": "GetCovidVaccineLocationAvailability",
        "variables": {"locationId": location_id},
        "query": "query GetCovidVaccineLocationAvailability($locationId: ID\u0021) {getCovidVaccineLocationAvailability(locationId: $locationId) { covidVaccineManufacturerId hasAvailability }}",
    }
    response = requests.post(HYVEE_URL, headers=HEADERS, json=payload)

    if response.status_code == 200:
        return [
            manufacturer["covidVaccineManufacturerId"]
            for manufacturer in response.json()["data"][
                "getCovidVaccineLocationAvailability"
            ]
            if manufacturer["hasAvailability"] is True
        ]
    else:
        logging.error(
            "Bad response from Hyvee: Code {}: {}", response.status_code, response.text
        )
        return []


def get_available_appointment_times(location_id, manufacturer_id):
    payload = {
        "operationName": "GetCovidVaccineTimeSlots",
        "variables": {
            "locationId": location_id,
            "covidVaccineManufacturerId": manufacturer_id,
        },
        "query": "query GetCovidVaccineTimeSlots($locationId: ID!, $covidVaccineManufacturerId: ID!) { getCovidVaccineTimeSlots(locationId: $locationId, covidVaccineManufacturerId: $covidVaccineManufacturerId)}",
    }

    response = requests.post(HYVEE_URL, headers=HEADERS, json=payload)

    if response.status_code == 200:
        return response.json()["data"]["getCovidVaccineTimeSlots"]
    else:
        logging.error(
            "Bad response from Hyvee: Code {}: {}", response.status_code, response.text
        )
        return []
