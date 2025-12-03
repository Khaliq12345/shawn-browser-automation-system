import sys

sys.path.append(".")

from typing import Optional
from src.platforms.browser import BrowserBase
from html_to_markdown import convert_to_markdown


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
            search_url = f"https://www.google.com/search?q={self.prompt}&oq={self.prompt}"
            self.page.google_get(search_url, timeout=self.timeout, bypass_cloudflare=True)
            return True
        except Exception as e:
            self.logger.error(f"Error starting or navigating the page - {e}")
            return False


    def find_and_fill_input(self) -> bool:
        print("Filling input")
        return True

    def extract_response(self) -> Optional[str]:
        self.logger.error("Extracting response")
        if not self.page:
            return None
        content_selector = 'div[jsmodel="k8Azyd E23uIf"]'
        see_more_selector = 'div[aria-controls="m-x-content"]'

        # click on see more (ai answer)
        if not self.page.is_element_present(see_more_selector, wait=5):
            self.logger.error("AI Answer not visible")
            return None
        try:
            self.page.click(see_more_selector, wait=self.timeout)
        except Exception as e:
            self.logger.error(f"Unable to find the see more buttons {e}")
            return None

        # wait for content to be visible
        try:
            self.page.wait_for_element(content_selector, wait=self.timeout)
        except Exception as e:
            self.logger.error(f"Unable to find the content {e}")
            return None

        try:
            content_element = self.page.wait_for_element(content_selector)
            content = content_element.html if content_element else ""
            content_markdown = convert_to_markdown(content)
            return content_markdown
        except Exception as e:
            self.logger.error(f"Unable to extract content {e}")
            return None
