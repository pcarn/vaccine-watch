import os

from constants import TRUE_VALUES

from .slack import notify_slack


def notify_people(clinics):
    if os.environ["NOTIFY_SLACK"].lower() in TRUE_VALUES:
        notify_slack(clinics)
