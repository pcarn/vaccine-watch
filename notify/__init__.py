class NotificationMethod:
    """
    Base class for notification methods.
    The subclass should format the data as desired, and send the notification.
    """

    def notify_available_locations(self, locations):
        """
        Notifies that locations are available
        locations: a list of dicts with shape {
          "id": id of the location,
          "name": name of the location
          "link": link to sign up
          "earliest_appointment_day": (string, optional), day of the earliest appointment in human-readable format
          "latest_appointment_day": (string, optional), day of the latest appointment in human-readable format
          "zip": (string, optional), zip code of the location
          "state": (string, optional), state the location is in, 2 letter abbreviation preferred
        }
        """
        raise NotImplementedError

    def notify_unavailable_locations(self, locations):
        """
        Notifies that locations are now unavailable
        locations: a list of dicts with shape {
          "id": id of the location,
          "name": name of the location
          "link": link to sign up
          "earliest_appointment_day": (string, optional), day of the earliest appointment in human-readable format
          "latest_appointment_day": (string, optional), day of the latest appointment in human-readable format
          "zip": (string, optional), zip code of the location
          "state": (string, optional), state the location is in, 2 letter abbreviation preferred
        }
        """
        raise NotImplementedError
