import asyncio
import uvicorn

from src.platforms.google import GoogleScraper


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
        url="https://google.com",
        prompt="Who is Patrick Lumumba",
        name="google",
        process_id="google_535349999999",
    )
    asyncio.run(matching_scraper.send_prompt())


if __name__ == "__main__":
    # main()
    test()
