import sys
import pyperclip

sys.path.append("..")

from typing import Optional
from src.platforms.browser import BrowserBase


class ChatGPTScraper(BrowserBase):
    def __init__(
        self,
        browser,
        logger,
        url: str,
        prompt: str,
        name: str,
        process_id: str,
        headless: bool = False,
    ) -> None:
        super().__init__(browser, logger, url, prompt, name, process_id, headless)

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
            self.page.locator(copy_selector).last.click(timeout=120000, force=True)
        except Exception as e:
            print(f"Unable to find copy button {e}")
            return None
        content = pyperclip.paste()
        return content
