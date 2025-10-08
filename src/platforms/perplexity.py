import sys

sys.path.append(".")

from typing import Optional
from src.platforms.browser import BrowserBase
from html_to_markdown import convert_to_markdown
import logging


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
        print("Filling the prompt")

        if not self.page:
            return False

        self.page.sleep(5)
        self.page.mouse_press(0, 0)
        self.page.sleep(5)
        try:
            prompt_input_selector = 'div[id="ask-input"]'
            # trying to fill the prompt
            try:
                self.page.type(prompt_input_selector, self.prompt, wait=self.timeout)
            except Exception as e:
                print(f"Can not fill the prompt input {e}")
                return False

            # Validate
            try:
                submit_button = 'button[data-testid="submit-button"]'
                self.page.click(submit_button, wait=self.timeout)
            except Exception as e:
                print(f"Submit button is not available - {e}")
                return False
            return True
        except Exception as e:
            print(f"Error in find_and_fill_input {e}")
            return False

    def extract_response(self) -> Optional[str]:
        print("Extracting response")
        if not self.page:
            return None
        content = None
        share_selector = 'button[data-testid="share-button"]'
        try:
            self.page.wait_for_element(share_selector, wait=self.timeout)
        except Exception as e:
            print(f"Unable to find copy button - {e}")
            return None
        content_selector = 'div[id="markdown-content-0"]'
        content_element = self.page.wait_for_element(
            content_selector, wait=self.timeout
        )
        content = content_element.html if content_element else ""
        content_markdown = convert_to_markdown(content)
        return content_markdown


if __name__ == "__main__":
    import time

    logger = logging.getLogger(f"{__name__}")
    perplexity = PerplexityScraper(
        logger,
        url="https://www.perplexity.ai/",
        prompt="Top men'shoe brand",
        name="perplexity",
        process_id=f"perplexity_{time.time()}",
        timeout=60,
        country="us",
        brand_report_id="brand-12345",
        date="2025-10-07 04:07:41.285308",
    )
    perplexity.send_prompt()
