import os

from constants import TRUE_VALUES

from .console import (
    notify_console_available_locations,
    notify_console_unavailable_locations,
)
from .discord import (
    notify_discord_available_locations,
    notify_discord_unavailable_locations,
)
from .slack import notify_slack_available_locations, notify_slack_unavailable_locations
from .twitter import (
    notify_twitter_available_locations,
    notify_twitter_unavailable_locations,
)


def notify_available(locations):
    if "SLACK_BOT_TOKEN" in os.environ:
        notify_slack_available_locations(locations)
    if "TWITTER_CONSUMER_KEY" in os.environ:
        notify_twitter_available_locations(locations)
    if "DISCORD_WEBHOOK_URL" in os.environ:
        notify_discord_available_locations(locations)
    if (
        "NOTIFY_CONSOLE" in os.environ
        and os.environ["NOTIFY_CONSOLE"].lower() in TRUE_VALUES
    ):
        notify_console_available_locations(locations)


def notify_unavailable(locations):
    if "SLACK_BOT_TOKEN" in os.environ:
        notify_slack_unavailable_locations(locations)
    if "TWITTER_CONSUMER_KEY" in os.environ:
        notify_twitter_unavailable_locations(locations)
    if "DISCORD_WEBHOOK_URL" in os.environ:
        notify_discord_unavailable_locations(locations)
    if (
        "NOTIFY_CONSOLE" in os.environ
        and os.environ["NOTIFY_CONSOLE"].lower() in TRUE_VALUES
    ):
        notify_console_unavailable_locations(locations)
