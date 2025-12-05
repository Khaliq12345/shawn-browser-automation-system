import sys


sys.path.append(".")

import time
from typing import Optional
from src.platforms.browser import BrowserBase


class PerplexityScraper(BrowserBase):
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
        self.logger.info("Filling the prompt")

        if not self.page:
            return False

        time.sleep(5)
        prompt_input_selector = 'div[id="ask-input"]'
        # trying to fill the prompt
        self.find_and_click(prompt_input_selector, "Can not fill the prompt input", timeout=self.timeout)
        self.page.fill(prompt_input_selector, value=self.prompt)

        # Validate
        submit_button = 'button[data-testid="submit-button"]'
        self.find_and_click(submit_button, "Submit button is not available ", timeout=self.timeout, click=True)

        return True

    def extract_response(self) -> Optional[str]:
        self.logger.info("Extracting response")
        if not self.page:
            return None

        content = None
        share_selector = 'button[data-testid="share-button"]'
        self.find_and_click(share_selector, "Unable to find copy button", timeout=self.timeout)

        # Get content
        content_selector = 'div[id="markdown-content-0"]'   
        self.find_and_click(content_selector, "Unable to find content", timeout=self.timeout)
        content = self.extract_content(content_selector)
        return content
