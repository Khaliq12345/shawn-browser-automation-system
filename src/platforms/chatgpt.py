import sys

sys.path.append("..")

from typing import Optional
from playwright.sync_api import ElementHandle
from src.platforms.browser import BrowserBase


class ChatGPTScraper(BrowserBase):
    def __init__(
        self, url: str, prompt: str, name: str, headless: bool = False
    ) -> None:
        super().__init__(url, prompt, name, headless)

    def find_and_fill_input(self) -> bool:
        try:
            # Looking For the close button of modal
            close_btn_selector = 'button[data-testid="close-button"]'
            try:
                self.page.wait_for_selector(close_btn_selector, timeout=self.timeout)
            except Exception as e:
                print(f"Unable Modal Close Btn {e}")
                return False
            self.page.click(close_btn_selector, timeout=self.timeout)
            # trying to fill the prompt
            prompt_input_selector = "#prompt-textarea"
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
        content_selector = "div.markdown.prose"
        copy_selector = 'button[aria-label="Edit in canvas"]'  # 'button[data-testid="copy-turn-action-button"]'
        # Looking for the edit button (it appears once the response is generated)
        try:
            self.page.wait_for_selector(copy_selector, timeout=self.timeout)
        except Exception as e:
            print(f"Unable to find edit button {e}")
            return None
        self.page.wait_for_timeout(5000)
        # Looking for the response selector
        try:
            self.page.wait_for_selector(content_selector, timeout=self.timeout)
        except Exception as e:
            print(f"Unable to find the content {e}")
            return None
        content = self.page.query_selector(content_selector)
        return content


if __name__ == "__main__":
    prompt = "Explique-moi la théorie de la relativité en termes simples."

    with ChatGPTScraper(
        url="https://chatgpt.com/", prompt=prompt, name="chatgpt"
    ) as browser:
        browser.send_prompt()
