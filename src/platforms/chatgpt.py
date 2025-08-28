import sys
from playwright.async_api import expect
import pyperclip

sys.path.append("..")

from typing import Optional
from src.platforms.browser import BrowserBase


class ChatGPTScraper(BrowserBase):
    def __init__(
        self,
        browser,
        url: str,
        prompt: str,
        name: str,
        process_id: str,
        headless: bool = False,
    ) -> None:
        super().__init__(browser, url, prompt, name, process_id, headless)

    async def find_and_fill_input(self) -> bool:
        try:
            await self.page.wait_for_timeout(5000)
            await self.page.mouse.click(0, 0)
            await self.page.wait_for_timeout(5000)
            # trying to fill the prompt
            prompt_input_selector = 'div[id="prompt-textarea"]'  # "#prompt-textarea"
            try:
                print("Filling input")
                await self.page.fill(
                    prompt_input_selector, self.prompt, timeout=self.timeout
                )
                print("Done FIlling")
            except Exception as e:
                print(f"Can not fill the prompt input {e}")
                return False
            # Validate
            await self.page.keyboard.press("Enter")
            return True
        except Exception as e:
            print(f"Error in find_and_fill_input {e}")
            return False

    async def extract_response(self) -> Optional[str]:
        print("extracting response")
        content = None
        copy_selector = (
            'div.justify-start button[data-testid="copy-turn-action-button"]'
        )
        try:
            await self.page.locator(copy_selector).last.click(
                timeout=120000, force=True
            )
        except Exception as e:
            print(f"Unable to find copy button {e}")
            return None
        content = pyperclip.paste()
        return content
