import sys

sys.path.append("..")

from typing import Optional
from src.platforms.browser import BrowserBase


class GoogleScraper(BrowserBase):
    def __init__(
        self, url: str, prompt: str, name: str, process_id: str, headless: bool = False
    ) -> None:
        super().__init__(url, prompt, name, process_id, headless)
        self.timeout = 120000

    async def find_and_fill_input(self) -> bool:
        try:
            prompt_input_selector = 'textarea[name="q"]'
            # trying to fill the prompt
            try:
                await self.page.fill(
                    prompt_input_selector, self.prompt, timeout=self.timeout
                )
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
        content_selector = 'div[id="m-x-content"]'
        show_more_button = 'div[class="kHtcsd"]'

        try:
            await self.page.click(show_more_button, timeout=self.timeout)
            await self.page.wait_for_timeout(timeout=3000)
        except Exception as e:
            print(f"Unable to find the Show more button {e}")
            return None

        try:
            await self.page.wait_for_selector(content_selector, timeout=self.timeout)
        except Exception as e:
            print(f"Unable to find the content {e}")
            return None

        content_element = await self.page.query_selector(content_selector)
        content = await content_element.inner_html() if content_element else ""
        return content
