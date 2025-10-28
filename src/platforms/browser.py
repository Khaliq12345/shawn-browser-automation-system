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
    S3_BUCKET_NAME,
)
import httpx
from botasaurus_driver import Driver

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
        self.timeout = timeout
        self.bucket = S3_BUCKET_NAME
        self.storage = AWSStorage(self.bucket)
        self.country = country
        self.date = date
        self.languague = languague
        self.brand = brand
        # initialise database
        self.database = Database()
        # initialise page
        self.page: Optional[Driver] = None

    def navigate(self) -> bool:
        """Start the browser and navigate to the specified URL"""
        print("Loading the page")
        if not self.page:
            return False
        try:
            self.page.google_get(self.url, timeout=self.timeout, bypass_cloudflare=True)
            return True
        except Exception as e:
            print(f"Error starting or navigating the page - {e}")
            return False

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

    def save_response(self, content: Optional[str]) -> bool:
        """Save the generated output from the prompt in html and text file"""
        if not self.page:
            return False

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
            self.storage.save_file(f"{basekey}/{text_name}", txt_out)
            # send to parser api
            self.logger.info("- Parsing output with LLM")
        except Exception as e:
            self.logger.error(f"Unable to save output - {e}")
            return False

        try:
            self.extract_brand_info(basekey)
        except Exception as e:
            self.logger.error(f"Unable to start the parser - {e}")

        # Save ScreenShot
        try:
            self.page.save_screenshot(filename=screeshot_path)
            self.storage.save_file(f"{basekey}/{screenshot_name}", screeshot_path)
        except Exception as e:
            self.logger.error(f"Unable to save screenshot - {e}")

        # # Save Video
        # try:
        #     video = self.page.video
        #     if video:
        #         self.logger.info("Successfully recorded video")
        #         self.page.close()
        #         video.save_as(video_path)
        #         self.storage.save_file(f"{basekey}/{video_name}", video_path)
        #     else:
        #         self.logger.error("No video was recorded")
        #
        # except Exception as e:
        #     self.logger.error(f"Unable to record video - {e}")

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
        if not self.page:
            return None

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
        self.page.sleep(5)

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

        # setup the proxy
        proxy = f"http://{PROXY_USERNAME}:{PROXY_PASSWORD}@{self.country}.decodo.com:{PROXIES.get(self.country)}"

        # initialise page
        headless = HEADLESS != "false"
        self.page = Driver(
            headless=headless,
            proxy=proxy,
            enable_xvfb_virtual_display=True,
        )
        if not self.page:
            return None

        # start processing the prompt
        try:
            self.process_prompt()
        except Exception as e:
            self.logger.error(f"- Error while processing prompt - {e}")
            self.database.update_process_status(self.process_id, "failed")
        finally:
            self.page.close()
