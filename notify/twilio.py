import json
import logging
import os

from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client

from . import NotificationMethod
from .utils import shorten_url


class Twilio(NotificationMethod):
    def __init__(self):
        account_sid = os.environ["TWILIO_ACCOUNT_SID"]
        auth_token = os.environ["TWILIO_AUTH_TOKEN"]
        self.client = Client(account_sid, auth_token)

    def send_message_to_twilio(self, message):
        if "TWILIO_TO_NUMBERS" in os.environ:
            recipients = json.loads(os.environ["TWILIO_TO_NUMBERS"])
            for recipient in recipients:
                try:
                    response = self.client.api.account.messages.create(
                        to=recipient,
                        from_=os.environ["TWILIO_FROM_NUMBER"],
                        body=message,
                    )
                    logging.debug("Message to twilio sent successfully")
                except TwilioRestException:
                    logging.exception("Error when sending message to Twilio")

    def notify_available_locations(self, locations):
        for location in locations:
            self.send_message_to_twilio(format_available_message(location))

    def notify_unavailable_locations(self, locations):
        for location in locations:
            self.send_message_to_twilio(format_unavailable_message(location))


states = json.loads(os.environ["STATES"])


def format_available_message(location):
    if "earliest_appointment_day" in location:
        if location["earliest_appointment_day"] == location["latest_appointment_day"]:
            day_string = " on {}".format(location["earliest_appointment_day"])
        else:
            day_string = " from {} to {}".format(
                location["earliest_appointment_day"],
                location["latest_appointment_day"],
            )
    else:
        day_string = ""

    return "{}Vaccine appointments available at {}{}. Sign up here{}:\n{}{}".format(
        "{}: ".format(location["state"])
        if (len(states) > 1 and "state" in location)
        else "",
        location["name"],
        day_string,
        ", zip code {}".format(location["zip"]) if "zip" in location else "",
        shorten_url(location["link"]),
        " (as of {})".format(location["appointments_last_fetched"])
        if location.get("appointments_last_fetched", None)
        else "",
    )


def format_unavailable_message(location):
    return "Vaccine appointments no longer available at {}{}.".format(
        location["name"],
        " (as of {})".format(location["appointments_last_fetched"])
        if location.get("appointments_last_fetched", None)
        else "",
    )
