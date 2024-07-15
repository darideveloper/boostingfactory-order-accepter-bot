import os
import csv
from time import sleep

from rich import print

from libs.web_scraping import WebScraping
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By


class DiscordChatReader ():
    
    def __init__(self, scraper: WebScraping, server_link: str,
                 channels_names: list, wait_time: int) -> None:
        """_summary_

        Args:
            scraper (WebScraping): scraper instance
            channel_link (str): channel link
            channels_names (list): list of channels names
            wait_time (int): time to wait after end of loop when found new messages
        """

        # Settigns
        self.scraper = scraper
        self.server_link = server_link
        self.channels_names = channels_names
        self.wait_time = wait_time
        
        # Saved data
        self.saved_messages = []
        
        # Read keywords from csv
        current_folder = os.path.dirname(__file__)
        project_folder = os.path.dirname(current_folder)
        keywords_path = os.path.join(project_folder, "keywords.csv")
        with open(keywords_path, "r") as file:
            keywords_reader = csv.reader(file)
            self.keywords = list(map(lambda row: row[0].lower(), keywords_reader))
            
    def __get_channels__(self) -> dict[str, WebElement]:
        """ Load specific server and get channels """
        
        selectors = {
            "channel": '[aria-label="Canales"] > li a',
            "channel_name": '[class^="name_"]',
        }
                
        channels_data = {}
        channels_elems = self.scraper.get_elems(selectors["channel"])
        for channel_elem in channels_elems:
            channel_name_elem = channel_elem.find_element(
                By.CSS_SELECTOR,
                selectors["channel_name"]
            )
            channel_name = channel_name_elem.text
            if channel_name in self.channels_names:
                channels_data[channel_name] = channel_elem
                
        if not channels_data:
            print("Discord channels not found. Check server link and channels names.")
            quit()
        
        return channels_data
    
    def __load_channel__(self, channel_name: str, channel_elem: WebElement):
        """ Load specific channel and scroll to the bottom
        
        Args:
            channel_name (str): channel name
            channel_elem (WebElement): channel element
        """
        
        print(f"\nLoading channel '{channel_name}'...")
        
        # Open chat
        channel_elem.click()
        self.scraper.refresh_selenium()
        sleep(1)
    
    def __get_messages__(self) -> list[str]:
        """ Read last @everyone visible messages in current channel
        
        Returns:
            list[str]: messages in channel
        """
        
        selectors = {
            "message": '[data-list-id="chat-messages"] > li h3 + div',
        }
        
        # Get last 5 messages texts
        messages = self.scraper.get_texts(selectors["message"])
        messages = messages[-5:]
        
        # Get only @everyone messages and remove new lines
        messages = list(filter(lambda message: "@everyone" in message, messages))
        messages = list(map(
            lambda message: message.replace("\n", " ").lower(),
            messages
        ))
        
        return messages
    
    def __get_new_messages__(self, channels_name: str) -> list[str]:
        """ Validate new messages and return them
        
        Args:
            channels_name (str): channel name
        
        Returns:
            list[str]: new messages found
        """
        
        print("\tReading messages...")
                
        # Get and validate each message
        new_messages = []
        messages = self.__get_messages__()
        for message in messages:
            
            # Skip saved messages
            if message in self.saved_messages:
                continue
            self.saved_messages.append(message)
            
            # Validate mssage
            keyword_found = False
            for keyword in self.keywords:
                
                # Check if almost the most of the words are in the message
                words_num = len(keyword.split(" "))
                words_found = 0
                for word in keyword.split(" "):
                    if word in message:
                        words_found += 1
                
                if words_found >= words_num - 1:
                    counter = f"{words_found}/{words_num} words found"
                    print(f"\tNew message ({counter}): {message}")
                    new_messages.append(message)
                    keyword_found = True
                    
            if not keyword_found:
                print(f"\tMessage skipped: {message}")
        
        if not new_messages:
            print("\tNo new messages found.")
            
        return new_messages
    
    def __validate_login__(self):
        """ Validate if user is logged in """
        
        print("Validating Discord login...")
                
        self.scraper.set_page(self.server_link)
        sleep(5)
        self.scraper.refresh_selenium()
        current_url = self.scraper.driver.current_url
        if "/login" in current_url:
            print("Discord session expired. Login again in Chrome.")
            quit()
            
        print("Logged in Discord.")
        sleep(5)
        self.scraper.refresh_selenium()
            
    def wait_for_messages(self):
        """ Wait for new messages, valdiate them and return
        """
        
        # Load server page and validate login
        self.__validate_login__()
        
        messages_found = False
        while not messages_found:
        
            # Get and validate channels
            channels = self.__get_channels__()
            for channels_name, channel_elem in channels.items():

                # Load channel and read messages
                self.__load_channel__(channels_name, channel_elem)
                new_messages = self.__get_new_messages__(channels_name)
                if new_messages:
                    messages_found = True
                    sleep(self.wait_time)
                    break