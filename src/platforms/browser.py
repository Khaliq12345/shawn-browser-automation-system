from abc import ABC, abstractmethod
from contextlib import ContextDecorator
import sys
from src.utils.database import update_process_status, start_process, save_awsupload
from src.utils.aws_storage import AWSStorageAsync

sys.path.append("..")
# from playwright.async_api import async_playwright
import os
from typing import Optional
from camoufox.async_api import AsyncCamoufox
from browserforge.fingerprints import Screen
from src.utils.globals import save_file
from src.utils.redis_utils import AsyncRedisBase


class BrowserBase(ContextDecorator, ABC):
    def __init__(
        self,
        url: str,
        prompt: str,
        name: str,
        process_id: str,
        headless: bool = False,
    ) -> None:
        self.url = url
        self.prompt = prompt
        self.name = name
        self.process_id = process_id
        self.headless = headless
        self.camoufox = None
        self.browser = None
        self.context = None
        self.timeout = 60000
        self.redis = AsyncRedisBase(process_id)
        self.bucket = "browser-outputs"
        self.storage = AWSStorageAsync(self.bucket)
        self.uid = self.process_id.split("_")[1]

    async def navigate(self) -> bool:
        """Start the browser and navigate to the specified URL"""
        try:
            await self.page.goto(self.url, timeout=self.timeout)
            return True
        except Exception as e:
            print(f"Error starting or navigating the page - {e}")
            return False

    async def save_response(self, content: Optional[str]) -> bool:
        """Save the generated output from the prompt in html and text file"""

        basekey = f"{self.name}/{self.uid}"
        save_folder = f"responses/{basekey}/"
        text_name = "output.txt"
        txt_out = os.path.join(save_folder, text_name)

        # break the flow if no response in found
        if not content:
            await self.redis.set_log("No generated output")
            print("No generated output")
            return False

        save_file(txt_out, content)
        # Save Text Result
        await self.aws_upload_file(f"{basekey}/{text_name}", txt_out)
        # await self.storage.save_file(f"{basekey}/{text_name}", txt_out)

        # Save ScreenShot
        screenshot_name = "screenshot.png"
        screeshot_path = f"responses/{self.name}/{self.uid}/{screenshot_name}"
        await self.page.screenshot(path=screeshot_path, full_page=True)
        await self.aws_upload_file(f"{basekey}/{screenshot_name}", screeshot_path)
        # await self.storage.save_file(f"{basekey}/{screenshot_name}", screeshot_path)

        # Save Video
        video = self.page.video
        if video:
            await self.redis.set_log("Successfully recorded video")
            await self.page.close()
            video_name = "video.mp4"
            video_path = os.path.join(f"responses/{basekey}/", video_name)
            await video.save_as(video_path)
            # Save Video to aws
            await self.aws_upload_file(f"{basekey}/{video_name}", video_path)
            # await self.storage.save_file(f"{basekey}/{video_name}", video_path)
        else:
            await self.redis.set_log("Unable to record video")

        await self.redis.set_log(f" Successfully saved -- Output -> {save_folder}")
        return True

    async def aws_upload_file(self, key: str, path: str) -> None:
        await self.storage.save_file(key, path)
        await save_awsupload(f"{self.bucket}/{key}", self.name, self.prompt)

    @abstractmethod
    async def find_and_fill_input(self) -> bool:
        """Platform-specific method to fill and submit the prompt."""
        pass

    @abstractmethod
    async def extract_response(self) -> Optional[str]:
        """Platform-specific method to extract the response."""
        pass

    async def send_prompt(self) -> None:
        """Start the workflow"""
        async with AsyncCamoufox(
            screen=Screen(max_width=1920, max_height=1080), headless=self.headless
        ) as self.browser:
            self.context = await self.browser.new_context(
                record_video_dir=f"responses/{self.name}/{self.uid}/",
                record_video_size={"width": 1280, "height": 720},
            )
            self.page = await self.context.new_page()

            await self.redis.set_log("- Workflow Started")
            await start_process(self.process_id, self.name, self.prompt)

            # Set 1: Navigate to the platform
            is_navigate = await self.navigate()
            if not is_navigate:
                await self.redis.set_log("- Error starting or navigating the page")
                await update_process_status(self.process_id, "failed")
                return None
            await self.redis.set_log("- Successfully navigated to the page")

            # Step 2: Fill and Submit the input
            is_filled = await self.find_and_fill_input()
            if not is_filled:
                await self.redis.set_log("- Error filling the prompt")
                await update_process_status(self.process_id, "failed")
                return None
            await self.redis.set_log("- Prompt successfully filled")

            # Step 3: Extract the generated response
            content = await self.extract_response()
            if not content:
                await self.redis.set_log("- Error while extracting the response")
                await update_process_status(self.process_id, "failed")
                return None
            await self.redis.set_log("- Response successfully extracted")

            # Step 4: Save the response
            await self.save_response(content)
            await self.redis.set_log("- Saving extracted data")

            # Step 5: Mark as Sucess on supabase
            await update_process_status(self.process_id, "success")
            await self.redis.set_log("- Process Successfully ended !")

            print("Browser instance closed")
