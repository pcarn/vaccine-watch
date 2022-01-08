import os

from utils import env_var_is_true


class TestClinic:
    """
    Base class for Clinics offering tests, not vaccines
    """

    def get_locations(self):
        """
        Returns a dict with keys "with_vaccine", "without_vaccine".
        Yes, it's for tests, but for compatibility the keys are vaccine
        Each is a list of dicts with shape {
          "id": id of the location,
          "test_type": (string) Type of the test (PCR Test, Rapid Test)
          "name": name of the location
          "link": link to sign up
          "appointment_dates": (array of strings, optional), days of the appointments available in human-readable format
          "zip": (string, optional), zip code of the location
          "state": (string, optional), state of the location (2 letter abbreviation preferred)
        }
        """
        raise NotImplementedError
