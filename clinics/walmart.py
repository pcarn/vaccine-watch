import os

from geopy.distance import distance

from .vaccine_spotter import VaccineSpotterClinic


class Walmart(VaccineSpotterClinic):
    def __init__(self):
        self.here = (os.environ["LATITUDE"], os.environ["LONGITUDE"])
        super().__init__()

    def should_include_location(self, location):
        coordinates = location["geometry"]["coordinates"]
        return location["properties"]["provider_brand"] == "walmart" and distance(
            self.here, (coordinates[1], coordinates[0])
        ).miles < int(os.environ["RADIUS"])

    def format_data(self, location):
        return {
            "link": "https://www.walmart.com/cp/flu-shots-immunizations/1228302",
            "id": "walmart-{}".format(location["properties"]["id"]),
            "name": "Walmart {}".format(location["properties"]["name"]),
            "state": location["properties"]["state"],
            "zip": location["properties"]["postal_code"],
        }
