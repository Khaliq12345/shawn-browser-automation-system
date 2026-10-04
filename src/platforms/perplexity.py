import sys


sys.path.append(".")

from src.platforms.browser import BrowserBase
import pyperclip
from src.utils.email_service import EmailService
from src.config.config import EMAIL_ACCOUNT, EMAIL_PASSWORD, IMAP_SERVER


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

    def get_otp_code(self) -> str:
        # Initialize the service with your config
        email_service = EmailService(
            IMAP_SERVER=IMAP_SERVER,
            EMAIL_ACCOUNT=EMAIL_ACCOUNT,
            EMAIL_PASSWORD=EMAIL_PASSWORD,
        )

        # Fetch the OTP
        otp = email_service.fetch_latest_otp(
            timeout=60,
            poll_interval=5,
            sender_email="team@mail.perplexity.ai",  # Set to None if not needed
            subject_keyword="Sign in to Perplexity",
        )
        if otp:
            print(f"\n[SUCCESS] Extracted OTP Code: **{otp}**")
            return otp
        else:
            print("\n[FAILED] Could not retrieve OTP.")
            raise RuntimeError("[FAILED] Could not retrieve OTP.")

    def _wait_for_captcha(self, timeout_seconds: int = 60) -> bool:
        """Wait for Cloudflare security verification to clear with a timeout"""
        if not self.page:
            return False
        self.logger.info("Checking for security verification...")
        interval = 5000  # 5 seconds
        max_attempts = timeout_seconds // (interval // 1000)
        attempts = 0

        try:
            while self.page.get_by_text(
                "Performing security verification"
            ).is_visible():
                if attempts >= max_attempts:
                    self.logger.error("Cloudflare security verification timed out.")
                    return False

                self.logger.info("Waiting for security verification to complete...")
                self.page.wait_for_timeout(interval)
                attempts += 1
            return True
        except Exception:
            # If the element detaches or page reloads while checking, it's usually safe to proceed
            return True

    def navigate(self) -> bool:
        """Start the browser and navigate to the specified URL"""
        if not self.page:
            return False
        try:
            self.page.goto(self.url, timeout=self.timeout)
            self.logger.info(self.page.title)

            # Wait for Cloudflare security verification to clear if present
            if not self._wait_for_captcha():
                return False

            self.logger.info("Checking if we are logged in..")
            self.page.wait_for_load_state(state="load", timeout=self.timeout)
            sign_in_button = self.page.get_by_role("button", name="Sign In")
            if sign_in_button.is_visible():
                self.logger.info("We are not logged in..")
                sign_in_button.click()
                self.page.get_by_role("textbox", name="Enter your email").fill(
                    EMAIL_ACCOUNT, timeout=self.timeout
                )
                self.page.get_by_role("button", name="Continue with email").click()
                otp_code = self.get_otp_code()
                self.page.get_by_role("textbox", name="Digit 1 of").fill(otp_code[0])
                self.page.get_by_role("textbox", name="Digit 2 of").fill(otp_code[1])
                self.page.get_by_role("textbox", name="Digit 3 of").fill(otp_code[2])
                self.page.get_by_role("textbox", name="Digit 4 of").fill(otp_code[3])
                self.page.get_by_role("textbox", name="Digit 5 of").fill(otp_code[4])
                self.page.get_by_role("textbox", name="Digit 6 of").fill(otp_code[5])
                self.page.wait_for_load_state(state="load", timeout=self.timeout)
            else:
                self.logger.info("We are logged in..")
            self.page.click('button[aria-label^="Use incognito"]')
            return True
        except Exception as e:
            self.logger.error(f"Error starting or navigating the page - {e}")
            return False

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

    def find_and_fill_input(self) -> bool:
        if not self.page:
            return False
        prompt_input_selector = 'div[id="ask-input"]'
        NEW_LOADING_SELECTOR = (
            'div[class="_sharedDuration_orhia_1 _defaultShimmer_orhia_9 min-w-0"]'
        )
        self.page.type(prompt_input_selector, text=self.prompt)
        self.page.wait_for_timeout(3000)
        self.page.keyboard.press("Enter")
        self.remove_modal()
        try:
            loading = self.page.locator(NEW_LOADING_SELECTOR).last
            # Only wait briefly for loading to appear
            loading.wait_for(state="visible", timeout=3000)
            # If it appeared, wait for it to disappear
            loading.wait_for(state="hidden", timeout=60000)
            self.logger.info("LOCATOR IS HIDDEN!!")
        except Exception:
            self.logger.info("Loading indicator did not appear or is already gone")
        return True

    def extract_response(self) -> dict | None:
        self.logger.info("Extracting response")
        if not self.page:
            return None
        content = None
        try:
            self.remove_modal()
            self.find_and_click(
                "main", "Unable to click on main", 60 * 1000, click=True
            )
        except Exception as _:
            self.debug_snapshot("on-failure")
        self.page.keyboard.press("End")
        # Get the latest answer
        copy_button = self.page.locator('button[aria-label="Copy"]').last
        copy_button.click()
        content = self.page.evaluate("navigator.clipboard.readText()")
        # content = pyperclip.paste()
        self.logger.info(f"COPIED TEXT {content[:20]}")
        if not content:
            raise RuntimeError("Perplexity Failed: Hit rate-limit / sign-up wall")
        return {"markdown": content or "", "html": ""}
