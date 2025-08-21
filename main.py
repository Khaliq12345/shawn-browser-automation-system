import asyncio
import uvicorn
import sys

from src.platforms.google import GoogleScraper

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


# Launch API
def main():
    uvicorn.run(
        "src.api.app:app",
        host="localhost",
        port=8001,
        reload=True,
    )


def test():
    matching_scraper = GoogleScraper(
        url="https://gemini.google.com",
        prompt="All about python in 3 sentences",
        name="google",
        process_id="google_535348448",
    )
    matching_scraper.run_browser()
    pass


if __name__ == "__main__":
    main()
    # test()
