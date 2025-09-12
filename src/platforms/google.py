import sys

sys.path.append("..")

from typing import Optional
from src.platforms.browser import BrowserBase
from html_to_markdown import convert_to_markdown
from playwright.sync_api import expect


class GoogleScraper(BrowserBase):
    def __init__(
        self,
        browser,
        logger,
        url: str,
        prompt: str,
        name: str,
        process_id: str,
        timeout: int,
        country: str,
    ) -> None:
        super().__init__(
            browser, logger, url, prompt, name, process_id, timeout, country
        )

    def find_and_fill_input(self) -> bool:
        try:
            prompt_input_selector = 'textarea[name="q"]'
            # trying to fill the prompt
            try:
                self.page.fill(prompt_input_selector, self.prompt, timeout=self.timeout)
            except Exception as e:
                print(f"Can not fill the prompt input {e}")
                return False
            # Validate
            self.page.keyboard.press("Enter")
            self.page.wait_for_load_state("load", timeout=self.timeout)
            return True
        except Exception as e:
            print(f"Error in find_and_fill_input {e}")
            return False

    def extract_response(self) -> Optional[str]:
        print("Extracting response")
        content_selector = 'div[id="m-x-content"]'
        show_more_button = 'div[class="kHtcsd"]'

        try:
            expect(self.page.locator(show_more_button).first).to_be_visible()
            self.page.click(show_more_button)
        except Exception as e:
            print(f"Unable to find the Show more button {e}")
            return None

        try:
            expect(self.page.locator(content_selector).first).to_be_visible()
        except Exception as e:
            print(f"Unable to find the content {e}")
            return None

        content_element = self.page.query_selector(content_selector)
        content = content_element.inner_html() if content_element else ""
        content_markdown = convert_to_markdown(content)
        return content_markdown
