import json
import logging
import os

from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client

from .utils import shorten_url

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


def send_message_to_twilio(message):
    account_sid = os.environ["TWILIO_ACCOUNT_SID"]
    auth_token = os.environ["TWILIO_AUTH_TOKEN"]
    client = Client(account_sid, auth_token)

    if "TWILIO_TO_NUMBERS" in os.environ:
        recipients = json.loads(os.environ["TWILIO_TO_NUMBERS"])
        for recipient in recipients:
            try:
                response = client.api.account.messages.create(
                    to=recipient, from_=os.environ["TWILIO_FROM_NUMBER"], body=message
                )
                logging.info(
                    "Payload delivered successfully, code {}.".format(response.status)
                )
            except TwilioRestException as e:
                logging.exception(e)


def notify_twilio_available_locations(locations):
    for location in locations:
        send_message_to_twilio(format_available_message(location))


def notify_twilio_unavailable_locations(locations):
    for location in locations:
        send_message_to_twilio(format_unavailable_message(location))
