from datetime import datetime
import textwrap
from typing import Any
from slack_sdk import WebClient
from src.config.config import SLACK_TOKEN


class SlackBase:
    def __init__(self) -> None:
        self.client = WebClient(token=SLACK_TOKEN)


    def send_message(self,name: str, brand: str, country: str, languague: str, brand_report_id: str, prompt_id: str, process_id: str, prompt: str, exc: Any):
        # Message with all task details
        error_message = textwrap.dedent(f"""
            *Date/Time:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

            *Task Details:*
            • Platform: `{name}`
            • Brand: `{brand}`
            • Country: `{country}`
            • Language: `{languague}`
            • Brand Report ID: `{brand_report_id}`
            • Prompt ID: `{prompt_id}`
            • Process ID: `{process_id}`

            *Prompt:*
            ```
            {prompt}
            ```

            *Error:*
            ```
            {str(exc)}
            ```
        """).strip()
        self.client.chat_postMessage(channel="#scraper", text=error_message)
