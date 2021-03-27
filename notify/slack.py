import json
import logging
import os

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from utils import env_var_is_true

from . import NotificationMethod


class Slack(NotificationMethod):
    def __init__(self):
        self.client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])

    def send_message_to_slack(self, message):
        try:
            self.client.chat_postMessage(
                channel=os.environ["SLACK_CHANNEL"], text=message
            )
            logging.debug("Message to slack sent successfully")
        except SlackApiError:
            logging.exception("Failed to send message to slack")

    def notify_available_locations(self, locations):
        self.send_message_to_slack(format_available_message(locations))

    def notify_unavailable_locations(self, locations):
        self.send_message_to_slack(format_unavailable_message(locations))


states = json.loads(os.environ["STATES"])


def format_available_message(locations):
    message = ":large_green_circle: {}Vaccine appointments available at {} location{}:".format(
        "<!channel> " if env_var_is_true("SLACK_TAG_CHANNEL") else "",
        "these" if len(locations) > 1 else "this",
        "s" if len(locations) > 1 else "",
    )
    for location in locations:
        if "earliest_appointment_day" in location:
            if (
                location["earliest_appointment_day"]
                == location["latest_appointment_day"]
            ):
                day_string = " on *{}*".format(location["earliest_appointment_day"])
            else:
                day_string = " from *{}* to *{}*".format(
                    location["earliest_appointment_day"],
                    location["latest_appointment_day"],
                )
        else:
            day_string = ""

        message += "\n• {}{}{}. Sign up <{}|here>{}{}".format(
            "*{}*: ".format(location["state"])
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
    message = ":red_circle: Vaccine appointments no longer available at {} location{}:".format(
        "these" if len(locations) > 1 else "this",
        "s" if len(locations) > 1 else "",
    )
    for location in locations:
        message += "\n• {}{}{}".format(
            "*{}*: ".format(location["state"])
            if (len(states) > 1 and "state" in location)
            else "",
            location["name"],
            " (as of {})".format(location["appointments_last_fetched"])
            if location.get("appointments_last_fetched", None)
            else "",
        )
    return message
