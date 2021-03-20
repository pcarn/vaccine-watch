import itertools
import logging
import os
from datetime import datetime

import requests

from . import Clinic

HYVEE_URL = "https://www.hy-vee.com/my-pharmacy/api/graphql"
HEADERS = {"content-type": "application/json"}


class HyVee(Clinic):
    def get_locations(self):
        payload = {
            "operationName": "SearchPharmaciesNearPointWithCovidVaccineAvailability",
            "variables": {
                "radius": int(os.environ["RADIUS"]),
                "latitude": float(os.environ["LATITUDE"]),
                "longitude": float(os.environ["LONGITUDE"]),
            },
            "query": "query SearchPharmaciesNearPointWithCovidVaccineAvailability($latitude: Float\u0021, $longitude: Float\u0021, $radius: Int\u0021) {searchPharmaciesNearPoint(latitude: $latitude, longitude: $longitude, radius: $radius) {location {locationId name isCovidVaccineAvailable address {state zip}}}}",
        }
        response = requests.post(HYVEE_URL, headers=HEADERS, json=payload)

        if response.status_code == 200:
            locations = response.json()["data"]["searchPharmaciesNearPoint"]
            if isinstance(locations, list):
                locations_with_vaccine = [
                    {
                        **format_data(location),
                        **get_appointment_info(location["location"]["locationId"]),
                    }
                    for location in locations
                    if location["location"]["isCovidVaccineAvailable"] is True
                ]
                locations_without_vaccine = [
                    format_data(location)
                    for location in locations
                    if location["location"]["isCovidVaccineAvailable"] is False
                ]
            else:
                logging.warning("Bad response from Hy-Vee, no list in response")
                locations_with_vaccine = []
                locations_without_vaccine = []

        else:
            logging.error(
                "Bad response from Hy-Vee: Code {}".format(response.status_code)
            )
            locations_with_vaccine = []
            locations_without_vaccine = []

        return {
            "with_vaccine": locations_with_vaccine,
            "without_vaccine": locations_without_vaccine,
        }


def get_available_manufacturer_ids(location_id):
    payload = {
        "operationName": "GetCovidVaccineLocationAvailability",
        "variables": {"locationId": location_id},
        "query": "query GetCovidVaccineLocationAvailability($locationId: ID\u0021) {getCovidVaccineLocationAvailability(locationId: $locationId) { covidVaccineManufacturerId hasAvailability }}",
    }
    response = requests.post(HYVEE_URL, headers=HEADERS, json=payload)

    if response.status_code == 200:
        data = response.json()["data"]["getCovidVaccineLocationAvailability"]
        if isinstance(data, list):
            return [
                manufacturer["covidVaccineManufacturerId"]
                for manufacturer in data
                if manufacturer["hasAvailability"] is True
            ]
        else:
            logging.warning("Bad response from Hy-Vee, no list in response")
            return []
    else:
        logging.error("Bad response from Hy-Vee: Code {}".format(response.status_code))
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
        data = response.json().get("data", {}).get("getCovidVaccineTimeSlots")
        if isinstance(data, list):
            return data
        else:
            logging.warning("Bad response from Hy-Vee, no list in response")
            return []
    else:
        logging.error("Bad response from Hy-Vee: Code {}".format(response.status_code))
        return []


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


def format_data(location):
    return {
        "link": "https://www.hy-vee.com/my-pharmacy/covid-vaccine-consent",
        "id": "{}hyvee-{}".format(
            os.environ.get("CACHE_PREFIX", ""), location["location"]["locationId"]
        ),
        "name": "Hy-Vee {}".format(location["location"]["name"]),
        "state": location["location"]["address"]["state"],
        "zip": location["location"]["address"]["zip"],
    }
