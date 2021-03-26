from . import Clinic


class TestClinic(Clinic):

    location_a = {
        "link": "https://testlocations.fake/signup/location-a",
        "id": "location-a",
        "name": "Test Location A",
        "state": "CA",
        "zip": "90210",
        "earliest_appointment_day": "February 1 2021",
        "latest_appointment_day": "February 28 2021",
    }

    location_b = {
        "link": "https://testlocations.fake/signup/location-b",
        "id": "location-b",
        "name": "Test Location B",
        "state": "CA",
        "zip": "90211",
        "earliest_appointment_day": "February 2 2021",
        "latest_appointment_day": "February 3 2021",
    }

    location_c = {
        "link": "https://testlocations.fake/signup/location-c",
        "id": "location-c",
        "name": "Test Location C",
        "state": "CA",
        "zip": "90210",
        "earliest_appointment_day": "March 2 2021 9AM",
        "latest_appointment_day": "March 2 2021 1115AM",
    }

    location_d = {
        "link": "https://testlocations.fake/signup/location-d",
        "id": "location-d",
        "name": "Test Location D",
        "state": "CA",
        "zip": "90211",
        "earliest_appointment_day": "March 3 2021 10AM",
        "latest_appointment_day": "March 4 2021 10AM",
    }

    flip = False

    def get_locations(self):
        first_set = [self.location_a, self.location_c]
        second_set = [self.location_b, self.location_d]

        locations_with_vaccine = first_set
        locations_without_vaccine = second_set

        if self.flip:
            locations_with_vaccine, locations_without_vaccine = (
                locations_without_vaccine,
                locations_with_vaccine,
            )

        ret_dic = {
            "with_vaccine": locations_with_vaccine,
            "without_vaccine": locations_without_vaccine,
        }

        # invert it
        self.flip = not self.flip

        return ret_dic
