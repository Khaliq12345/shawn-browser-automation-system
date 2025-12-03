import sys


sys.path.append(".")

from typing import Optional
from src.platforms.browser import BrowserBase
from html_to_markdown import convert_to_markdown


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
        print("Filling input")
        if not self.page:
            return False
        try:
            self.page.sleep(5)
            self.page.mouse_press(0, 0)
            self.page.sleep(5)
            # trying to fill the prompt
            prompt_input_selector = 'div[id="prompt-textarea"]'  # "#prompt-textarea"
            try:
                self.page.type(prompt_input_selector, self.prompt, wait=self.timeout)
                print("Done Filling")
            except Exception as e:
                print(f"Can not fill the prompt input {e}")
                return False
            # Validate
            self.page.click('button[data-testid="send-button"]', wait=self.timeout)
            return True
        except Exception as e:
            print(f"Error in find_and_fill_input {e}")
            return False

    def extract_response(self) -> Optional[str]:
        print("extracting response")
        if not self.page:
            return None
        content = None
        copy_selector = (
            'div.justify-start button[data-testid="copy-turn-action-button"]'
        )
        try:
            self.page.wait_for_element(copy_selector, wait=self.timeout)
        except Exception as e:
            print(f"Unable to find copy button {e}")
            return None

        content_selector = 'article[data-turn="assistant"]'
        content_element = self.page.wait_for_element(
            content_selector, wait=self.timeout
        )
        content = content_element.html if content_element else ""
        content_markdown = convert_to_markdown(content)
        return content_markdown
