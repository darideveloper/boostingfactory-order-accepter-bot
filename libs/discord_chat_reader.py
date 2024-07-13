from time import sleep

from rich import print

from libs.web_scraping import WebScraping
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By


class DiscordChatReader ():
    
    def __init__(self, scraper: WebScraping, server_link: str,
                 channels_names: list) -> None:
        """_summary_

        Args:
            scraper (WebScraping): scraper instance
            channel_link (str): channel link
            channels_names (list): list of channels names
        """

        # Settigns
        self.scraper = scraper
        self.server_link = server_link
        self.channels_names = channels_names
        
        # Saved data
        self.saved_messages = []
            
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
    
    def __load_channel__(self, channel_elem: WebElement):
        """ Load specific channel and scroll to the bottom
        
        Args:
            channel_link (str): channel link
        """
        
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
        messages = list(map(lambda message: message.replace("\n", " "), messages))
        
        return messages
    
    def __get_new_messages__(self) -> list[str]:
        """ Validate new messages and return them
        
        Returns:
            list[str]: new messages found
        """
                
        # Get and validate each message
        new_messages = []
        messages = self.__get_messages__()
        for message in messages:
            
            # Skip saved messages
            if message in self.saved_messages:
                continue
            self.saved_messages.append(message)
            
            # TODO: Validate mssage
            print(f"New message: {message}")
            
            new_messages.append(message)
            
        return new_messages
    
    def __validate_login__(self):
        """ Validate if user is logged in """
                
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
        
        # Get and validate channels
        channels = self.__get_channels__()
        for channels_name, channel_elem in channels.items():

            # Load channel and read messages
            self.__load_channel__(channel_elem)
            self.__get_new_messages__()
            print()