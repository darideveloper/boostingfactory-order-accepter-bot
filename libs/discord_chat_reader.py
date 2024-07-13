import os
from time import sleep

import pickle
from rich import print

from libs.web_scraping import WebScraping
from selenium.webdriver.remote.webelement import WebElement


class DiscordChatReader ():
    
    def __init__(self, scraper: WebScraping, server_link: str, channels_names: list,
                 user: str, password: str) -> None:
        """_summary_

        Args:
            scraper (WebScraping): scraper instance
            channel_link (str): channel link
            channels_names (list): list of channels names
        """
        
        self.scraper = scraper
        self.server_link = server_link
        self.channels_names = channels_names
        self.user = user
        self.password = password
        self.login_page = "https://discord.com/login"
        
        # Saved data
        self.saved_messages = []
        
        # Cookies path
        # Check if there are cookies
        current_folder = os.path.dirname(os.path.abspath(__file__))
        parent_folder = os.path.dirname(current_folder)
        cookies_folder = os.path.join(parent_folder, "cookies")
        self.cookies_file = os.path.join(cookies_folder, "discord_chat_reader.pkl")
        
    def __manual_login__(self):
        """ Manual login with user and password, and update cookies """
        
        # Login
        selectors = {
            "username": '[name="email"]',
            "password": '[name="password"]',
            "submit": "button[type='submit']",
        }
            
        self.scraper.send_data(selectors["username"], self.user)
        self.scraper.send_data(selectors["password"], self.password)
        self.scraper.click(selectors["submit"])
        
        sleep(5)
        self.scraper.refresh_selenium()
        
        # Validate login success
        current_url = self.scraper.driver.current_url
        if "login" in current_url:
            print("Manual login discord failed. Check credentials and try again.")
            quit()
        
        # Save cookies
        cookies = self.scraper.driver.get_cookies()
        with open(self.cookies_file, "wb") as file:
            pickle.dump(cookies, file)
            
        print("Manual login in Discord success.")
            
    def __get_channels__(self) -> dict[str, WebElement]:
        """ Load specific server and get channels """
        
        selectors = {
            "channel": '[aria-label="Canales"] > li a',
        }
                
        channels_data = {}
        channels_elems = self.scraper.get_elems(selectors["channel"])
        for channel_elem in channels_elems:
            channel_name = channel_elem.text
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
    
    def login(self):
        """ Login loading cookies """
        
        print(f"Login in Discord with user '{self.user}'...")
        
        # Load server page
        self.scraper.set_page(self.login_page)
        sleep(5)
        self.scraper.refresh_selenium()
        
        # First login
        if not os.path.exists(self.cookies_file):
            self.__manual_login__()
            return None
        
        # Delete old cookies
        self.scraper.driver.delete_all_cookies()
        
        # Load cookies
        cookies = pickle.load(open(self.cookies_file, "rb"))
        for cookie in cookies:
            self.scraper.driver.add_cookie(cookie)
        self.scraper.driver.refresh()
        self.scraper.refresh_selenium()
            
        # Validate if cookies are valid
        current_url = self.scraper.driver.current_url
        if "login" in current_url:
            self.__manual_login__()
            
        print("Login in Discord success.")
            
    def wait_for_messages(self):
        """ Wait for new messages, valdiate them and return
        """
        
        # Load server page
        self.scraper.set_page(self.server_link)
        sleep(5)
        self.scraper.refresh_selenium()
        
        # Get and validate channels
        channels = self.__get_channels__()
        for channels_name, channel_elem in channels.items():

            # Load channel and read messages
            self.__load_channel__(channel_elem)
            self.__get_new_messages__()
            print()