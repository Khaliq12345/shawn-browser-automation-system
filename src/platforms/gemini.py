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
            prompt_input_selector = 'div[role="textbox"].ql-editor.textarea'
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
        content_selector = ".response-container-content"
        footer_selector = ".response-container-footer"
        # Looking for the response footer (it appears once the response is generated)
        try:
            self.page.wait_for_selector(footer_selector, timeout=self.timeout)
        except Exception as e:
            print(f"Unable to find Response Footer {e}")
            return None
        # Looking for the response selector
        try:
            self.page.wait_for_selector(content_selector, timeout=self.timeout)
        except Exception as e:
            print(f"Unable to find the content {e}")
            return None
        content = self.page.query_selector(content_selector)
        return content
