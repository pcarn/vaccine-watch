import logging
import os

import redis

from clinics.hyvee import HyVee
from clinics.walgreens import Walgreens
from constants import TRUE_VALUES
from notify import notify_available, notify_unavailable

redis_client = redis.Redis.from_url(os.environ["REDIS_URL"])
hyvee = HyVee()
walgreens = Walgreens()
enabled_clinics = []
if "ENABLE_HYVEE" in os.environ and os.environ["ENABLE_HYVEE"].lower() in TRUE_VALUES:
    enabled_clinics.append(hyvee)
if (
    "ENABLE_WALGREENS" in os.environ
    and os.environ["ENABLE_WALGREENS"].lower() in TRUE_VALUES
):
    enabled_clinics.append(walgreens)

# If already notified for a clinic, don't notify again.
# When a clinic doesn't have vaccines, reset to not notified.
def check_for_appointments():
    available_clinics = []
    unavailable_clinics = []
    newly_available_clinics = []
    newly_unavailable_clinics = []

    for clinic in enabled_clinics:
        response = clinic.get_locations()
        available_clinics += response["with_vaccine"]
        unavailable_clinics += response["without_vaccine"]

    for clinic in available_clinics:
        if redis_client.get(clinic["id"]) is None:
            newly_available_clinics.append(clinic)
            redis_client.set(clinic["id"], "notified")

    for clinic in unavailable_clinics:
        deleted = redis_client.delete(clinic["id"])
        if deleted == 1:
            newly_unavailable_clinics.append(clinic)

    if len(newly_available_clinics) > 0:
        notify_available(newly_available_clinics)
        print("{} newly available clinics".format(len(newly_available_clinics)))

    if len(newly_unavailable_clinics) > 0:
        notify_unavailable(newly_unavailable_clinics)
        print("{} newly unavailable clinics".format(len(newly_unavailable_clinics)))

    if len(newly_available_clinics) == 0 and len(newly_unavailable_clinics) == 0:
        print("nothing to notify")

    for clinic in newly_unavailable_clinics:
        redis_client.delete("tweet-{}".format(clinic["id"]))
