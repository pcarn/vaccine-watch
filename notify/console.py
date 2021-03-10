import json
import logging
import os

from constants import TRUE_VALUES

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
                day_string = "\ton {}".format(location["earliest_appointment_day"])
            else:
                day_string = " from [{}] to [{}]".format(
                    location["earliest_appointment_day"],
                    location["latest_appointment_day"],
                )
        else:
            day_string = ""

        message += "\n {}{}{}.\n\tSign up at {}\n\t{}".format(
            "[{}]: ".format(location["state"])
            if (len(states) > 1 and "state" in location)
            else "",
            location["name"],
            day_string,
            location["link"],
            "Zip: {}".format(location["zip"]) if "zip" in location else "",
        )
    return message


def format_unavailable_message(locations):
    message = "Vaccine appointments no longer available at {} location{}:".format(
        "these" if len(locations) > 1 else "this",
        "s" if len(locations) > 1 else "",
    )
    for location in locations:
        message += "\n {}{}".format(
            "[{}]: ".format(location["state"])
            if (len(states) > 1 and "state" in location)
            else "",
            location["name"],
        )
    return message


def notify_console_available_locations(locations):
    print("[CONSOLE] {}".format(format_available_message(locations)))


def notify_console_unavailable_locations(locations):
    print("[CONSOLE] {}".format(format_unavailable_message(locations)))
