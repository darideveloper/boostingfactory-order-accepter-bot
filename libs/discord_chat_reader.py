from time import sleep

from rich import print

from libs.web_scraping import WebScraping


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
        """ Load main page in new tab """
        
        # Create new tab
        self.scraper.open_tab()
        
        # Delete current tab
        self.scraper.close_tab()
        
        # Move to new tab
        self.scraper.switch_to_tab(0)
        
        # Open server link
        self.scraper.set_page(self.server_link)
        self.scraper.zoom(50)
        sleep(8)
        self.scraper.refresh_selenium()
            
    def __load_channel__(self, channel_name: str):
        """ Load specific channel and scroll to the bottom
        
        Args:
            channel_name (str): channel name
        """
        
        print(f"\nLoading channel '{channel_name}'...")
        
        selectors = {
            "channel": f'[data-dnd-name="{channel_name}"] a'
        }
        
        # Open chat
        try:
            self.scraper.click_js(selectors["channel"])
            self.scraper.refresh_selenium()
            sleep(1)
        except Exception:
            print(f"\tError opening channel '{channel_name}'. Retrying in 5 seconds...")
            sleep(5)
            self.__load_page__()
            self.__load_channel__(channel_name)
    
    def __get_messages__(self) -> list[str]:
        """ Read last @everyone visible messages in current channel
        
        Returns:
            list[str]: messages in channel
        """
        
        selectors = {
            "message": '[data-list-id="chat-messages"] > '
                       'li:nth-last-child(-n+8) h3 + div',
        }
        self.scraper.refresh_selenium()
        
        # Get messages with js script
        code = f"""
            var messages = document.querySelectorAll('{selectors["message"]}')
            var messagesText = Array.from(messages).map(message => message.textContent);
            return messagesText;
        """
        messages = self.scraper.driver.execute_script(code)

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
            
            # Validate mssage
            keyword_found = False
            for keyword in self.keywords:
                
                # Check if almost the most of the words are in the message
                words_num = len(keyword.split(" "))
                words_found = 0
                for word in keyword.split(" "):
                    if word in message:
                        words_found += 1
                
                if words_found == words_num:
                    print(f"\tNew message: {message}")
                    keyword_found = True
                    break
            
            if not keyword_found:
                continue
                
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
            for channels_name in self.channels_names:
                # Load channel and read messages
                self.__load_channel__(channels_name)
                self.__save_new_order_ids__()
                
            # End loop if new orderids found
            if self.order_ids:
                order_ids_found = True
