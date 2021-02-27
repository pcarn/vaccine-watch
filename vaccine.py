import os

from clinics.hyvee import get_available_hyvees

TRUE_VALUES = ["true", "1"]


def check_for_appointments():
    if os.environ["ENABLE_HYVEE"].lower() in TRUE_VALUES:
        for clinic in get_available_hyvees():
            print(clinic["id"])
