import sys

from patchright.sync_api import Browser


sys.path.append("..")

import time
import requests
import pyhtml2md
from playwright.sync_api import Page
from abc import ABC, abstractmethod
from contextlib import ContextDecorator
from src.utils.database import Database
from src.utils.aws_storage import AWSStorage
import os
from typing import Dict, Optional
from src.utils.globals import save_file
import random
from src.config.config import (
    PARSER_URL,
    PARSER_KEY,
    SG_PROXY_PASSWORD,
    SG_PROXY_USERNAME,
    US_PROXY_PASSWORD,
    US_PROXY_USERNAME,
    S3_BUCKET_NAME,
    HEADLESS,
    PARSE_OUTPUT,
)
import httpx
from camoufox.sync_api import Camoufox
from patchright.sync_api import sync_playwright
from xvfbwrapper import Xvfb

# Proxy lists
PROXIES = {
    "sg": ["isp.decodo.com"],
    "us": ["isp.decodo.com"],
}


class BrowserBase(ContextDecorator, ABC):
    def __init__(
        self,
        brand_report_id: str,
        prompt_id: str,
        logger,
        url: str,
        prompt: str,
        name: str,
        process_id: str,
        timeout: int,
        country: str,
        date: str,
        languague: str,
        brand: str,
    ) -> None:
        self.brand_report_id = brand_report_id
        self.prompt_id = prompt_id
        self.url = url
        self.prompt = prompt
        self.name = name
        self.process_id = process_id
        self.logger = logger
        self.timeout = timeout * 1000
        self.bucket = S3_BUCKET_NAME
        self.storage = AWSStorage(self.bucket)
        self.country = country
        self.date = date
        self.languague = languague
        self.brand = brand
        # initialise database
        self.database = Database()
        # initialise page
        self.page: Optional[Page] = None
        self.display = None

    def debug_snapshot(self, label: str) -> str:
        if not self.page:
            raise ValueError("Browser is not started")

        buffer = self.page.screenshot(full_page=True)

        cookies = {
            "PHPSESSID": "3s9dq38no2jfkoj7m1n47qi1q6",
        }

        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:153.0) Gecko/20100101 Firefox/153.0",
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.9",
            "Origin": "https://freeimage.host",
            "Connection": "keep-alive",
            "Referer": "https://freeimage.host/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Priority": "u=0",
        }

        files = {
            "source": (f"{label}.png", buffer, "image/png"),
            "type": (None, "file"),
            "action": (None, "upload"),
            "timestamp": (None, str(int(time.time() * 1000))),
            "auth_token": (None, "2b03c7fc68dd1e401e9d3d7b2df9581e90a61591"),
        }

        try:
            response = requests.post(
                "https://freeimage.host/json",
                cookies=cookies,
                headers=headers,
                files=files,
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()

            # Extract the direct image URL from the JSON response
            image_url = data["image"]["url"]
            self.logger.info(f"[DEBUG] {label}: {image_url}")
            return image_url

        except Exception as e:
            self.logger.error(
                f"[DEBUG] Failed to upload snapshot {label} to freeimage.host: {e}"
            )
            # Fallback to local save if upload fails
            path = f"/tmp/{label}.png"
            with open(path, "wb") as f:
                f.write(buffer)
            self.logger.info(f"[DEBUG] Saved locally instead: {path}")
            return path

    def get_proxy(self):
        """
        Get a random proxy from the specified country.
        """
        country = self.country.lower()

        if country not in PROXIES:
            raise ValueError(f"Country '{country}' not supported. Use 'sg' or 'us'")

        return random.choice(PROXIES[country])

    def navigate(self) -> bool:
        """Start the browser and navigate to the specified URL"""
        if not self.page:
            return False
        try:
            self.page.goto(self.url, timeout=self.timeout)
            self.logger.info(self.page.title)
            return True
        except Exception as e:
            self.logger.error(f"Error starting or navigating the page - {e}")
            return False

    def find_and_click(
        self, selector: str, error_message: str, timeout: int, click: bool = False
    ) -> bool:
        """Click ELement if visible, if not raise Error"""
        if not self.page:
            raise ValueError("Browser is not started")
        try:
            if click:
                self.page.click(selector, timeout=timeout, force=True)
            else:
                self.page.wait_for_selector(selector, timeout=timeout)
            return True
        except Exception as e:
            self.logger.error(error_message)
            raise ValueError(f"{error_message} {str(e)}")

    def extract_content(self, selector: str) -> dict:
        """Extract content from an element"""
        if not self.page:
            raise ValueError("Browser is not started")

        try:
            contents = self.page.query_selector_all(selector)
            content = contents[-1]
            if not content:
                return {"markdown": "", "html": ""}
            content_markdown = pyhtml2md.convert(content.inner_html())
            return {"markdown": content_markdown, "html": content.inner_html()}
        except Exception as e:
            self.logger.error("Unable to extract content")
            raise ValueError(f"Unable to extract content - {str(e)}")

    def extract_brand_info(self, s3_key: str):
        headers = {
            "accept": "application/json",
            "X-API-KEY": PARSER_KEY,
            "Content-Type": "application/x-www-form-urlencoded",
        }
        params = {
            "brand_report_id": self.brand_report_id,
            "prompt_id": self.prompt_id,
            "model": self.name,
            "brand": self.brand,
            "s3_key": s3_key,
            "languague": self.languague,
            "date": self.date,
        }
        response = httpx.post(
            f"{PARSER_URL}/api/report/prompts/parse",
            params=params,
            headers=headers,
        )
        response.raise_for_status()
        self.logger.info("- LLM Parser Started")

    def save_response(
        self, content: Optional[Dict[str, str] | str], selector: str | None = None
    ) -> bool:
        """Save the generated output from the prompt in html and text file"""
        if not self.page:
            return False

        if isinstance(content, str):
            return False

        basekey = f"{self.name}/{self.process_id}"
        save_folder = f"responses/{basekey}/"
        markdown_name = "output.txt"
        screenshot_name = "screenshot.png"
        html_name = "output.html"

        # video_name = "video.mp4"
        markdown_out = os.path.join(save_folder, markdown_name)
        screeshot_path = os.path.join(save_folder, screenshot_name)
        html_out = os.path.join(save_folder, html_name)
        # video_path = os.path.join(save_folder, video_name)

        # break the flow if no response in found
        if not content:
            self.logger.error("No generated output")
            return False

        # Save Text Result (Markdown and html)
        try:
            save_file(markdown_out, content["markdown"])
            save_file(html_out, content["html"])
            self.storage.save_file(f"{basekey}/{markdown_name}", markdown_out)
            self.storage.save_file(f"{basekey}/{html_name}", html_out)
        except Exception as e:
            self.logger.error(f"Unable to save output - {e}")
            return False

        # Start analyses
        if PARSE_OUTPUT == "yes":
            # send to parser api
            self.logger.info("- Parsing output with LLM")
            try:
                self.extract_brand_info(basekey)
            except Exception as e:
                self.logger.error(f"Unable to start the parser - {e}")

        # Save ScreenShot
        try:
            if selector:
                self.page.locator(selector).last.screenshot(path=screeshot_path)
            else:
                self.page.screenshot(path=screeshot_path, full_page=True)
            self.storage.save_file(f"{basekey}/{screenshot_name}", screeshot_path)
        except Exception as e:
            self.logger.error(f"Unable to save screenshot - {e}")

        self.logger.info(f" Successfully saved -- Output -> {save_folder}")
        return True

    @abstractmethod
    def find_and_fill_input(self) -> bool:
        """Platform-specific method to fill and submit the prompt."""
        pass

    @abstractmethod
    def extract_response(self) -> Optional[str]:
        """Platform-specific method to extract the response."""
        pass

    def save_raise_error(self, error_message: str) -> None:
        """Save, Log and raise Error"""
        self.debug_snapshot("on-failure")
        self.logger.error(error_message)
        # if save:
        #     self.database.update_process_status(self.process_id, "failed")
        raise ValueError(error_message)

    def process_prompt(self, selector: str | None) -> None:
        if not self.page:
            return None

        # Set 1: Navigate to the platform
        is_navigate = self.navigate()
        if not is_navigate:
            error_message = "Error starting or navigating the page"
            self.save_raise_error(error_message)
        self.logger.info("Successfully navigated to the page")

        # Step 2: Fill and Submit the input
        is_filled = self.find_and_fill_input()
        if not is_filled:
            error_message = "Error filling the prompt"
            self.save_raise_error(error_message)

        self.logger.info("Prompt successfully filled")
        time.sleep(5)

        # Step 3: Extract the generated response
        content = self.extract_response()
        if not content:
            error_message = "Error while extracting the response"
            self.save_raise_error(error_message)
        self.logger.info("Response successfully extracted")

        # Step 4: Save the response
        is_response_saved = self.save_response(content, selector)
        if not is_response_saved:
            error_message = "Error while saving response"
            self.save_raise_error(error_message)
        self.logger.info("Saving extracted data")

        # Step 5: Mark as Sucess
        # self.database.update_process_status(self.process_id, "success")
        self.logger.info("Process Successfully ended !")

    def setup_page(self, browser: Browser):
        self.page = browser.new_page()
        self.logger.info(f"Workflow Started - {self.name}")
        self.database.start_process(
            self.process_id,
            self.name,
            self.prompt,
            self.brand_report_id,
        )

        # Start processing the prompt
        selector = (
            'div[class="break-words min-w-0 flex-1"]'
            if self.name == "perplexity"
            else None
        )
        self.process_prompt(selector)
        self.page.close() if self.page else None

    def send_prompt(self) -> None:
        """Start the workflow"""
        if HEADLESS == "yes":
            headless = True
        else:
            headless = False  # "virtual"

        PROXY_PORT = f"1000{random.randint(1, 7)}"
        if self.country == "sg":
            proxy = {
                "server": f"{self.get_proxy()}:{PROXY_PORT}",
                "username": SG_PROXY_USERNAME,
                "password": SG_PROXY_PASSWORD,
            }
        elif self.country == "us":
            proxy = {
                "server": f"{self.get_proxy()}:{PROXY_PORT}",
                "username": US_PROXY_USERNAME,
                "password": US_PROXY_PASSWORD,
            }

        # 1. Group shared options to keep code DRY and maintainable
        common_options = {
            "window": (1920, 1080),
            "slow_mo": 1000,
            "locale": f"en-{self.country.upper()}",
            "headless": headless,
            "proxy": proxy,
            "geoip": True,
            "humanize": False,
        }

        # 2. Add case-specific overrides
        match self.name:
            case "google":
                with Xvfb():
                    with sync_playwright() as p:
                        try:
                            browser = p.chromium.launch(
                                # user_data_dir="...",
                                # channel="chrome",
                                proxy=proxy,
                                headless=False,
                                # no_viewport=True,
                            )
                            self.setup_page(browser)
                        except Exception as e:
                            self.save_raise_error(f"Processing Error - {str(e)}")
            case _:
                camoufox_options = Camoufox(**common_options)
                # 3. Execution block
                with camoufox_options as browser:
                    try:
                        self.setup_page(browser)
                    except Exception as e:
                        self.save_raise_error(f"Processing Error - {str(e)}")
