import os
from slack_sdk import WebClient

def post_to_slack(message, channel=None):
    client = WebClient(token=os.environ.get("SLACK_BOT_TOKEN"))
    client.chat_postMessage(
        channel=channel or os.environ.get("SLACK_CHANNEL", "#alerts"),
        text=message
    )
