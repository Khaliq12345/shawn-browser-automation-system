import sys


sys.path.append(".")

from src.platforms.browser import BrowserBase


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

        self.page.wait_for_timeout(2000)
        prompt_input_selector = 'div[id="ask-input"]'
        # trying to fill the prompt
        self.find_and_click(
            prompt_input_selector, "Can not fill the prompt input", timeout=5 * 1000
        )

        self.page.type(prompt_input_selector, text=self.prompt)
        self.page.wait_for_timeout(2000)
        self.page.keyboard.press("Enter")
        self.page.wait_for_timeout(2000)
        # submit_button = 'button[data-testid="submit-button"]'
        # self.find_and_click(submit_button, "Submit button is not available ", timeout=self.timeout, click=True)
        return True

    def get_markdown_content(self) -> str:
        if not self.page:
            raise ValueError("Browser is not started")
        try:
            # wait for the button to actually be visible instead of blind sleep
            self.page.wait_for_timeout(2000)
            self.debug_snapshot("on-before-download-click")
            self.page.get_by_role("button", name="Download").nth(-1).click(
                timeout=20 * 1000
            )
            with self.page.expect_download(timeout=15000) as download_info:
                self.page.get_by_role("menuitem", name="Markdown").click()

            self.debug_snapshot("on-after-download")
            download = download_info.value
            path = download.path()
            with open(path, "r", encoding="utf-8") as f:
                markdown = f.read()

            self.page.reload(timeout=20 * 1000, wait_until="load")
            self.logger.info("Deleting the session")
            self.page.get_by_label("Main", exact=True).get_by_role(
                "button", name="Session actions"
            ).click()

            self.page.get_by_text("Delete").click(timeout=20 * 1000)
            self.page.get_by_role("button", name="Delete").click(timeout=20 * 1000)
            return markdown

        except Exception as e:
            self.debug_snapshot("on-failure")  # <-- this is the money shot
            self.logger.error("Unable to download markdown")
            raise ValueError(f"Unable to download markdown - {str(e)}")

    def extract_response(self) -> dict | None:
        self.logger.info("Extracting response")
        if not self.page:
            return None

        content = None
        try:
            self.find_and_click(
                "main", "Unable to click on main", 20 * 1000, click=True
            )
        except Exception as _:
            self.debug_snapshot("on-failure")  # <-- this is the money shot
        self.page.keyboard.press("End")
        # share_selector = 'div[class="-ml-sm gap-xs flex flex-shrink-0 items-center"] button:nth-child(2)'
        # self.find_and_click(
        #     share_selector, "Unable to find share button", timeout=20 * 1000
        # )
        # Get content
        # content_selector = 'div[id="markdown-content-0"]'
        # self.find_and_click(
        #     content_selector, "Unable to find content", timeout=5 * 1000
        # )
        # content = self.extract_content(content_selector)
        # self.page.pause()
        content = self.get_markdown_content()
        return {"markdown": content, "html": ""}
