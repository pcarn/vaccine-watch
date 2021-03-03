class Clinic:
    # Returns a dict with keys "with_vaccine", "without_vaccine".
    # Each is a list of dicts with shape {
    #   "id": id of the clinic,
    #   "name": name of the location
    #   "link": link to sign up
    #   "earliest_appointment_day": (string, optional), day of the earliest appointment in human-readable format
    #   "latest_appointment_day": (string, optional), day of the latest appointment in human-readable format
    #   "state": state the location is in, 2 letter abbreviation preferred
    #   "zip": zip code of the location
    # }
    def get_locations(self):
        raise NotImplementedError
