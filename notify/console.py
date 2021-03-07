import logging
import os

from constants import TRUE_VALUES


def format_available_message(clinics):
    message = "Vaccine appointments available at {} clinic{}:".format(
        "these" if len(clinics) > 1 else "this",
        "s" if len(clinics) > 1 else "",
    )
    for clinic in clinics:
        if "earliest_appointment_day" in clinic:
            if clinic["earliest_appointment_day"] == clinic["latest_appointment_day"]:
                day_string = "\ton {}".format(clinic["earliest_appointment_day"])
            else:
                day_string = " from [{}] to [{}]".format(
                    clinic["earliest_appointment_day"], clinic["latest_appointment_day"]
                )
        else:
            day_string = ""

        message += "\n {}{}{}.\n\tSign up at {}\n\t{}".format(
            "[{}]: ".format(clinic["state"]) if "state" in clinic else "",
            clinic["name"],
            day_string,
            clinic["link"],
            "Zip: {}".format(clinic["zip"]) if "zip" in clinic else "",
        )
    return message


def format_unavailable_message(clinics):
    message = "Vaccine appointments no longer available at {} clinic{}:".format(
        "these" if len(clinics) > 1 else "this",
        "s" if len(clinics) > 1 else "",
    )
    for clinic in clinics:
        message += "\n {}{}".format(
            "[{}]: ".format(clinic["state"]) if "state" in clinic else "",
            clinic["name"],
        )
    return message


def notify_console_available_clinics(clinics):
    print("[CONSOLE] {}".format(format_available_message(clinics)))


def notify_console_unavailable_clinics(clinics):
    print("[CONSOLE] {}".format(format_unavailable_message(clinics)))
