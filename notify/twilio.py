import json
import logging
import os

from twilio.rest import Client

from .utils import shorten_url

states = json.loads(os.environ["STATES"])

def format_available_message(locations):
    message = "Vaccine appointments available at {} location{}:".format(
        "these" if len(locations) > 1 else "this",
        "s" if len(locations) > 1 else "",
    )
    for location in locations:
        if "earliest_appointment_day" in location:
            if (
                location["earliest_appointment_day"]
                == location["latest_appointment_day"]
            ):
                day_string = " on {}".format(location["earliest_appointment_day"])
            else:
                day_string = " from {} to {}".format(
                    location["earliest_appointment_day"],
                    location["latest_appointment_day"],
                )
        else:
            day_string = ""

        message += "\n• {}{}{}. Sign up here: {}{}".format(
            "{}: ".format(location["state"])
            if (len(states) > 1 and "state" in location)
            else "",
            location["name"],
            day_string,
            shorten_url(location["link"]),
            ", zip code {}".format(location["zip"]) if "zip" in location else "",
        )
    return message


def format_unavailable_message(locations):
    message = "Vaccine appointments no longer available at {} location{}:".format(
        "these" if len(locations) > 1 else "this",
        "s" if len(locations) > 1 else "",
    )
    for location in locations:
        message += "\n• {}{}".format(
            location["state"]
            if (len(states) > 1 and "state" in location)
            else "",
            location["name"],
        )
    return message


def send_message_to_twilio(message):
    account_sid = os.environ['TWILIO_ACCOUNT_SID']
    auth_token = os.environ['TWILIO_AUTH_TOKEN']
    client = Client(account_sid, auth_token)

    if "TWILIO_TO_NUMBERS" in os.environ:
        recipients = json.loads(os.environ["TWILIO_TO_NUMBERS"])
        for recipient in recipients:
            try:
                message = client.api.account.messages.create(
                    to=recipient,
                    from_=os.environ["TWILIO_FROM_NUMBER"],
                    body=message
                )
                logging.info(
                    "Payload delivered successfully, code {}.".format(message.status)
                )
            except:
                logging.exception("Error sending message to twilio")


def notify_twilio_available_locations(locations):
    send_message_to_twilio(format_available_message(locations))


def notify_twilio_unavailable_locations(locations):
    send_message_to_twilio(format_unavailable_message(locations))