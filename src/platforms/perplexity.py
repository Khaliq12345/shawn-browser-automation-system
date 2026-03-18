import sys


sys.path.append(".")

import time
from typing import Optional
from src.platforms.browser import BrowserBase
import requests


class PerplexityScraper(BrowserBase):
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
        self.logger.info("Filling the prompt")

        if not self.page:
            return False

        time.sleep(5)
        prompt_input_selector = 'div[id="ask-input"]'
        # trying to fill the prompt
        self.find_and_click(
            prompt_input_selector, "Can not fill the prompt input", timeout=5 * 1000
        )
        self.page.fill(prompt_input_selector, value=self.prompt)

        # Validate
        self.page.keyboard.press("Enter")
        # submit_button = 'button[data-testid="submit-button"]'
        # self.find_and_click(submit_button, "Submit button is not available ", timeout=self.timeout, click=True)

        return True

    def debug_snapshot(self, label: str) -> str:
        if not self.page:
            raise ValueError("Browser is not started")
        buffer = self.page.screenshot(full_page=True)
        response = requests.post(
            "https://litterbox.catbox.moe/resources/internals/api.php",
            data={"reqtype": "fileupload", "time": "24h"},
            files={"fileToUpload": (f"{label}.png", buffer, "image/png")},
        )
        url = response.text.strip()
        self.logger.info(f"[DEBUG] {label}: {url}")
        return url

    def get_markdown_content(self) -> str:
        if not self.page:
            raise ValueError("Browser is not started")
        try:
            download_button = "div.-ml-sm:nth-child(1) > button:nth-child(2)"
            markdown_option = "text=Markdown"

            # wait for the button to actually be visible instead of blind sleep
            self.page.wait_for_selector(download_button, state="visible", timeout=15000)
            self.debug_snapshot("01-before-click")

            self.page.locator(download_button).first.click()

            # wait for the dropdown to appear
            self.page.wait_for_selector(markdown_option, state="visible", timeout=10000)
            self.debug_snapshot("02-dropdown-open")

            with self.page.expect_download(timeout=15000) as download_info:
                self.page.locator(markdown_option).click()

            self.debug_snapshot("03-after-download")

            download = download_info.value
            path = download.path()
            with open(path, "r", encoding="utf-8") as f:
                markdown = f.read()
            return markdown

        except Exception as e:
            self.debug_snapshot("on-failure")  # <-- this is the money shot
            self.logger.error("Unable to download markdown")
            raise ValueError(f"Unable to download markdown - {str(e)}")

    def extract_response(self) -> Optional[str]:
        self.logger.info("Extracting response")
        if not self.page:
            return None

        content = None
        share_selector = 'button[aria-label="Share"]'
        self.find_and_click(
            share_selector, "Unable to find share button", timeout=20 * 1000
        )
        self.logger.info(
            f"SHARE BUTTON - {self.page.locator(share_selector).first.inner_html()}"
        )
        # Get content
        # content_selector = 'div[id="markdown-content-0"]'
        # self.find_and_click(
        #     content_selector, "Unable to find content", timeout=5 * 1000
        # )
        # content = self.extract_content(content_selector)
        # self.page.pause()
        content = self.get_markdown_content()
        return content
