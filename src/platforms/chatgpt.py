import sys

sys.path.append("..")

from typing import Optional
from src.platforms.browser import BrowserBase
from html_to_markdown import convert_to_markdown
import time #utilisé pour pallier à wait_for_timeout
from botasaurus_driver import Wait


class ChatGPTScraper(BrowserBase):
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

    #méthodes à changer : wait_for_timeout,mouse,type,keyboard,wait_for_selector,query_selector
    def find_and_fill_input(self) -> bool:
        if not self.page:
            return False
        try:
            time.sleep(5)
            self.page.run_js("document.body.click();") #on clique sur body pour s'assurer que le focus est sur la page
            time.sleep(5)

            prompt_input_selector = 'textarea[data-id="root"]'
            alt_selector = '[data-virtualkeyboard="true"]'

            try:
                print("Filling input")
                try:
                    self.page.type(prompt_input_selector, self.prompt)
                except:
                    self.page.type(alt_selector, self.prompt)
                print("Done Filling")
            except Exception as e:
                print(f"Can not fill the prompt input {e}")
                return False

            # Validate
            self.page.run_js("""
                const textarea = document.querySelector('textarea[data-id="root"]') ||
                               document.querySelector('[data-virtualkeyboard="true"]');
                if (textarea) {
                    const event = new KeyboardEvent('keydown', {
                        key: 'Enter',
                        code: 'Enter',
                        keyCode: 13,
                        bubbles: true,
                        ctrlKey: false
                    });
                    textarea.dispatchEvent(event);

                    const sendButton = document.querySelector('button[data-testid="send-button"]') ||
                                     document.querySelector('[data-testid="send-button"]') ||
                                     document.querySelector('button[type="submit"]');
                    if (sendButton) {
                        sendButton.click();
                    }
                }
            """)
            return True
        except Exception as e:
            print(f"Error in find_and_fill_input {e}")
            return False

    def extract_response(self) -> Optional[str]:
        print("extracting response")

        if not self.page:
            return None

        time.sleep(15)

        content_selectors = [
            'div[data-message-author-role="assistant"] div[class*="markdown"]',
            'div[data-message-author-role="assistant"]',
            '[data-message-author-role="assistant"]',
            'div[data-testid*="conversation-turn"]:last-child',
            '.prose',
            '[class*="prose"]'
        ]

        content = None
        for content_selector in content_selectors:
            try:
                content_element = self.page.select(content_selector, wait=Wait.SHORT)
                if content_element:
                    content = content_element.get_attribute("innerHTML")
                    if content and content.strip():
                        break
                    else:
                        text_content = content_element.get_attribute("textContent")
                        if text_content and text_content.strip():
                            content = text_content
                            break
            except Exception:
                continue

        if not content or content.strip() == "":
            content = self.page.run_js("""
                const assistantMessages = document.querySelectorAll('[data-message-author-role="assistant"]');
                if (assistantMessages.length > 0) {
                    const lastMessage = assistantMessages[assistantMessages.length - 1];
                    const markdownDiv = lastMessage.querySelector('[class*="markdown"], .prose, [class*="prose"]');
                    if (markdownDiv) {
                        return markdownDiv.innerHTML || markdownDiv.textContent;
                    }
                    return lastMessage.innerHTML || lastMessage.textContent;
                }

                const conversations = document.querySelectorAll('[data-testid*="conversation-turn"]');
                if (conversations.length >= 2) {
                    const lastConv = conversations[conversations.length - 1];
                    return lastConv.innerHTML || lastConv.textContent;
                }
                return null;
            """)

        if not content or content.strip() == "":
            return None

        try:
            if '<' in content and '>' in content:
                content_markdown = convert_to_markdown(content)
                return content_markdown
            else:
                return content.strip()
        except Exception as e:
            print(f"ERROR: Markdown conversion failed: {e}")
            return content.strip() if content else None

