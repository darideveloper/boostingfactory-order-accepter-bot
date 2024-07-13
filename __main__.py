import os
import csv

from dotenv import load_dotenv

from libs.factory_scraper import FactoryScraper
from libs.discord_chat_reader import DiscordChatReader
from libs.web_scraping import WebScraping

# Read keywords from csv
current_folder = os.path.dirname(__file__)
csv_path = os.path.join(current_folder, "keywords.csv")
with open(csv_path, "r") as file:
    reader = csv.reader(file)
    KEYWORDS = list(map(lambda row: row[0], reader))

# Read .env's configuration
load_dotenv()
HEADLESS = os.getenv("SHOW_BROWSER") != "True"
USERNAME = os.getenv("USERNAME_SCRAPER")
PASSWORD = os.getenv("PASSWORD")
WAIT_TIME = int(os.getenv("WAIT_TIME"))
CHANNELS_NAMES = os.getenv("CHANNELS_NAMES").split(",")
SERVER_LINK = os.getenv("SERVER_LINK")

if __name__ == "__main__":
    
    # Create cookies folder
    current_folder = os.path.dirname(__file__)
    cookies_folder = os.path.join(current_folder, "cookies")
    os.makedirs(cookies_folder, exist_ok=True)
    
    # Initialize chrome
    scraper = WebScraping(headless=HEADLESS)
    
    # Initialize and login factory scraper
    factory_scraper = FactoryScraper(
        username=USERNAME,
        password=PASSWORD,
        keywords=KEYWORDS,
        wait_time=WAIT_TIME,
        scraper=scraper
    )
    factory_scraper.login()
    
    # Wait for new valid messages in discord
    discord_chat_reader = DiscordChatReader(
        scraper=scraper,
        server_link=SERVER_LINK,
        channels_names=CHANNELS_NAMES
    )
    discord_chat_reader.wait_for_messages()
    
    
    # Accept orders
    factory_scraper.automate_orders()
