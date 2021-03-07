import os

from constants import TRUE_VALUES

from .console import (
    notify_console_available_clinics,
    notify_console_unavailable_clinics,
)
from .slack import notify_slack_available_clinics, notify_slack_unavailable_clinics
from .twitter import (
    notify_twitter_available_clinics,
    notify_twitter_unavailable_clinics,
)


def notify_available(clinics):
    if "SLACK_BOT_TOKEN" in os.environ:
        notify_slack_available_clinics(clinics)
    if "TWITTER_CONSUMER_KEY" in os.environ:
        notify_twitter_available_clinics(clinics)
    if (
        "NOTIFY_CONSOLE" in os.environ
        and os.environ["NOTIFY_CONSOLE"].lower() in TRUE_VALUES
    ):
        notify_console_available_clinics(clinics)


def notify_unavailable(clinics):
    if "SLACK_BOT_TOKEN" in os.environ:
        notify_slack_unavailable_clinics(clinics)
    if "TWITTER_CONSUMER_KEY" in os.environ:
        notify_twitter_unavailable_clinics(clinics)
    if (
        "NOTIFY_CONSOLE" in os.environ
        and os.environ["NOTIFY_CONSOLE"].lower() in TRUE_VALUES
    ):
        notify_console_unavailable_clinics(clinics)
