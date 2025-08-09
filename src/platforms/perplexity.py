import os
import time
from camoufox.sync_api import Camoufox
from src.utils.globals import save_file

def find_and_fill_input(page, prompt: str, timeout_ms: int = 8000) -> bool:
    try:
        sel = 'div[id="ask-input"]'
        page.wait_for_selector(sel, timeout=timeout_ms)
        page.click(sel)
        page.keyboard.type(prompt)
        page.keyboard.press("Enter")
        return True
    except Exception:
        return False


def wait_for_response_element(page, timeout_s: int = 60):
    copy_selector = 'button[data-testid="share-button"]'
    end = time.time() + timeout_s
    while time.time() < end:
        try:
            if page.query_selector(copy_selector):
                sel = 'div[id="markdown-content-0"]'
                try:
                    page.wait_for_selector(sel, timeout=3000)
                    el = page.query_selector(sel)
                    if el and el.inner_text().strip():
                        return el
                except Exception:
                    pass
        except Exception:
            pass
        time.sleep(0.5)
    return None


def query_perplexity(prompt: str):
    timestamp = int(time.time())
    save_folder = f"responses/perplexity/{timestamp}/"
    html_out = os.path.join(save_folder, "html_res.html")
    txt_out = os.path.join(save_folder, "txt_res.txt")

    with Camoufox(headless=False) as browser:
        page = browser.new_page()
        page.goto("https://www.perplexity.ai/", wait_until="networkidle", timeout=60000)
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
        time.sleep(1)

        if not find_and_fill_input(page, prompt):
            print("Impossible de trouver la zone d'entrée")
            return

        resp_el = wait_for_response_element(page)
        if not resp_el:
            print("Pas de réponse trouvée")
            return

        html_fragment = resp_el.inner_html()
        text_fragment = resp_el.inner_text()

        save_file(html_out, html_fragment)
        save_file(txt_out, text_fragment)

        print(f" HTML -> {html_out}")
        print(f" TXT  -> {txt_out}")
        
        # page.pause()


if __name__ == "__main__":
    prompt = "Explique-moi la théorie de la relativité en termes simples."
    query_perplexity(prompt)
