from abc import ABC, abstractmethod
from contextlib import ContextDecorator
import sys
from src.utils.database import update_process_status, start_process

sys.path.append("..")

import os
from typing import Optional
from camoufox.sync_api import Camoufox
from playwright.sync_api import ElementHandle
from src.utils.globals import save_file
from src.utils.redis_utils import RedisBase


class BrowserBase(ContextDecorator, ABC):
    def __init__(
        self, url: str, prompt: str, name: str, process_id: str, headless: bool = False
    ) -> None:
        self.url = url
        self.prompt = prompt
        self.name = name
        self.process_id = process_id
        self.camoufox = Camoufox().start()
        self.page = self.camoufox.new_page()
        self.headless = headless
        self.timeout = 60000
        self.redis = RedisBase(process_id)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.page.close()
        self.camoufox.close()
        print("Browser instance closed")
        return True

    def navigate(self) -> bool:
        """Start the browser and navigate to the specified URL"""
        try:
            self.page.goto(self.url, timeout=self.timeout)
            return True
        except Exception as e:
            print(f"Error starting or navigating the page - {e}")
            return False

    def save_response(self, content: Optional[ElementHandle]) -> bool:
        """Save the generated output from the prompt in html and text file"""
        save_folder = f"responses/{self.name}/{self.process_id}/"
        html_out = os.path.join(save_folder, "html_res.html")
        txt_out = os.path.join(save_folder, "txt_res.txt")

        # break the flow if no response in found
        if not content:
            self.redis.set_log("No generated output")
            print("No generated output")
            return False

        html_fragment = content.inner_html()
        text_fragment = content.inner_text()
        save_file(html_out, html_fragment)
        save_file(txt_out, text_fragment)
        self.redis.set_log(f" Successfully saved -- Output -> {save_folder}")
        return True

    @abstractmethod
    def find_and_fill_input(self) -> bool:
        """Platform-specific method to fill and submit the prompt."""
        pass

    @abstractmethod
    def extract_response(self) -> Optional[ElementHandle]:
        """Platform-specific method to extract the response."""
        pass

    def send_prompt(self) -> None:
        """Start the workflow"""
        self.redis.set_log("- Workflow Started")
        start_process(self.process_id, self.name, self.prompt)

        # Set 1: Navigate to the platform
        is_navigate = self.navigate()
        if not is_navigate:
            self.redis.set_log("- Error starting or navigating the page")
            update_process_status(self.process_id, "failled")
            return None
        self.redis.set_log("- Successfully navigated to the page")

        # Step 2: Fill and Submit the input
        is_filled = self.find_and_fill_input()
        if not is_filled:
            self.redis.set_log("- Error filling the prompt")
            update_process_status(self.process_id, "failled")
            return None
        self.redis.set_log("- Prompt successfully filled")

        # Step 3: Extract the generated response
        content = self.extract_response()
        if not content:
            self.redis.set_log("- Error while extracting the response")
            update_process_status(self.process_id, "failled")
            return None
        self.redis.set_log("- Response successfully extracted")

        # Step 4: Save the response
        self.save_response(content)
        self.redis.set_log("- Saving extracted data")

        # Step 5: Mark as Sucess on supabase
        update_process_status(self.process_id, "success")
        self.redis.set_log("- Process Successfully ended !")
