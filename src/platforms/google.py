import sys

sys.path.append(".")

from typing import Optional
from src.platforms.browser import BrowserBase
from html_to_markdown import convert_to_markdown
import logging


class GoogleScraper(BrowserBase):
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
        date: str,
    ) -> None:
        super().__init__(
            brand_report_id,
            logger,
            url,
            prompt,
            name,
            process_id,
            timeout,
            country,
            date,
        )

    def find_and_fill_input(self) -> bool:
        print("Filling input")
        if not self.page:
            return False
        try:
            try:
                self.page.type('textarea[name="q"]', self.prompt, wait=self.timeout)
            except Exception as e:
                print(f"Can not fill the prompt input {e}")
                return False
            # Validate
            self.page.click('input[type="submit"]', wait=self.timeout)
            return True
        except Exception as e:
            print(f"Error in find_and_fill_input {e}")
            return False

    def extract_response(self) -> Optional[str]:
        print("Extracting response")
        if not self.page:
            return None
        content_selector = 'div[jsmodel="k8Azyd E23uIf"]'
        see_more_selector = 'div[aria-controls="m-x-content"]'

        # click on see more (ai answer)
        if not self.page.is_element_present(see_more_selector, wait=5):
            return None
        try:
            self.page.click(see_more_selector, wait=self.timeout)
        except Exception as e:
            print(f"Unable to find the see more buttons {e}")
            return None

        # wait for content to be visible
        try:
            self.page.wait_for_element(content_selector, wait=self.timeout)
        except Exception as e:
            print(f"Unable to find the content {e}")
            return None

        try:
            content_element = self.page.wait_for_element(content_selector)
            content = content_element.html if content_element else ""
            content_markdown = convert_to_markdown(content)
            return content_markdown
        except Exception as e:
            print(f"Unable to extract content {e}")
            return None


if __name__ == "__main__":
    import time

    logger = logging.getLogger(f"{__name__}")
    google = GoogleScraper(
        logger,
        url="https://www.google.com/",
        prompt="top brands in US",
        name="google",
        process_id=f"google_{time.time()}",
        timeout=60,
        country="us",
        brand_report_id="brand-12345",
        date="2025-10-07 04:07:41.285308",
    )
    google.send_prompt()
