import sys

sys.path.append("..")

from typing import Optional
from src.platforms.browser import BrowserBase
from html_to_markdown import convert_to_markdown


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
        try:
            # trying to fill the prompt
            try:
                self.page.get_by_role("textbox").fill(self.prompt, timeout=self.timeout)
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
        content_selector = "response-container div"
        action_button = ".buttons-container-v2"

        try:
            self.page.wait_for_selector(
                action_button, state="visible", timeout=self.timeout
            )
        except Exception as e:
            print(f"Unable to find the action buttons {e}")
            return None

        try:
            self.page.wait_for_selector(
                content_selector, state="visible", timeout=self.timeout
            )
        except Exception as e:
            print(f"Unable to find the content {e}")
            return None

        content_element = self.page.query_selector(content_selector)
        content = content_element.inner_html() if content_element else ""
        content_markdown = convert_to_markdown(content)
        return content_markdown
