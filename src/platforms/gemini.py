import sys

sys.path.append("..")

from typing import Optional
from playwright.sync_api import ElementHandle
from src.platforms.browser import BrowserBase


class GeminiScraper(BrowserBase):
    def __init__(
        self, url: str, prompt: str, name: str, process_id: str, headless: bool = False
    ) -> None:
        super().__init__(url, prompt, name, process_id, headless)
        self.timeout = 120000

    def find_and_fill_input(self) -> bool:
        try:
            prompt_input_selector = 'textarea[name="q"]'
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

    def extract_response(self) -> Optional[str]:
        content_selector = 'div[id="m-x-content"]'
        show_more_button = 'div[class="kHtcsd"]'

        # Looking for the response footer (it appears once the response is generated)
        try:
            self.page.click(show_more_button, timeout=self.timeout)
            self.page.wait_for_timeout(timeout=3000)
        except Exception as e:
            print(f"Unable to find the Show more button {e}")
            return None

        try:
            self.page.wait_for_selector(content_selector, timeout=self.timeout)
        except Exception as e:
            print(f"Unable to find the content {e}")
            return None

        content = self.page.query_selector(content_selector).inner_html()
        return content
