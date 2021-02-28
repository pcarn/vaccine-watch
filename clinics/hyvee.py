import json
import os

import requests


def format_hyvee_data(clinic):
    return {
        "link": "https://www.hy-vee.com/my-pharmacy/covid-vaccine-consent",
        "id": "hyvee-{}".format(clinic["location"]["locationId"]),
        "name": clinic["location"]["name"],
        "state": clinic["location"]["address"]["state"],
        "zip": clinic["location"]["address"]["zip"],
    }


def get_hyvee_clinics():
    url = "https://www.hy-vee.com/my-pharmacy/api/graphql"
    headers = {"content-type": "application/json"}
    payload = {
        "operationName": "SearchPharmaciesNearPointWithCovidVaccineAvailability",
        "variables": {
            "radius": int(os.environ["HYVEE_RADIUS"]),
            "latitude": float(os.environ["HYVEE_LATITUDE"]),
            "longitude": float(os.environ["HYVEE_LONGITUDE"]),
        },
        "query": "query SearchPharmaciesNearPointWithCovidVaccineAvailability($latitude: Float\u0021, $longitude: Float\u0021, $radius: Int\u0021) {searchPharmaciesNearPoint(latitude: $latitude, longitude: $longitude, radius: $radius) {location {locationId name isCovidVaccineAvailable address {state zip}}}}",
    }
    response = requests.post(url, headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        clinics = response.json()["data"]["searchPharmaciesNearPoint"]
        clinics_with_vaccine = [
            format_hyvee_data(clinic)
            for clinic in clinics
            if clinic["location"]["isCovidVaccineAvailable"] is True
        ]
        clinics_without_vaccine = [
            format_hyvee_data(clinic)
            for clinic in clinics
            if clinic["location"]["isCovidVaccineAvailable"] is False
        ]

    else:
        logging.error(
            "Bad response from Hyvee: Code {}: {}", response.status_code, response.text
        )
        clinics_with_vaccine = []
        clinics_without_vaccine = []

    return {
        "with_vaccine": clinics_with_vaccine,
        "without_vaccine": clinics_without_vaccine,
    }
