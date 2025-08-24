import sys

import pyperclip

sys.path.append("..")

from typing import Optional
from src.platforms.browser import BrowserBase


class PerplexityScraper(BrowserBase):
    def __init__(
        self, url: str, prompt: str, name: str, process_id: str, headless: bool = True
    ) -> None:
        super().__init__(url, prompt, name, process_id, headless)

    async def find_and_fill_input(self) -> bool:
        try:
            prompt_input_selector = 'div[id="ask-input"]'
            # trying to fill the prompt
            try:
                await self.page.fill(
                    prompt_input_selector, self.prompt, timeout=self.timeout
                )
            except Exception as e:
                print(f"Can not fill the prompt input {e}")
                return False
            # Validate
            try:
                submit_button = 'button[aria-label="Submit"]'
                await self.page.click(submit_button, timeout=self.timeout)
            except Exception as e:
                print(f"Submit button is not available - {e}")
                return False
            return True
        except Exception as e:
            print(f"Error in find_and_fill_input {e}")
            return False

    async def extract_response(self) -> Optional[str]:
        content = None
        copy_selector = 'button[aria-label="Copy"]'
        try:
            await self.page.wait_for_selector(copy_selector, timeout=120000)
            await self.page.click(copy_selector)
            print("Copied")
        except Exception as e:
            print(f"Unable to find copy button - {e}")
            return None
        content = pyperclip.paste()
        return content
