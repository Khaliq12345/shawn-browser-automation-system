# from src.platforms.gemini import GeminiScraper
# from src.platforms.perplexity import PerplexityScraper
from src.platforms.chatgpt import ChatGPTScraper


def main():
    print("Hello from shawn-browser-automation-system !")
    prompt = "Explique-moi la théorie de la relativité en termes simples."

    with ChatGPTScraper(
        url="https://chatgpt.com/", prompt=prompt, name="chatgpt"
    ) as browser:
        browser.send_prompt()
    # 
    # with GeminiScraper(
    #     url="https://gemini.google.com", prompt=prompt, name="gemini"
    # ) as browser:
    #     browser.send_prompt()
    # 
    # with PerplexityScraper(
    #     url="https://www.perplexity.ai/", prompt=prompt, name="perplexity"
    # ) as browser:
    #     browser.send_prompt()

if __name__ == "__main__":
    main()
