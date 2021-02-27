import json
import os

import requests


def format_hyvee_data(clinic):
    return {
        "name": clinic["location"]["nickname"] or clinic["location"]["name"],
    }


def get_available_hyvees():
    url = "https://www.hy-vee.com/my-pharmacy/api/graphql"
    headers = {"content-type": "application/json"}
    payload = {
        "operationName": "SearchPharmaciesNearPointWithCovidVaccineAvailability",
        "variables": {
            "radius": int(os.environ["HYVEE_RADIUS"]),
            "latitude": float(os.environ["HYVEE_LATITUDE"]),
            "longitude": float(os.environ["HYVEE_LONGITUDE"]),
        },
        "query": "query SearchPharmaciesNearPointWithCovidVaccineAvailability($latitude: Float\u0021, $longitude: Float\u0021, $radius: Int\u0021 = 10) {\n searchPharmaciesNearPoint(latitude: $latitude, longitude: $longitude, radius: $radius) {\n distance\n location {\n locationId\n name\n nickname\n phoneNumber\n businessCode\n isCovidVaccineAvailable\n covidVaccineEligibilityTerms\n address {\n line1\n line2\n city\n state\n zip\n latitude\n longitude\n __typename\n }\n __typename\n }\n __typename\n }\n}\n",
    }
    response = requests.post(url, headers=headers, data=json.dumps(payload))

    clinics = response.json()["data"]["searchPharmaciesNearPoint"]
    clinics_with_vaccine = [
        format_hyvee_data(clinic)
        for clinic in clinics
        if clinic["location"]["isCovidVaccineAvailable"] is False  # change to True
    ]

    return clinics_with_vaccine


# If appointments are available,
# use redis to make sure we don't notify again until they're unavailable
