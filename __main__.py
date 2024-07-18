import os
import csv

from dotenv import load_dotenv

from libs.factory_scraper import FactoryScraper
from libs.discord_chat_reader import DiscordChatReader
from libs.web_scraping import WebScraping

# Read keywords from csv
KEYWORDS = []
current_folder = os.path.dirname(__file__)
csv_path = os.path.join(current_folder, "keywords.csv")
with open(csv_path, "r") as file:
    reader = csv.reader(file)
    for line in reader:
        if line:
            KEYWORDS.append(line[0])

# Read .env's configuration
load_dotenv()
HEADLESS = os.getenv("SHOW_BROWSER") != "True"
USERNAME = os.getenv("USERNAME_SCRAPER")
PASSWORD = os.getenv("PASSWORD")
WAIT_TIME = int(os.getenv("WAIT_TIME"))
DISCORD_CHANNELS_NAMES = os.getenv("DISCORD_CHANNELS_NAMES").split(",")
DISCORD_SERVER_LINK = os.getenv("DISCORD_SERVER_LINK")

if __name__ == "__main__":
    
    print("Starting chrome...")
    
    # Get windows username
    username = os.getlogin()
    chrome_data_folder = f"C:\\Users\\{username}\\AppData"
    chrome_data_folder += "\\Local\\Google\\Chrome\\User Data"
    
    # Initialize chrome
    scraper = WebScraping(
        headless=HEADLESS,
        chrome_folder=chrome_data_folder,
        start_killing=True,
    )
    
    # Initialize scrapers
    factory_scraper = FactoryScraper(
        scraper=scraper,
    )
    discord_chat_reader = DiscordChatReader(
        scraper=scraper,
        server_link=DISCORD_SERVER_LINK,
        channels_names=DISCORD_CHANNELS_NAMES,
        wait_time=WAIT_TIME,
        keywords=KEYWORDS,
    )
    
    # Validate login in factory
    factory_scraper.validate_login()
    discord_chat_reader.validate_login()
    
    # Main loop
    while True:
        # Wait for messages
        discord_chat_reader.wait_for_messages()
        # Accept orders
        factory_scraper.loop_orders(discord_chat_reader.order_ids)
