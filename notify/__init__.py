import os

from constants import TRUE_VALUES

from .slack import notify_slack_available_clinics, notify_slack_unavailable_clinics


def notify_available(clinics):
    if os.environ.get("SLACK_BOT_TOKEN", False):
        notify_slack_available_clinics(clinics)


def notify_unavailable(clinics):
    if os.environ.get("SLACK_BOT_TOKEN", False):
        notify_slack_unavailable_clinics(clinics)
