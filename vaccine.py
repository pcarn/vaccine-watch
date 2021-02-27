from clinics.hyvee import get_available_hyvees


def check_for_appointments():
    for clinic in get_available_hyvees():
        print(clinic["id"])
