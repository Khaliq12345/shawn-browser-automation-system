from slack_sdk import WebClient
from src.config.config import SLACK_TOKEN


class SlackBase:
    def __init__(self) -> None:
        self.client = WebClient(token=SLACK_TOKEN)

    def send_message(self, error: str):
        self.client.chat_postMessage(channel="#scraper", text=error)
