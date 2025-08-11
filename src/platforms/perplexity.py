import sys

sys.path.append("..")

from typing import Optional
from playwright.sync_api import ElementHandle
from src.platforms.browser import BrowserBase


class PerplexityScraper(BrowserBase):
    def __init__(
        self, url: str, prompt: str, name: str, process_id: str, headless: bool = False
    ) -> None:
        super().__init__(url, prompt, name, process_id, headless)

    def find_and_fill_input(self) -> bool:
        try:
            prompt_input_selector = 'div[id="ask-input"]'
            # trying to fill the prompt
            try:
                self.page.fill(prompt_input_selector, self.prompt, timeout=self.timeout)
            except Exception as e:
                print(f"Can not fill the prompt input {e}")
            # Validate
            self.page.keyboard.press("Enter")
            return True
        except Exception as e:
            print(f"Error in find_and_fill_input {e}")
            return False

    def extract_response(self) -> Optional[ElementHandle]:
        share_btn_selector = 'button[data-testid="share-button"]'
        content_selector = 'div[id="markdown-content-0"]'
        # Looking for the share button (it appears once the response is generated)
        try:
            self.page.wait_for_selector(share_btn_selector, timeout=self.timeout)
        except Exception as e:
            print(f"Unable to find Share button {e}")
            return None
        # Looking for the response selector
        try:
            self.page.wait_for_selector(content_selector, timeout=self.timeout)
        except Exception as e:
            print(f"Unable to find the content {e}")
            return None
        content = self.page.query_selector(content_selector)
        return content

