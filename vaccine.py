import os

import redis

from clinics.balls import Balls
from clinics.cosentinos import Cosentinos
from clinics.cvs import CVS
from clinics.hyvee import HyVee
from clinics.test_clinic import TestClinic
from clinics.walgreens import Walgreens
from clinics.walmart import Walmart
from notify.console import Console
from notify.discord import Discord
from notify.slack import Slack
from notify.twilio import Twilio
from notify.twitter import Twitter
from utils import env_var_is_true

redis_client = redis.Redis.from_url(os.environ["REDIS_URL"])

enabled_clinics = []
if env_var_is_true("ENABLE_BALLS"):
    enabled_clinics.append(Balls())
if env_var_is_true("ENABLE_COSENTINOS"):
    enabled_clinics.append(Cosentinos())
if env_var_is_true("ENABLE_CVS"):
    enabled_clinics.append(CVS())
if env_var_is_true("ENABLE_HYVEE"):
    enabled_clinics.append(HyVee())
if env_var_is_true("ENABLE_WALGREENS"):
    enabled_clinics.append(Walgreens())
if env_var_is_true("ENABLE_WALMART"):
    enabled_clinics.append(Walmart())
if env_var_is_true("ENABLE_TEST"):
    enabled_clinics.append(TestClinic())

enabled_notification_methods = []
if env_var_is_true("NOTIFY_CONSOLE"):
    enabled_notification_methods.append(Console())
if "DISCORD_WEBHOOK_URL" in os.environ:
    enabled_notification_methods.append(Discord())
if "SLACK_BOT_TOKEN" in os.environ:
    enabled_notification_methods.append(Slack())
if "TWILIO_AUTH_TOKEN" in os.environ:
    enabled_notification_methods.append(Twilio())
if "TWITTER_CONSUMER_KEY" in os.environ:
    enabled_notification_methods.append(Twitter())


# If already notified for a location, don't notify again.
# When a location doesn't have vaccines, reset to not notified.
def check_for_appointments():
    available_locations = []
    unavailable_locations = []
    newly_available_locations = []
    newly_unavailable_locations = []

    for clinic in enabled_clinics:
        response = clinic.get_locations()
        available_locations += response["with_vaccine"]
        unavailable_locations += response["without_vaccine"]

    for location in available_locations:
        if redis_client.get(location["id"]) is None:
            newly_available_locations.append(location)
            redis_client.set(location["id"], "notified")

    for location in unavailable_locations:
        deleted = redis_client.delete(location["id"])
        if deleted == 1:
            newly_unavailable_locations.append(location)

    if len(newly_available_locations) > 0:
        print("{} newly available locations".format(len(newly_available_locations)))
        for notification_method in enabled_notification_methods:
            notification_method.notify_available_locations(newly_available_locations)

    if len(newly_unavailable_locations) > 0:
        print("{} newly unavailable locations".format(len(newly_unavailable_locations)))
        for notification_method in enabled_notification_methods:
            notification_method.notify_unavailable_locations(
                newly_unavailable_locations
            )

    if len(newly_available_locations) == 0 and len(newly_unavailable_locations) == 0:
        print("nothing to notify")
