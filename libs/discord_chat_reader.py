from time import sleep

from rich import print

from libs.web_scraping import WebScraping
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By


class DiscordChatReader ():
    
    def __init__(self, scraper: WebScraping, server_link: str,
                 channels_names: list, wait_time: int, keywords: list) -> None:
        """_summary_

        Args:
            scraper (WebScraping): scraper instance
            channel_link (str): channel link
            channels_names (list): list of channels names
            wait_time (int): time to wait after end of loop when found new messages
            keywords (list): list of keywords to search in messages
        """

        # Settigns
        self.scraper = scraper
        self.server_link = server_link
        self.channels_names = channels_names
        self.wait_time = wait_time
        self.keywords = keywords
        
        # Saved data
        self.saved_messages = []
        self.order_ids = []
            
    def __load_page__(self):
        """ Load main page """
        
        self.scraper.set_page(self.server_link)
        sleep(5)
        self.scraper.refresh_selenium()
            
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
        try:
            channel_elem.click()
            self.scraper.refresh_selenium()
            sleep(1)
        except Exception:
            print(f"Error opening channel '{channel_name}'. Retrying in 5 seconds...")
            sleep(5)
            self.__load_page__()
            self.__load_channel__(channel_name, channel_elem)
    
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
    
    def __save_new_order_ids__(self):
        """ Validate new messages and return their order ids
        """
        
        print("\tReading messages...")
                
        # Get and validate each message
        messages = self.__get_messages__()
        for message in messages:
            
            # Skip saved messages
            if message in self.saved_messages:
                continue
            self.saved_messages.append(message)
            
            # # Validate mssage
            # keyword_found = False
            # for keyword in self.keywords:
                
            #     # Check if almost the most of the words are in the message
            #     words_num = len(keyword.split(" "))
            #     words_found = 0
            #     for word in keyword.split(" "):
            #         if word in message:
            #             words_found += 1
                
            #     if words_found >= words_num - 1:
            #         counter = f"{words_found}/{words_num} words found"
            #         print(f"\tNew message ({counter}): {message}")
            #         keyword_found = True
                    
            # if not keyword_found:
            #     print(f"\tMessage skipped: {message}")
            #     continue
                
            # Get order id
            message_parts = message.split("order id: ")
            message_parts = message_parts[-1].split(" ")
            order_id = message_parts[0]
            self.order_ids.append(order_id)
            
        if not self.order_ids:
            print("\tNo new orders found.")
                
    def validate_login(self):
        """ Validate if user is logged in """
        
        print("Validating Discord login...")
                
        self.__load_page__()
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
        
        print("\nWaiting for messages...")
        
        # Reset order ids
        self.order_ids = []
        
        self.__load_page__()
        
        order_ids_found = False
        while not order_ids_found:
        
            # Get and validate channels
            channels = self.__get_channels__()
            for channels_name, channel_elem in channels.items():

                # Load channel and read messages
                self.__load_channel__(channels_name, channel_elem)
                self.__save_new_order_ids__()
                
            # End loop if new orderids found
            if self.order_ids:
                order_ids_found = True
