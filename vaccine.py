import logging
import os

import redis

from clinics.balls import Balls
from clinics.cosentinos import Cosentinos
from clinics.cvs import CVS
from clinics.hyvee import HyVee
from clinics.test_clinic import TestClinic
from clinics.walgreens import Walgreens
from clinics.walmart import Walmart
from constants import TRUE_VALUES
from notify import notify_available, notify_unavailable

redis_client = redis.Redis.from_url(os.environ["REDIS_URL"])

enabled_clinics = []
if "ENABLE_BALLS" in os.environ and os.environ["ENABLE_BALLS"].lower() in TRUE_VALUES:
    enabled_clinics.append(Balls())
if (
    "ENABLE_COSENTINOS" in os.environ
    and os.environ["ENABLE_COSENTINOS"].lower() in TRUE_VALUES
):
    enabled_clinics.append(Cosentinos())
if "ENABLE_CVS" in os.environ and os.environ["ENABLE_CVS"].lower() in TRUE_VALUES:
    enabled_clinics.append(CVS())
if "ENABLE_HYVEE" in os.environ and os.environ["ENABLE_HYVEE"].lower() in TRUE_VALUES:
    enabled_clinics.append(HyVee())
if (
    "ENABLE_WALGREENS" in os.environ
    and os.environ["ENABLE_WALGREENS"].lower() in TRUE_VALUES
):
    enabled_clinics.append(Walgreens())
if (
    "ENABLE_WALMART" in os.environ
    and os.environ["ENABLE_WALMART"].lower() in TRUE_VALUES
):
    enabled_clinics.append(Walmart())
if "ENABLE_TEST" in os.environ and os.environ["ENABLE_TEST"].lower() in TRUE_VALUES:
    enabled_clinics.append(TestClinic())

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
        notify_available(newly_available_locations)
        print("{} newly available locations".format(len(newly_available_locations)))

    if len(newly_unavailable_locations) > 0:
        notify_unavailable(newly_unavailable_locations)
        print("{} newly unavailable locations".format(len(newly_unavailable_locations)))

    if len(newly_available_locations) == 0 and len(newly_unavailable_locations) == 0:
        print("nothing to notify")

    for location in newly_unavailable_locations:
        redis_client.delete("tweet-{}".format(location["id"]))
