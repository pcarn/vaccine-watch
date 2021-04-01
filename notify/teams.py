import json
import logging
import os

import requests

from utils import timeout_amount

from . import NotificationMethod


class Teams(NotificationMethod):
    def notify_available_locations(self, locations):
        send_message_to_teams(format_available_message(locations))

    def notify_unavailable_locations(self, locations):
        send_message_to_teams(format_unavailable_message(locations))


states = json.loads(os.environ["STATES"])


def format_available_message(locations):
    message = "\u2705 Vaccine appointments available at {} location{}:".format(
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

        message += "\n\n* {}{}{}. Sign up **[here]({})**{}{}".format(
            "**{}**: ".format(location["state"])
            if (len(states) > 1 and "state" in location)
            else "",
            location["name"],
            day_string,
            location["link"],
            ", zip code {}".format(location["zip"]) if "zip" in location else "",
            " (as of {})".format(location["appointments_last_fetched"])
            if location.get("appointments_last_fetched", None)
            else "",
        )
    return message


def format_unavailable_message(locations):
    message = (
        "\u274C Vaccine appointments no longer available at {} location{}:".format(
            "these" if len(locations) > 1 else "this",
            "s" if len(locations) > 1 else "",
        )
    )
    for location in locations:
        message += "\n\n* {}{}{}".format(
            "**{}**: ".format(location["state"])
            if (len(states) > 1 and "state" in location)
            else "",
            location["name"],
            " (as of {})".format(location["appointments_last_fetched"])
            if location.get("appointments_last_fetched", None)
            else "",
        )
    return message


def send_message_to_teams(message):
    webhook_url = os.environ["TEAMS_WEBHOOK_URL"]
    data = {"text": message}
    try:
        response = requests.post(webhook_url, json=data, timeout=timeout_amount)
        response.raise_for_status()
        logging.debug("Message to teams sent successfully")
    except requests.exceptions.RequestException:
        logging.exception("Error sending message to teams")
