import os

from dotenv import load_dotenv

from logic.factory_scraper import FactoryScraper

# Read .env's configuration
load_dotenv()
HEADLESS = os.getenv("SHOW_BROWSER") != "True"
KEYWORDS = os.getenv("KEYWORDS").split(",")
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")

if __name__ == "__main__":
    factory_scraper = FactoryScraper(
        headless=HEADLESS, username=USERNAME, password=PASSWORD, keywords=KEYWORDS
    )

    factory_scraper.automate_orders()
