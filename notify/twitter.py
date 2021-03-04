import logging
import os

import redis
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


def format_available_message(clinic):
    if "earliest_appointment_day" in clinic:
        if clinic["earliest_appointment_day"] == clinic["latest_appointment_day"]:
            day_string = " on {}".format(clinic["earliest_appointment_day"])
        else:
            day_string = " from {} to {}".format(
                clinic["earliest_appointment_day"], clinic["latest_appointment_day"]
            )
    else:
        day_string = ""

    return "{}Vaccine appointments available at {}{}. Sign up here, zip code {}:\n{}".format(
        "{}: ".format(clinic["state"]) if "state" in clinic else "",
        clinic["name"],
        day_string,
        clinic["zip"],
        shorten_url(clinic["link"]),
    )


def format_unavailable_message(clinic):
    return "Vaccine appointments no longer available at {}.".format(clinic["name"])


def notify_twitter_available_clinics(clinics):
    for clinic in clinics:
        try:
            response = client.post_tweet(format_available_message(clinic))
            redis_client.set("tweet-{}".format(clinic["id"]), response.id)
        except twitter.error.TwitterError:
            logging.exception("Error when posting tweet")


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
