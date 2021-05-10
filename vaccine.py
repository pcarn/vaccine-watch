import os
import time

import redis

from clinics.balls import Balls
from clinics.cosentinos import Cosentinos
from clinics.hyvee import HyVee
from clinics.rapid_test_kc import RapidTestKC
from clinics.test_clinic import TestClinic
from clinics.vaccine_spotter import VaccineSpotter
from notify.console import Console
from notify.discord import Discord
from notify.slack import Slack
from notify.teams import Teams
from notify.twilio import Twilio
from notify.twitter import Twitter
from utils import env_var_is_true

redis_client = redis.Redis.from_url(os.environ["REDIS_URL"])

enabled_clinics = []
if env_var_is_true("ENABLE_BALLS"):
    enabled_clinics.append(Balls())
if env_var_is_true("ENABLE_COSENTINOS"):
    enabled_clinics.append(Cosentinos())
if env_var_is_true("ENABLE_HYVEE"):
    enabled_clinics.append(HyVee())
if env_var_is_true("ENABLE_RAPID_TEST_KC"):
    enabled_clinics.append(RapidTestKC())
if env_var_is_true("ENABLE_VACCINE_SPOTTER"):
    enabled_clinics.append(VaccineSpotter())
if env_var_is_true("ENABLE_TEST"):
    enabled_clinics.append(TestClinic())

enabled_notification_methods = []
if env_var_is_true("NOTIFY_CONSOLE"):
    enabled_notification_methods.append(Console())
if "DISCORD_WEBHOOK_URL" in os.environ:
    enabled_notification_methods.append(Discord())
if "SLACK_BOT_TOKEN" in os.environ:
    enabled_notification_methods.append(Slack())
if "TEAMS_WEBHOOK_URL" in os.environ:
    enabled_notification_methods.append(Teams())
if "TWILIO_AUTH_TOKEN" in os.environ:
    enabled_notification_methods.append(Twilio())
if "TWITTER_CONSUMER_KEY" in os.environ:
    enabled_notification_methods.append(Twitter())


def cache_key(location):
    return "{}{}".format(os.environ.get("CACHE_PREFIX", ""), location["id"])


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
        cache_value = redis_client.get(cache_key(location))
        if cache_value is None or (
            "latest_appointment_day" in location
            and cache_value.decode("utf-8")
            != location[
                "latest_appointment_day"
            ]  # There's a new day we haven't notified for
        ):
            newly_available_locations.append(location)
            redis_client.set(
                cache_key(location), location.get("latest_appointment_day", "notified")
            )
        # Reset Walgreens unavailability timer
        if "walgreens" in location["id"]:
            first_unavailable_cache_key = "{}first-unavailable-{}".format(
                os.environ.get("CACHE_PREFIX", ""), location["id"]
            )
            deleted = redis_client.delete(first_unavailable_cache_key)
            if deleted == 1:
                print("False alarm on Walgreens unavailability")

    for location in unavailable_locations:
        # Some locations tend to toggle their locations to unavailable, then back again, which leads to a lot of noise.
        # Don't treat them as unavailable until they have been for one hour
        if redis_client.get(cache_key(location)):
            first_unavailable_cache_key = "{}first-unavailable-{}".format(
                os.environ.get("CACHE_PREFIX", ""), location["id"]
            )
            first_unavailable_time = redis_client.get(first_unavailable_cache_key)
            if first_unavailable_time:
                if int(time.time()) - int(first_unavailable_time) > 60 * 60:
                    redis_client.delete(first_unavailable_cache_key)
                    redis_client.delete(cache_key(location))
                    newly_unavailable_locations.append(location)
            else:
                print("Walgreens says unavailable, going to wait before notifying")
                redis_client.set(first_unavailable_cache_key, int(time.time()))
        else:
            deleted = redis_client.delete(cache_key(location))
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
