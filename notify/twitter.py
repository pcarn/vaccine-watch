import logging
import os
from datetime import datetime

import redis
import twitter
from pytz import timezone

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


def format_available_message(clinic, retry_attempt):
    if "earliest_appointment_day" in clinic:
        if clinic["earliest_appointment_day"] == clinic["latest_appointment_day"]:
            day_string = " on {}".format(clinic["earliest_appointment_day"])
        else:
            day_string = " from {} to {}".format(
                clinic["earliest_appointment_day"], clinic["latest_appointment_day"]
            )
    else:
        day_string = ""

    return "{}Vaccine appointments available at {}{}. Sign up here{}:\n{}{}".format(
        "{}: ".format(clinic["state"]) if "state" in clinic else "",
        clinic["name"],
        day_string,
        ", zip code {}".format(clinic["zip"]) if "zip" in clinic else "",
        shorten_url(clinic["link"]),
        " ({})".format(datetime.now(timezone("US/Central")).strftime("%I:%M"))
        if retry_attempt
        else "",
    )


def format_unavailable_message(clinic):
    return "Vaccine appointments no longer available at {}.".format(clinic["name"])


def notify_clinic_available(clinic, retry_attempt=False):
    try:
        response = client.post_tweet(format_available_message(clinic, retry_attempt))
        redis_client.set("tweet-{}".format(clinic["id"]), response.id)
    except twitter.error.TwitterError as exception:
        if not retry_attempt and exception.message[0]["code"] == 170:  # Duplicate Tweet
            notify_clinic_available(clinic, retry_attempt=True)
        else:
            logging.exception("Error when posting tweet")


def notify_twitter_available_clinics(clinics):
    for clinic in clinics:
        notify_clinic_available(clinic)


def notify_twitter_unavailable_clinics(clinics):
    for clinic in clinics:
        try:
            previous_tweet_id = redis_client.get("tweet-{}".format(clinic["id"]))
            if previous_tweet_id:
                client.post_tweet(
                    format_unavailable_message(clinic),
                    in_reply_to_status_id=previous_tweet_id,
                )
        except twitter.error.TwitterError:
            logging.exception("Error when posting tweet")
