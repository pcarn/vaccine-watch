import json
import logging
import os

import redis
import requests
import twitter

from . import NotificationMethod
from .utils import shorten_url

redis_client = redis.Redis.from_url(os.environ["REDIS_URL"])


class Twitter(NotificationMethod):
    def __init__(self):
        if "TWITTER_CONSUMER_KEY" in os.environ:
            self.client = twitter.Api(
                consumer_key=os.environ["TWITTER_CONSUMER_KEY"],
                consumer_secret=os.environ["TWITTER_CONSUMER_SECRET"],
                access_token_key=os.environ["TWITTER_ACCESS_TOKEN_KEY"],
                access_token_secret=os.environ["TWITTER_ACCESS_TOKEN_SECRET"],
            )

    def cache_key(self, location):
        return "{}tweet-{}".format(os.environ.get("CACHE_PREFIX", ""), location["id"])

    def post_tweet(self, content, in_reply_to_status_id=None):
        return self.client.PostUpdate(
            content, in_reply_to_status_id=in_reply_to_status_id
        )

    def notify_available_locations(self, locations):
        for location in locations:
            for retry_attempt in range(0, 5):
                try:
                    response = self.post_tweet(
                        format_available_message(location, retry_attempt)
                    )
                    logging.debug("Message to twitter delivered successfully")

                    old_cache_value = redis_client.get(self.cache_key(location))
                    new_cache_value = "{},{}".format(  # Append to existing value
                        (old_cache_value.decode("utf-8") if old_cache_value else ""),
                        response.id,
                    )
                    redis_client.set(
                        self.cache_key(location),
                        new_cache_value,
                    )
                except twitter.error.TwitterError as exception:
                    if retry_attempt < 4 and exception.message[0]["code"] == 187:
                        logging.warning("Duplicate tweet, will retry")
                    else:
                        logging.exception("Error when posting tweet")
                        break
                except (requests.exceptions.RequestException, ConnectionResetError):
                    logging.exception("Connection error when posting tweet, will retry")
                else:
                    break
            else:
                logging.error("Five consecutive errors when posting tweet")

    def notify_unavailable_locations(self, locations):
        for location in locations:
            for retry_attempt in range(0, 5):
                try:
                    cache_value = redis_client.get(self.cache_key(location))
                    previous_tweet_ids = (
                        cache_value.decode("utf-8") if cache_value else ""
                    ).split(",")
                    for previous_tweet_id in previous_tweet_ids:
                        if previous_tweet_id:
                            self.post_tweet(
                                format_unavailable_message(location),
                                in_reply_to_status_id=previous_tweet_id,
                            )
                except twitter.error.TwitterError:
                    logging.exception("Error when posting tweet")
                    break
                except (requests.exceptions.RequestException, ConnectionResetError):
                    logging.exception(
                        "Connection error when posting tweet{}".format(
                            ", will retry" if retry_attempt < 4 else ""
                        )
                    )
                else:
                    redis_client.delete(self.cache_key(location))
                    break
            else:
                logging.error("Five consecutive errors when posting tweet")


emojis = [None, "😷", "💉", "😷💉", "💉😷"]

states = json.loads(os.environ["STATES"])


def format_available_message(location, retry_attempt):
    if "earliest_appointment_day" in location:
        if location["earliest_appointment_day"] == location["latest_appointment_day"]:
            day_string = " on {}".format(location["earliest_appointment_day"])
        else:
            day_string = " from {} to {}".format(
                location["earliest_appointment_day"], location["latest_appointment_day"]
            )
    else:
        day_string = ""

    return "{}Vaccine appointments available at {}{}. Sign up here{}:\n{}{}{}".format(
        "{}: ".format(location["state"])
        if (len(states) > 1 and "state" in location)
        else "",
        location["name"],
        day_string,
        ", zip code {}".format(location["zip"]) if "zip" in location else "",
        shorten_url(location["link"]),
        " (as of {})".format(location["appointments_last_fetched"])
        if location.get("appointments_last_fetched", None)
        else "",
        " {}".format(emojis[retry_attempt]) if retry_attempt > 0 else "",
    )


def format_unavailable_message(location):
    return "Vaccine appointments no longer available at {}{}.".format(
        location["name"],
        " (as of {})".format(location["appointments_last_fetched"])
        if location.get("appointments_last_fetched", None)
        else "",
    )
