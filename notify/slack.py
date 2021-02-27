import os

from slack_sdk import WebClient


def format_message(clinics):
    return "hi"


def notify_slack(clinics):
    client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
    message = format_message(clinics)
    print(message)
    # response = client.chat_postMessage(channel=os.environ['SLACK_CHANNEL'], text=message)
