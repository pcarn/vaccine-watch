import os

from constants import TRUE_VALUES

from .slack import notify_slack_available_clinics, notify_slack_unavailable_clinics


def notify_available(clinics):
    if os.environ["NOTIFY_SLACK"].lower() in TRUE_VALUES:
        notify_slack_available_clinics(clinics)


def notify_unavailable(clinics):
    if os.environ["NOTIFY_SLACK"].lower() in TRUE_VALUES:
        notify_slack_unavailable_clinics(clinics)
