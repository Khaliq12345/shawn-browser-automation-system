import sys

sys.path.append("..")

from typing import Optional
from src.platforms.browser import BrowserBase
from html_to_markdown import convert_to_markdown
import time #utilisé pour pallier à wait_for_timeout
from botasaurus_driver import Wait


class PerplexityScraper(BrowserBase):
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
        date: str,
    ) -> None:
        super().__init__(
            brand_report_id,
            logger,
            url,
            prompt,
            name,
            process_id,
            timeout,
            country,
            date,
        )

    def find_and_fill_input(self) -> bool:
        if not self.page:
            return False
        try:
            time.sleep(5)
            self.page.run_js("document.body.click();")
            time.sleep(5)

            prompt_input_selector = 'div[id="ask-input"]'
            try:
                print("Filling input")
                self.page.type(prompt_input_selector, self.prompt)
                print("Done Filling")
            except Exception as e:
                print(f"Can not fill the prompt input {e}")
                return False

            # Validate
            try:
                submit_button = 'button[aria-label="Submit"]'
                self.page.click(submit_button)
            except Exception as e:
                print(f"Submit button is not available - {e}")
                return False
            return True
        except Exception as e:
            print(f"Error in find_and_fill_input {e}")
            return False


    def extract_response(self) -> Optional[str]:
        print("extracting response")

        if not self.page:
            return None

        # Attendre que la page charge la réponse
        time.sleep(10)

        # Essayer avec un script JS
        content = self.page.run_js("""
            const selectors = [
                'div[class*="prose"]',
                '.prose',
                'div[class*="answer"]',
                'div[class*="response"]',
                'main article',
                '[data-testid*="answer"]',
                'div[class*="markdown"]'
            ];

            for (const selector of selectors) {
                const elements = document.querySelectorAll(selector);
                for (const element of elements) {
                    const text = element.textContent || '';
                    const html = element.innerHTML || '';
                    if (text.length > 50) {
                        console.log('Found content with selector:', selector);
                        return html || text;
                    }
                }
            }

            return null;
        """)

        if content and content.strip():
            try:
                if '<' in content and '>' in content: #si c'est du html
                    content_markdown = convert_to_markdown(content)
                    return content_markdown
                else:
                    return content.strip()
            except Exception as e:
                print(f"Markdown conversion failed: {e}")
                return content.strip()

        # Fallback CSS si JavaScript échoue
        print("Echech du script js ,essai des sélecteurs CSS...")
        content_selectors = [
            "div[class*='prose']",
            ".prose",
            "div[class*='answer']",
            "div[class*='response']",
            "main article"
        ]

        for content_selector in content_selectors:
            try:
                content_element = self.page.select(content_selector, wait=Wait.SHORT)
                if content_element:
                    content = content_element.get_attribute("innerHTML")
                    if content and content.strip() and len(content.strip()) > 50:
                        try:
                            content_markdown = convert_to_markdown(content)
                            return content_markdown
                        except Exception as e:
                            return content.strip()
            except Exception:
                continue

        print("Aucun contenu trouvé")
        return None

