import os

from clinics.hyvee import get_available_hyvees
from constants import TRUE_VALUES
from notify import notify_people


def check_for_appointments():
    clinics = []
    if os.environ["ENABLE_HYVEE"].lower() in TRUE_VALUES:
        clinics += get_available_hyvees()
    if len(clinics) > 0:
        notify_people(clinics)
