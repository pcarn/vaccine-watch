import json
import logging
import os

import requests

from . import NotificationMethod
from .utils import shorten_url


class Discord(NotificationMethod):
    def notify_available_locations(self, locations):
        send_message_to_discord(format_available_message(locations))

    def notify_unavailable_locations(self, locations):
        send_message_to_discord(format_unavailable_message(locations))


states = json.loads(os.environ["STATES"])


def format_available_message(locations):
    message = ":green_circle: Vaccine appointments available at {} location{}:".format(
        "these" if len(locations) > 1 else "this",
        "s" if len(locations) > 1 else "",
    )
    for location in locations:
        if "earliest_appointment_day" in location:
            if (
                location["earliest_appointment_day"]
                == location["latest_appointment_day"]
            ):
                day_string = " on **{}**".format(location["earliest_appointment_day"])
            else:
                day_string = " from **{}** to **{}**".format(
                    location["earliest_appointment_day"],
                    location["latest_appointment_day"],
                )
        else:
            day_string = ""

        message += "\n• {}{}{}. Sign up here: {}{}{}".format(
            "**{}**: ".format(location["state"])
            if (len(states) > 1 and "state" in location)
            else "",
            location["name"],
            day_string,
            shorten_url(location["link"]),
            ", zip code {}".format(location["zip"]) if "zip" in location else "",
            " (as of {})".format(location["appointments_last_fetched"])
            if location.get("appointments_last_fetched", None)
            else "",
        )
    return message


def format_unavailable_message(locations):
    message = ":red_circle: Vaccine appointments no longer available at {} location{}:".format(
        "these" if len(locations) > 1 else "this",
        "s" if len(locations) > 1 else "",
    )
    for location in locations:
        message += "\n• {}{}{}".format(
            "**{}**: ".format(location["state"])
            if (len(states) > 1 and "state" in location)
            else "",
            location["name"],
            " (as of {})".format(location["appointments_last_fetched"])
            if location.get("appointments_last_fetched", None)
            else "",
        )
    return message


def send_message_to_discord(message):
    webhook_url = os.environ["DISCORD_WEBHOOK_URL"]
    data = {"content": message}
    try:
        response = requests.post(webhook_url, json=data)
        response.raise_for_status()
        logging.debug("Message to discord sent successfully")
    except requests.exceptions.HTTPError:
        logging.exception("Error sending message to discord")
