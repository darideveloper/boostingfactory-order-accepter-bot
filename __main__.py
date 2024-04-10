import os

from dotenv import load_dotenv

from logic.factory_scraper import FactoryScraper

# Read .env's configuration
load_dotenv()
HEADLESS = os.getenv("SHOW_BROWSER") != "True"
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")

if __name__ == "__main__":
    factory_scraper = FactoryScraper(
        headless=HEADLESS, username=USERNAME, password=PASSWORD
    )

    factory_scraper.automate_orders()
