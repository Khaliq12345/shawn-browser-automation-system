from abc import ABC, abstractmethod
from contextlib import ContextDecorator
import sys
from src.utils.database import (
    update_process_status,
    start_process,
    save_awsupload,
)
from src.utils.aws_storage import AWSStorage

sys.path.append("..")
import os
from typing import Optional
from src.utils.globals import save_file
from src.config.config import PROXY_USERNAME, PROXY_PASSWORD

# PROXY configs
PROXIES = {"us": "10000"}


class BrowserBase(ContextDecorator, ABC):
    def __init__(
        self,
        browser,
        logger,
        url: str,
        prompt: str,
        name: str,
        process_id: str,
        timeout: int,
        country: str,
        headless: bool = False,
    ) -> None:
        self.url = url
        self.prompt = prompt
        self.name = name
        self.process_id = process_id
        self.headless = headless
        self.browser = browser
        self.logger = logger
        self.context = None
        self.timeout = timeout
        self.bucket = "browser-outputs"
        self.storage = AWSStorage(self.bucket)
        self.uid = self.process_id.split("_")[1]
        self.country = country

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
        save_awsupload(f"{self.bucket}/{key}", self.name, self.prompt)

    def save_response(self, content: Optional[str]) -> bool:
        """Save the generated output from the prompt in html and text file"""

        basekey = f"{self.name}/{self.uid}"
        save_folder = f"responses/{basekey}/"
        text_name = "output.txt"
        txt_out = os.path.join(save_folder, text_name)

        # break the flow if no response in found
        if not content:
            self.logger.error("No generated output")
            print("No generated output")
            return False

        # Save Text Result
        try:
            save_file(txt_out, content)
            self.aws_upload_file(f"{basekey}/{text_name}", txt_out)
        except Exception as e:
            self.logger.error(f"Unable to save output - {e}")
            return False

        # Save ScreenShot
        try:
            screenshot_name = "screenshot.png"
            screeshot_path = f"responses/{self.name}/{self.uid}/{screenshot_name}"
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
                video_name = "video.mp4"
                video_path = os.path.join(f"responses/{basekey}/", video_name)
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

    def send_prompt(self) -> None:
        """Start the workflow"""
        print("Creating context")
        self.logger.info("Creating Context")
        self.context = self.browser.new_context(
            record_video_dir=f"responses/{self.name}/{self.uid}/",
            record_video_size={"width": 1280, "height": 720},
            proxy={
                "server": f"http://{self.country}.decodo.com:{PROXIES[self.country]}",
                "username": PROXY_USERNAME,
                "password": PROXY_PASSWORD,
            },
        )
        try:
            self.page = self.context.new_page()
            self.logger.info("- Workflow Started")
            start_process(self.process_id, self.name, self.prompt)

            # Set 1: Navigate to the platform
            is_navigate = self.navigate()
            if not is_navigate:
                self.logger.error("- Error starting or navigating the page")
                update_process_status(self.process_id, "failed")
                return None
            self.logger.info("- Successfully navigated to the page")

            # Step 2: Fill and Submit the input
            is_filled = self.find_and_fill_input()
            if not is_filled:
                self.logger.error("- Error filling the prompt")
                update_process_status(self.process_id, "failed")
                return None
            self.logger.info("- Prompt successfully filled")

            # Step 3: Extract the generated response
            content = self.extract_response()
            if not content:
                self.logger.error("- Error while extracting the response")
                update_process_status(self.process_id, "failed")
                return None
            self.logger.info("- Response successfully extracted")

            # Step 4: Save the response
            self.save_response(content)
            self.logger.info("- Saving extracted data")

            # Step 5: Mark as Sucess on supabase
            update_process_status(self.process_id, "success")
            self.logger.info("- Process Successfully ended !")

        finally:
            self.page.close()
            self.context.close()
            print("Context and Page instance closed")
