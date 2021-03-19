import json
import logging
import os

import requests

from . import Clinic


# Not using VaccineSpotter so that we get more frequent updates
class CVS(Clinic):
    def __init__(self):
        self.allow_list = json.loads(os.environ["CVS_ALLOW_LIST"])
        self.block_list = json.loads(os.environ.get("CVS_BLOCK_LIST", "{}"))
        self.states = json.loads(os.environ["STATES"])

    def get_locations(self):
        url = "https://www.cvs.com/immunizations/covid-19-vaccine.vaccine-status.json?vaccineinfo"
        response = requests.get(url)
        site_locked_out = locked_out()
        locations_with_vaccine = []
        locations_without_vaccine = []

        if response.status_code == 200:
            data = response.json()["responsePayloadData"]["data"]
            for state in self.states:
                try:
                    locations = data[state]
                except KeyError:
                    logging.info("{} not included in CVS data yet".format(state))
                    continue

                for location in locations:
                    if location["city"] in self.allow_list[state]:
                        if location["status"] == "Available":
                            if site_locked_out:
                                logging.info(
                                    "Would have notified for CVS {}, {} but site is locked out".format(
                                        location["city"], state
                                    )
                                )
                            else:
                                locations_with_vaccine.append(format_data(location))
                        elif location["status"] == "Fully Booked":
                            locations_without_vaccine.append(format_data(location))
                        else:
                            logging.error(
                                "Unknown location status from CVS: {}".format(
                                    location["status"]
                                )
                            )
                    elif (
                        state not in self.block_list
                        or location["city"] not in self.block_list[state]
                    ):
                        logging.warning(
                            "New city found for CVS: {}, {}. Add to allow list or block list.".format(
                                location["city"], state
                            )
                        )

        else:
            logging.error(
                "Bad response from CVS: Code {}: {}".format(
                    response.status_code, response.text
                )
            )

        return {
            "with_vaccine": locations_with_vaccine,
            "without_vaccine": locations_without_vaccine,
        }


# CVS shows locations as available, but locks people out while they're adding locations.
# Only report as available if you can register
def locked_out():
    url = "https://www.cvs.com/vaccine/intake/store/cvd-schedule?icid=coronavirus-lp-vaccine-pa-statetool"
    response = requests.get(url)
    if response.status_code == 200:
        return "Please check back later" in response.text
    else:
        return True  # Locked out if we can't get there


def format_data(location):
    return {
        "id": "{}cvs-{}-{}".format(
            os.environ.get("CACHE_PREFIX", ""), location["state"], location["city"]
        ),
        "state": location["state"],
        "name": "CVS {}".format(
            " ".join([word.capitalize() for word in location["city"].split(" ")])
        ),
        "link": "https://www.cvs.com/immunizations/covid-19-vaccine",
    }
