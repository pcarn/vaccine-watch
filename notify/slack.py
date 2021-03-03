import logging
import os

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from constants import TRUE_VALUES


def format_available_message(clinics):
    message = (
        ":large_green_circle: {}Vaccine appointments available at {} clinic{}:".format(
            "<!channel> "
            if os.environ["SLACK_TAG_CHANNEL"].lower() in TRUE_VALUES
            else "",
            "these" if len(clinics) > 1 else "this",
            "s" if len(clinics) > 1 else "",
        )
    )
    for clinic in clinics:
        if "earliest_appointment_day" in clinic:
            if clinic["earliest_appointment_day"] == clinic["latest_appointment_day"]:
                day_string = " on *{}*".format(clinic["earliest_appointment_day"])
            else:
                day_string = " from *{}* to *{}*".format(
                    clinic["earliest_appointment_day"], clinic["latest_appointment_day"]
                )
        else:
            day_string = ""

        message += "\n• *{}*: {}{}. Sign up <{}|here>, zip code {}".format(
            clinic["state"], clinic["name"], day_string, clinic["link"], clinic["zip"]
        )
    return message


def format_unavailable_message(clinics):
    message = ":red_circle: Vaccines no longer available at {} clinic{}:".format(
        "these" if len(clinics) > 1 else "this",
        "s" if len(clinics) > 1 else "",
    )
    # Add emoji
    for clinic in clinics:
        message += "\n• *{}*: {}".format(clinic["state"], clinic["name"])
    return message


def send_message_to_slack(message):
    client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
    try:
        response = client.chat_postMessage(
            channel=os.environ["SLACK_CHANNEL"], text=message
        )
    except SlackApiError:
        logging.exception("Failed to send message to slack")


def notify_slack_available_clinics(clinics):
    send_message_to_slack(format_available_message(clinics))


def notify_slack_unavailable_clinics(clinics):
    send_message_to_slack(format_unavailable_message(clinics))
