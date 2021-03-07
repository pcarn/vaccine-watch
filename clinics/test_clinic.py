from . import Clinic


class TestClinic(Clinic):

    clinic_a = {
        "link": "https://testclinics.fake/signup/clinic-a",
        "id": "clinic-a",
        "name": "A Clinic",
        "state": "CA",
        "zip": "90210",
        "earliest_appointment_day": "February 1 2021",
        "latest_appointment_day": "February 28 2021",
    }

    clinic_b = {
        "link": "https://testclinics.fake/signup/clinic-b",
        "id": "cosentinos-B",
        "name": "B Clinic",
        "state": "CA",
        "zip": "90211",
        "earliest_appointment_day": "February 2 2021",
        "latest_appointment_day": "February 3 2021",
    }

    clinic_c = {
        "link": "https://testclinics.fake/signup/clinic-c",
        "id": "clinic-c",
        "name": "C Clinic",
        "state": "CA",
        "zip": "90210",
        "earliest_appointment_day": "March 2 2021 9AM",
        "latest_appointment_day": "March 2 2021 1115AM",
    }

    clinicD = {
        "link": "https://testclinics.fake/signup/clinic-d",
        "id": "cosentinos-d",
        "name": "D Clinic",
        "state": "CA",
        "zip": "90211",
        "earliest_appointment_day": "March 3 2021 10AM",
        "latest_appointment_day": "March 4 2021 10AM",
    }

    flip = False

    def get_locations(self):
        first_set = [self.clinic_a, self.clinic_c]
        second_set = [self.clinic_b, self.clinicD]

        if self.flip:
            clinics_with_vaccine = first_set
            clinics_without_vaccine = second_set
        else:
            clinics_without_vaccine = first_set
            clinics_with_vaccine = second_set

        ret_dic = {
            "with_vaccine": clinics_with_vaccine,
            "without_vaccine": clinics_without_vaccine,
        }

        # invert it
        self.flip = not self.flip

        return ret_dic
