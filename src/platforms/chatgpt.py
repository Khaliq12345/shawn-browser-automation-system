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

    def wait_for_answer_complete(self, selector, timeout=60000, stable_for=2000):
        if not self.page:
            return False
        locator = self.page.locator(selector).last

        start_time = self.page.evaluate("Date.now()")
        last_text = ""
        last_change = self.page.evaluate("Date.now()")

        while self.page.evaluate("Date.now()") - start_time < timeout:
            try:
                current_text = locator.inner_text().strip()
                if current_text == "Searching the web":
                    continue

                if current_text != last_text:
                    last_text = current_text
                    last_change = self.page.evaluate("Date.now()")
                # Answer has not changed for 2 seconds
                if (
                    current_text
                    and self.page.evaluate("Date.now()") - last_change >= stable_for
                ):
                    return current_text
            except Exception as _:
                pass
            self.page.wait_for_timeout(500)
        return last_text

    def find_and_fill_input(self) -> bool:
        self.logger.info("Filling input")
        if not self.page:
            return False
        time.sleep(5)
        # trying to fill the prompt
        self.page.get_by_role("textbox", name="Chat with ChatGPT").click()
        self.page.wait_for_timeout(2000)
        self.page.get_by_role("textbox", name="Chat with ChatGPT").fill(self.prompt)
        self.page.wait_for_timeout(5000)
        self.page.keyboard.press("Enter")
        self.page.wait_for_timeout(10000)

        self.logger.info("Done Filling")
        return True

    def extract_response(self) -> Optional[str]:
        self.logger.info("Extracting response")
        if not self.page:
            return None

        if self.page.url.startswith("https://auth.openai.com/log-in-or-create-account"):
            raise RuntimeError("Redirected to Login, retring..")

        force_login_locator = self.page.locator('section[data-gate-kind="force_login"]')
        if force_login_locator.is_visible():
            raise RuntimeError("Login modal visible, retring..")

        self.page.wait_for_timeout(10000)
        content = None
        content_selector = 'li[data-message-role="assistant"]'
        self.wait_for_answer_complete(content_selector)
        self.find_and_click(
            content_selector,
            error_message="Unable to find the content",
            timeout=5 * 1000,
        )
        content = self.extract_content(content_selector)
        return content
