import sys
import time

from html_to_markdown import convert_to_markdown
from selenium.webdriver import Chrome
from selenium.webdriver.support.wait import WebDriverWait

sys.path.append("..")


from abc import ABC, abstractmethod
from contextlib import ContextDecorator
from src.utils.database import Database
from src.utils.aws_storage import AWSStorage
import os
from typing import Optional
from src.utils.globals import save_file
from func_retry import retry
from src.config.config import (
    PARSER_URL,
    PARSER_KEY,
    RESIDENTIAL_PROXY_PASSWORD,
    RESIDENTIAL_PROXY_USERNAME,
    S3_BUCKET_NAME,
    HEADLESS,
)
import httpx
import undetected_chromedriver as uc
from selenium.webdriver.support import expected_conditions as EC
from undetected_chromedriver import By

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
        self.page: Optional[Chrome] = None

    def navigate(self) -> bool:
        """Start the browser and navigate to the specified URL"""
        if not self.page:
            return False
        try:
            self.page.get(self.url)
            return True
        except Exception as e:
            self.logger.error(f"Error starting or navigating the page - {e}")
            return False

    def find_and_click(self, selector: str, error_message: str, timeout: int, click: bool = False) -> bool:
        """Click ELement if visible, if not raise Error"""
        if not self.page:
            raise ValueError("Browser is not started")
        try:
            WebDriverWait(self.page, timeout).until(
              EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
            )
            element = self.page.find_element(By.CSS_SELECTOR, selector)
            element.click() if click else None
            return True
        except Exception as e:
            self.logger.error(error_message)
            raise ValueError(f"{error_message} {str(e)}")

    def extract_content(self, selector: str) -> str | None:
        """Extract content from an element"""
        if not self.page:
            raise ValueError("Browser is not started")

        try:
            content_element = self.page.find_element(By.CSS_SELECTOR, selector)
            content = content_element.get_attribute("innerHTML")
            content_markdown = convert_to_markdown(content) if content else ""
            return content_markdown
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

    def save_response(self, content: Optional[str]) -> bool:
        """Save the generated output from the prompt in html and text file"""
        if not self.page:
            return False

        basekey = f"{self.name}/{self.process_id}"
        save_folder = f"responses/{basekey}/"
        text_name = "output.txt"
        screenshot_name = "screenshot.png"
        # video_name = "video.mp4"
        txt_out = os.path.join(save_folder, text_name)
        screeshot_path = os.path.join(save_folder, screenshot_name)
        # video_path = os.path.join(save_folder, video_name)

        # break the flow if no response in found
        if not content:
            self.logger.error("No generated output")
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

        # Start analyses
        # try:
        #     self.extract_brand_info(basekey)
        # except Exception as e:
        #     self.logger.error(f"Unable to start the parser - {e}")

        # Save ScreenShot
        try:
            self.page.save_screenshot(filename=screeshot_path)
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
        self.logger.error(error_message)
        self.database.update_process_status(self.process_id, "failed")
        raise ValueError(error_message)


    def process_prompt(self) -> None:
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
        is_response_saved = self.save_response(content)
        if not is_response_saved:
            error_message = "Error while saving response"
            self.save_raise_error(error_message)
        self.logger.info("Saving extracted data")

        # Step 5: Mark as Sucess on supabase
        self.database.update_process_status(self.process_id, "success")
        self.logger.info("Process Successfully ended !")



    @retry(times=3, delay=1)
    def send_prompt(self) -> None:
        """Start the workflow"""
        try:
            self.logger.info(f"Workflow Started - {self.name}")
            self.database.start_process(
                self.process_id, self.name, self.prompt, self.brand_report_id
            )

            # initialise page

            if HEADLESS == "yes":
                headless = True
            else:
                headless = False

            proxy = f"http://{RESIDENTIAL_PROXY_USERNAME}:{RESIDENTIAL_PROXY_PASSWORD}@isp.decodo.com:10000"

            options = uc.ChromeOptions()
            options.add_argument(f"--proxy-server={proxy}")


            self.page = uc.Chrome(options=options, version_main=142, headless=headless)
            self.page.implicitly_wait(self.timeout) 

            if not self.page:
                return None
            #
            # self.page.enable_human_mode()

            # start processing the prompt
            self.process_prompt()
            self.page.close()
            self.page.quit()
        except Exception as e:
            if self.page:
                self.page.close()
                self.page.quit()
            self.save_raise_error(f"Processing Error - {str(e)}")
