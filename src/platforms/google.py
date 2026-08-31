import sys
import time
import requests


sys.path.append(".")

from typing import Dict, Optional
from src.platforms.browser import BrowserBase
from src.config.config import CAPTCHA_API_KEY


class GoogleScraper(BrowserBase):
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

    def submit_captcha_task(self, site_url, site_key, data_s):
        """Submit CAPTCHA task to 2Captcha API v2 and return task ID"""
        url = "https://api.2captcha.com/createTask"

        payload = {
            "clientKey": CAPTCHA_API_KEY,
            "task": {
                "type": "RecaptchaV2TaskProxyless ",
                "websiteURL": site_url,
                "websiteKey": site_key,
                "isInvisible": False,
                "recaptchaDataSValue": data_s,
            },
        }

        try:
            response = requests.post(url, json=payload)
            data = response.json()

            if data.get("errorId") == 0:
                task_id = data.get("taskId")
                print(f"✓ CAPTCHA task submitted. Task ID: {task_id}")
                return task_id
            else:
                raise Exception(
                    f"Error submitting task: {data.get('errorDescription')}"
                )
        except Exception as e:
            raise Exception(f"Failed to submit CAPTCHA task: {str(e)}")

    def get_captcha_token(self, task_id, max_attempts=24, delay=5):
        """Poll 2Captcha API v2 for CAPTCHA solution and return token"""
        url = "https://api.2captcha.com/getTaskResult"

        payload = {"clientKey": CAPTCHA_API_KEY, "taskId": task_id}

        print(f"⏳ Waiting for CAPTCHA solution (checking every {delay}s)...")

        for attempt in range(1, max_attempts + 1):
            time.sleep(delay)

            try:
                response = requests.post(url, json=payload)
                data = response.json()

                status = data.get("status")

                if status == "ready":
                    token = data.get("solution", {}).get("gRecaptchaResponse")
                    print("✓ CAPTCHA solved successfully!")
                    return token
                elif status == "processing":
                    print(f"  Attempt {attempt}/{max_attempts}: Still processing...")
                    continue
                else:
                    raise Exception(f"Unexpected status: {data}")

            except Exception as e:
                print(f"  Attempt {attempt}/{max_attempts}: Error - {str(e)}")
                if attempt == max_attempts:
                    raise

        raise Exception("Timeout: CAPTCHA solution not ready after multiple attempts")

    def solve_captcha(self, site_url, site_key, data_s):
        """
        Main function to solve CAPTCHA.

        Args:
            site_url: The URL of the page with the CAPTCHA
            site_key: The reCAPTCHA sitekey

        Returns:
            The CAPTCHA token (gRecaptchaResponse)
        """
        print("\n🔄 Starting CAPTCHA solver...")
        print(f"   URL: {site_url}")
        print(f"   Sitekey: {site_key}")

        # Submit the task
        task_id = self.submit_captcha_task(site_url, site_key, data_s)

        # Get the solution
        token = self.get_captcha_token(task_id)

        return token

    def inject_captcha_token(self, token):
        """Inject the CAPTCHA token into the page"""
        if not self.page:
            return None
        print("\n💉 Injecting CAPTCHA token...")

        # Method 1: Set the textarea value
        self.page.evaluate(
            """
            (token) => {
                const textarea = document.querySelector('[name="g-recaptcha-response"]');
                if (textarea) {
                    textarea.value = token;
                    textarea.innerHTML = token;
                }
            }
        """,
            token,
        )
        print("✓ Token injected successfully!")
        return token

    def check_and_solve_captcha(self):
        # Check if CAPTCHA is present
        if not self.page:
            return None
        captcha_present = (
            self.page.query_selector("div.g-recaptcha") is not None
            or self.page.query_selector('iframe[src*="recaptcha"]') is not None
        )

        if captcha_present:
            print("\n🤖 CAPTCHA detected on page!")

            # Solve the CAPTCHA
            site_key_node = self.page.query_selector('div[class="g-recaptcha"]')
            if not site_key_node:
                pass
            else:
                site_key = site_key_node.get_attribute("data-sitekey")
                data_s = site_key_node.get_attribute("data-s")
                print(f"\nSITEKEY - {site_key}")
                token = self.solve_captcha(self.page.url, site_key, data_s)

                # Inject the token
                self.inject_captcha_token(token)

                # Wait a bit for the page to process
                time.sleep(2)
                return True
        else:
            print("\n✓ No CAPTCHA detected on this page")

    def navigate(self) -> bool:
        """Override navigate to use Google search URL with prompt"""
        self.logger.info("Loading the page")
        if not self.page:
            return False
        try:
            # Use Google search URL format with prompt
            search_url = "https://www.google.com"
            self.page.goto(search_url, timeout=self.timeout)
            self.page.get_by_role("combobox", name="Search").click()
            self.page.get_by_role("combobox", name="Search").fill(self.prompt)
            self.page.keyboard.press("Enter")
            self.page.wait_for_load_state(timeout=50000, state="load")
            captcha_solved = self.check_and_solve_captcha()
            if captcha_solved:
                self.page.goto("https://www.google.com", timeout=50000)
                self.page.fill(selector='textarea[title="Search"]', value=self.prompt)
                self.page.keyboard.press("Enter")
                self.page.wait_for_load_state(timeout=self.timeout)

                self.logger.info(self.page.title)
            return True
        except Exception as e:
            self.logger.error(f"Error starting or navigating the page - {e}")
            return False

    def find_and_fill_input(self) -> bool:
        self.logger.info("Filling input")
        return True

    def extract_response(self) -> Optional[Dict[str, str] | str]:
        self.logger.info("Extracting response")
        if not self.page:
            return None
        content_selector = 'div[jsname="KFl8ub"]'
        # see_more_selector = 'div[aria-controls="m-x-content"]'

        # see_more_selector = 'button[id="llm-show-more-button"]'
        # content_selector = 'div[id="llm-snippet"]'

        # click on see more (ai answer)
        # try:
        #     self.find_and_click(
        #         see_more_selector,
        #         "Ai overview not visible",
        #         timeout=5 * 1000,
        #         click=True,
        #     )
        # except Exception as _:
        #     return "Ai overview not visible"

        # wait for content to be visible
        try:
            self.find_and_click(
                content_selector,
                timeout=20 * 1000,
                error_message="Unable to find the content",
                click=True,
            )
        except Exception as e:
            self.logger.error(f"Unable to find the content - {e}")

        content = self.extract_content(content_selector)
        return content
