import json
import logging
import os

import redis
import requests
import twitter

from .utils import shorten_url

redis_client = redis.Redis.from_url(os.environ["REDIS_URL"])


class Twitter:
    def __init__(self):
        if "TWITTER_CONSUMER_KEY" in os.environ:
            self.client = twitter.Api(
                consumer_key=os.environ["TWITTER_CONSUMER_KEY"],
                consumer_secret=os.environ["TWITTER_CONSUMER_SECRET"],
                access_token_key=os.environ["TWITTER_ACCESS_TOKEN_KEY"],
                access_token_secret=os.environ["TWITTER_ACCESS_TOKEN_SECRET"],
            )

    def post_tweet(self, content, in_reply_to_status_id=None):
        return self.client.PostUpdate(
            content, in_reply_to_status_id=in_reply_to_status_id
        )


client = Twitter()

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


def notify_location_available(location):
    for retry_attempt in range(0, 5):
        try:
            response = client.post_tweet(
                format_available_message(location, retry_attempt)
            )
            redis_client.set(
                "{}tweet-{}".format(os.environ.get("CACHE_PREFIX", ""), location["id"]),
                response.id,
            )
        except twitter.error.TwitterError as exception:
            if retry_attempt < 4 and exception.message[0]["code"] == 187:
                logging.warning("Duplicate tweet, will retry")
            else:
                logging.exception("Error when posting tweet")
                break
        except requests.exceptions.ConnectionError:
            logging.exception("Connection error when posting tweet")
        else:
            break
    else:
        logging.error("Five consecutive errors when posting tweet")


def notify_twitter_available_locations(locations):
    for location in locations:
        notify_location_available(location)


def notify_twitter_unavailable_locations(locations):
    for location in locations:
        try:
            previous_tweet_id = redis_client.get(
                "{}tweet-{}".format(os.environ.get("CACHE_PREFIX", ""), location["id"])
            )
            if previous_tweet_id:
                client.post_tweet(
                    format_unavailable_message(location),
                    in_reply_to_status_id=previous_tweet_id,
                )
        except twitter.error.TwitterError:
            logging.exception("Error when posting tweet")
