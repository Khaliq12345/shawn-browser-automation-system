import sys

sys.path.append("..")

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
    ) -> None:
        super().__init__(logger, url, prompt, name, process_id, timeout, country)

    def find_and_fill_input(self) -> bool:
        try:
            self.page.wait_for_timeout(5000)
            self.page.mouse.click(0, 0)
            self.page.wait_for_timeout(5000)
            # trying to fill the prompt
            prompt_input_selector = 'div[id="prompt-textarea"]'  # "#prompt-textarea"
            try:
                print("Filling input")
                self.page.fill(prompt_input_selector, self.prompt, timeout=self.timeout)
                print("Done FIlling")
            except Exception as e:
                print(f"Can not fill the prompt input {e}")
                return False
            # Validate
            self.page.keyboard.press("Enter")
            return True
        except Exception as e:
            print(f"Error in find_and_fill_input {e}")
            return False

    def extract_response(self) -> Optional[str]:
        print("extracting response")
        content = None
        copy_selector = (
            'div.justify-start button[data-testid="copy-turn-action-button"]'
        )
        try:
            self.page.wait_for_selector(copy_selector, timeout=self.timeout)
        except Exception as e:
            print(f"Unable to find copy button {e}")
            return None

        content_selector = 'article[data-turn="assistant"]'
        content_element = self.page.query_selector(content_selector)
        content = content_element.inner_html() if content_element else ""
        content_markdown = convert_to_markdown(content)
        return content_markdown
