import logging
import os
from datetime import datetime

from geopy.distance import distance
from pytz import timezone

from .vaccine_spotter import VaccineSpotterClinic


class Walmart(VaccineSpotterClinic):
    def __init__(self):
        self.here = (os.environ["LATITUDE"], os.environ["LONGITUDE"])
        super().__init__()

    def should_include_location(self, location):
        coordinates = location["geometry"]["coordinates"]
        longitude, latitude = coordinates
        return location["properties"]["provider_brand"] == "walmart" and distance(
            self.here, (latitude, longitude)
        ).miles < int(os.environ["RADIUS"])

    def format_data(self, location):
        zone = os.environ.get("TIMEZONE", "US/Central")
        try:
            if location["properties"]["appointments_last_fetched"]:
                appointments_last_fetched = (
                    datetime.fromisoformat(
                        location["properties"]["appointments_last_fetched"]
                    )
                    .astimezone(timezone(zone))
                    .strftime("%-I:%M")
                )
            else:
                appointments_last_fetched = None
        except (
            ValueError,
            TypeError,
        ) as e:  # Python doesn't like 2 digits for decimal fraction of second
            appointments_last_fetched = None

        return {
            "link": location["properties"]["url"],
            "id": "{}walmart-{}".format(
                os.environ.get("CACHE_PREFIX", ""), location["properties"]["id"]
            ),
            "name": "Walmart {}".format(location["properties"]["name"]),
            "state": location["properties"]["state"],
            "zip": location["properties"]["postal_code"],
            "appointments_last_fetched": appointments_last_fetched,
        }
