import sys



sys.path.append(".")

from typing import Optional
from src.platforms.browser import BrowserBase


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

    def navigate(self) -> bool:
        """Override navigate to use Google search URL with prompt"""
        self.logger.info("Loading the page")
        if not self.page:
            return False
        try:
            # Use Google search URL format with prompt
            search_url = f"https://www.google.com/search?q={self.prompt}"
            self.page.goto(search_url, timeout=self.timeout)
            self.logger.info(self.page.title)
            return True
        except Exception as e:
            self.logger.error(f"Error starting or navigating the page - {e}")
            return False


    def find_and_fill_input(self) -> bool:
        self.logger.info("Filling input")
        return True

    def extract_response(self) -> Optional[str]:
        self.logger.info("Extracting response")
        if not self.page:
            return None
        content_selector = 'div[jsmodel="k8Azyd E23uIf"]'
        see_more_selector = 'div[aria-controls="m-x-content"]'

        # see_more_selector = 'button[id="llm-show-more-button"]'
        # content_selector = 'div[id="llm-snippet"]'

        # click on see more (ai answer)
        self.find_and_click(see_more_selector, "Ai overview not visible", timeout=5*1000, click=True)

        # wait for content to be visible
        self.find_and_click(content_selector, timeout=self.timeout, error_message="Unable to find the content")


        content = self.extract_content(content_selector)
        return content
