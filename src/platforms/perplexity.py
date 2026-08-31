import sys


sys.path.append(".")

from src.platforms.browser import BrowserBase
import pyperclip


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

    def wait_for_answer_complete(self, selector, timeout=60000, stable_for=2000):
        if not self.page:
            return False
        locator = self.page.locator(selector).last

        start_time = self.page.evaluate("Date.now()")
        last_text = ""
        last_change = self.page.evaluate("Date.now()")

        while self.page.evaluate("Date.now()") - start_time < timeout:
            try:
                current_text = locator.inner_text().strip()

                if current_text != last_text:
                    last_text = current_text
                    last_change = self.page.evaluate("Date.now()")
                # Answer has not changed for 2 seconds
                if (
                    current_text
                    and self.page.evaluate("Date.now()") - last_change >= stable_for
                ):
                    return current_text
            except Exception:
                pass
            self.page.wait_for_timeout(500)
        return last_text

    def remove_modal(self):
        if not self.page:
            return False
        self.logger.info("Removing modal")
        selector = 'div[data-type="portal"]'
        try:
            self.page.wait_for_selector(
                selector,
                state="attached",
                timeout=3000,
            )
            self.logger.info("Portal found")
            self.page.evaluate(
                """
                selector => {
                    document.querySelectorAll(selector).forEach(el => el.remove());
                }
                """,
                selector,
            )
            self.logger.info("Portal removed")

        except Exception:
            self.logger.info("Portal not found within 3 seconds")

    def get_valid_answer(self):
        if not self.page:
            return False
        prompt_input_selector = 'div[id="ask-input"]'
        LOADING_SELECTOR = 'svg[class="animate-pplxIndicator fill-mode-both h-full w-auto shrink-0 transform-gpu will-change-transform"]'
        for idx in range(1, 11):
            self.page.type(prompt_input_selector, text=self.prompt)
            self.page.wait_for_timeout(3000)
            self.page.keyboard.press("Enter")
            self.remove_modal()
            try:
                loading = self.page.locator(LOADING_SELECTOR)
                # Only wait briefly for loading to appear
                loading.wait_for(state="visible", timeout=3000)
                # If it appeared, wait for it to disappear
                loading.wait_for(state="hidden", timeout=60000)
            except Exception:
                self.logger.info("Loading indicator did not appear or is already gone")
            self.remove_modal()
            self.wait_for_answer_complete(
                "div.break-words.min-w-0.flex-1",
            )
            # Get the latest answer
            copy_button = self.page.locator('button[aria-label="Copy"]').last
            copy_button.click()
            copied_text = pyperclip.paste()
            # If we got a valid answer, stop the loop
            if "Sign up and repeat your request" not in copied_text:
                self.logger.info("Valid answer received. Stopping.")
                return copied_text

            self.logger.info(f"Attempt {idx} failed, retrying...")

    def find_and_fill_input(self, use_botasarus: bool = False) -> bool:
        self.logger.info("Filling the prompt")

        if not self.page:
            return False

        self.page.wait_for_timeout(2000)
        prompt_input_selector = 'div[id="ask-input"]'
        # trying to fill the prompt
        self.find_and_click(
            prompt_input_selector, "Can not fill the prompt input", timeout=30 * 1000
        )

        self.page.type(prompt_input_selector, text=self.prompt)
        self.page.wait_for_timeout(2000)
        self.page.keyboard.press("Enter")
        self.page.wait_for_timeout(2000)
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
            self.remove_modal()
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
        # content = self.get_markdown_content()
        content = self.get_valid_answer()
        return {"markdown": content or "", "html": ""}
