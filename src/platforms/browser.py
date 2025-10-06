import sys

sys.path.append("..")


from abc import ABC, abstractmethod
from contextlib import ContextDecorator
from src.utils.database import Database
from src.utils.aws_storage import AWSStorage

import os
from typing import Optional
from src.utils.globals import save_file
from src.config.config import (
    HEADLESS,
    PROXY_USERNAME,
    PROXY_PASSWORD,
    PARSER_URL,
    PARSER_KEY,
)
from patchright.sync_api import sync_playwright
from camoufox import Camoufox
from browserforge.fingerprints import Screen
from user_agent import generate_user_agent
import httpx

# PROXY configs
PROXIES = {
    "us": "10000",
    "sg": "10000",
    "ca": "20000",
    "gb": "30000",
    "au": "30000",
    "nz": "39000",
}


class BrowserBase(ContextDecorator, ABC):
    def __init__(
        self,
        brand_report_id: str,
        logger,
        url: str,
        prompt: str,
        name: str,
        process_id: str,
        timeout: int,
        country: str,
        headless: bool = False,
    ) -> None:
        self.brand_report_id = brand_report_id
        self.url = url
        self.prompt = prompt
        self.name = name
        self.process_id = process_id
        self.headless = headless
        self.logger = logger
        self.timeout = timeout
        self.bucket = "browser-outputs"
        self.storage = AWSStorage(self.bucket)
        self.country = country

        # initialise database
        self.database = Database()

    def navigate(self) -> bool:
        """Start the browser and navigate to the specified URL"""
        try:
            self.page.goto(self.url, timeout=self.timeout)
            return True
        except Exception as e:
            print(f"Error starting or navigating the page - {e}")
            return False

    def aws_upload_file(self, key: str, path: str) -> None:
        self.storage.save_file(key, path)

    def extract_brand_info(self, s3_key: str):
        headers = {
            "accept": "application/json",
            "X-API-KEY": PARSER_KEY,
        }
        params = {
            "prompt_id": self.process_id,
            "s3_key": s3_key,
        }
        response = httpx.get(
            f"{PARSER_URL}/api/llm/extract-brand-info",
            params=params,
            headers=headers,
        )
        response.raise_for_status()
        self.logger.info("- LLM Parser Started")

    def save_response(self, content: Optional[str]) -> bool:
        """Save the generated output from the prompt in html and text file"""

        basekey = f"{self.name}/{self.process_id}"
        save_folder = f"responses/{basekey}/"
        text_name = "output.txt"
        screenshot_name = "screenshot.png"
        video_name = "video.mp4"
        txt_out = os.path.join(save_folder, text_name)
        screeshot_path = os.path.join(save_folder, screenshot_name)
        video_path = os.path.join(save_folder, video_name)

        # break the flow if no response in found
        if not content:
            self.logger.error("No generated output")
            print("No generated output")
            return False

        # Save Text Result
        try:
            save_file(txt_out, content)
            self.aws_upload_file(f"{basekey}/{text_name}", txt_out)
            # send to parser api
            self.logger.info("- Parsing output with LLM")
            self.extract_brand_info(f"{basekey}/{text_name}")
        except Exception as e:
            self.logger.error(f"Unable to save output - {e}")
            return False

        # Save ScreenShot
        try:
            self.page.screenshot(path=screeshot_path, full_page=True)
            self.aws_upload_file(f"{basekey}/{screenshot_name}", screeshot_path)
        except Exception as e:
            self.logger.error(f"Unable to save screenshot - {e}")

        # Save Video
        try:
            video = self.page.video
            if video:
                self.logger.info("Successfully recorded video")
                self.page.close()
                video.save_as(video_path)
                self.aws_upload_file(f"{basekey}/{video_name}", video_path)
            else:
                self.logger.error("No video was recorded")

        except Exception as e:
            self.logger.error(f"Unable to record video - {e}")

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

    def process_prompt(self) -> None:
        # Set 1: Navigate to the platform
        is_navigate = self.navigate()
        if not is_navigate:
            self.logger.error("- Error starting or navigating the page")
            self.database.update_process_status(self.process_id, "failed")
            return None
        self.logger.info("- Successfully navigated to the page")

        # Step 2: Fill and Submit the input
        is_filled = self.find_and_fill_input()
        if not is_filled:
            self.logger.error("- Error filling the prompt")
            self.database.update_process_status(self.process_id, "failed")
            return None
        self.logger.info("- Prompt successfully filled")
        self.page.wait_for_timeout(5000)

        # Step 3: Extract the generated response
        content = self.extract_response()
        if not content:
            self.logger.error("- Error while extracting the response")
            self.database.update_process_status(self.process_id, "failed")
            return None
        self.logger.info("- Response successfully extracted")

        # Step 4: Save the response
        self.save_response(content)
        self.logger.info("- Saving extracted data")

        # Step 5: Mark as Sucess on supabase
        self.database.update_process_status(self.process_id, "success")
        self.logger.info("- Process Successfully ended !")

    def send_prompt(self) -> None:
        """Start the workflow"""
        self.logger.info("- Workflow Started")
        self.database.start_process(
            self.process_id, self.name, self.prompt, self.brand_report_id
        )
        self.database.update_process_status(self.process_id, "failed")

        # context = None
        # with Camoufox(
        #     geoip=True,
        #     headless=HEADLESS != "false",
        #     proxy={
        #         "server": f"http://{self.country}.decodo.com:{PROXIES[self.country]}",
        #         "username": PROXY_USERNAME,
        #         "password": PROXY_PASSWORD,
        #     },
        # ) as browser:
        #     try:
        #         ua = generate_user_agent()
        #         context = browser.new_context(
        #             record_video_dir=f"responses/{self.name}/{self.uid}/",
        #             record_video_size={"width": 1280, "height": 720},
        #             user_agent=ua,
        #             viewport={"width": 1280, "height": 720},
        #         )
        #         self.page = context.new_page()
        #         self.process_prompt()
        #     except Exception as e:
        #         self.logger.error(f"- Error while processing prompt - {e}")
        #         self.database.update_process_status(self.process_id, "failed")
        #     finally:
        #         self.page.close()
        #         context.close() if context else None
        #         print("Context and Page instance closed")
