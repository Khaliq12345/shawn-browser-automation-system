import sys



sys.path.append(".")

import time
from typing import Optional
from src.platforms.browser import BrowserBase


class ChatGPTScraper(BrowserBase):
    def __init__(
        self,
        logger,
        url: str,
        prompt: str,
        name: str,
        process_id: str,
        timeout: int,
        country: str,
        brand_report_id: str,
        prompt_id: str,
        date: str,
        languague: str,
        brand: str,
    ) -> None:
        super().__init__(
            brand_report_id,
            prompt_id,
            logger,
            url,
            prompt,
            name,
            process_id,
            timeout,
            country,
            date,
            languague,
            brand,
        )

    def find_and_fill_input(self) -> bool:
        self.logger.info("Filling input")
        if not self.page:
            return False
        time.sleep(5)
        # trying to fill the prompt
        prompt_input_selector = 'div[id="prompt-textarea"]'  # "#prompt-textarea"
        self.find_and_click(prompt_input_selector, error_message="Can not fill the prompt input", timeout=5*1000)
        self.page.fill(prompt_input_selector, value=self.prompt)
        self.logger.info("Done Filling")

        # Validate
        self.find_and_click('button[data-testid="send-button"]', error_message="Can not send prompt", timeout=5*1000, click=True)
        return True

    def extract_response(self) -> Optional[str]:
        self.logger.info("Extracting response")
        if not self.page:
            return None

        content = None
        copy_selector = 'div.justify-start button[data-testid="copy-turn-action-button"]'

        self.find_and_click(copy_selector, error_message="Unable to find copy button",  timeout=20*1000)


        content_selector = 'article[data-turn="assistant"]'
        self.find_and_click(content_selector, error_message="Unable to find the content", timeout=5*1000)
        content = self.extract_content(content_selector)
        return content
