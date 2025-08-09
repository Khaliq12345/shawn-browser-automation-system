import os
import time
from camoufox.sync_api import Camoufox
from playwright.sync_api import Page
from src.utils.globals import save_file

MAX_TIMEOUT = 60000


def find_and_fill_input(page: Page, prompt: str) -> bool:
    try:
        prompt_input_selector = 'div[id="ask-input"]'
        # trying to fill the prompt
        try:
            page.fill(prompt_input_selector, prompt, timeout=MAX_TIMEOUT)
        except Exception as e:
            print(f"Can not fill the prompt input {e}")
        # Validate
        page.keyboard.press("Enter")
        return True
    except Exception as e:
        print(f"Error in find_and_fill_input {e}")
        return False


def extract_response(page: Page):
    share_btn_selector = 'button[data-testid="share-button"]'
    content_selector = 'div[id="markdown-content-0"]'
    # Looking for the share button (it appears once the response is generated)
    try:
        page.wait_for_selector(share_btn_selector, timeout=MAX_TIMEOUT)
    except Exception as e:
        print(f"Unable to find Share button {e}")
        return None
    # Looking for the response selector
    try:
        page.wait_for_selector(content_selector, timeout=MAX_TIMEOUT)
    except Exception as e:
        print(f"Unable to find the content {e}")
        return None
    content = page.query_selector(content_selector)
    return content


def query_perplexity(prompt: str):
    # Base Params
    timestamp = int(time.time())
    save_folder = f"responses/perplexity/{timestamp}/"
    html_out = os.path.join(save_folder, "html_res.html")
    txt_out = os.path.join(save_folder, "txt_res.txt")

    with Camoufox(
        headless=False,
    ) as browser:
        page = browser.new_page()
        page.goto("https://www.perplexity.ai/", wait_until="load", timeout=MAX_TIMEOUT)
        # To Skip the google login modal once it shows up
        page.evaluate("""
            const targetSrc = "https://accounts.google.com/gsi/iframe/select";
            const observer = new MutationObserver(() => {
                document.querySelectorAll("iframe").forEach(iframe => {
                    if (iframe.src && iframe.src.startsWith(targetSrc)) {
                        iframe.remove();
                        console.log("Iframe Google supprimé");
                    }
                });
            });
            observer.observe(document.body, { childList: true, subtree: true });
        """)
        # Try to fill up and execute the prompt
        if not find_and_fill_input(page, prompt):
            print("Impossible de trouver la zone d'entrée")
            return
        # Wait and retrieve the generated answer
        resp_el = extract_response(page)
        if not resp_el:
            print("Pas de réponse trouvée")
            return
        # Get and save html and text contents
        html_fragment = resp_el.inner_html()
        text_fragment = resp_el.inner_text()
        save_file(html_out, html_fragment)
        save_file(txt_out, text_fragment)
        print(f" Successfully Ended -- Output -> {save_folder}")


if __name__ == "__main__":
    prompt = "Explique-moi la théorie de la relativité en termes simples."
    query_perplexity(prompt)
