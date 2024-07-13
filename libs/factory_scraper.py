import os
from time import sleep

import pickle
from rich import print

from libs.web_scraping import WebScraping


class FactoryScraper():
    def __init__(
        self,
        username: str,
        password: str,
        keywords: list,
        scraper: WebScraping,
        wait_time: int = 60,
    ) -> None:
        """starts chrome and initializes the scraper

        args:
            username: (str) username from .env
            password: (str) passsword from .env
            keywords: (list, str) filter titles for the targeted orders.
            headless: (bool) enables headless mode.
        """
        
        self.scraper = scraper

        # credentials
        self.username = username
        self.password = password

        # Title filter
        self.keywords = keywords
        
        # Refresh time
        self.wait_time = wait_time

        self.extracted_orders = {}
        
        current_folder = os.path.dirname(os.path.abspath(__file__))
        project_folder = os.path.dirname(current_folder)
        cookies_folder = os.path.join(project_folder, "cookies")
        self.cookies_file = os.path.join(cookies_folder, "factory_scraper.pkl")

    def login(self) -> None:
        """checks if session cookies exists

        if the cookies are found load them
        ifnot perfoms login.
        """

        self.scraper.set_page("https://www.boostingfactory.com/login")

        sleep(3)
        self.scraper.refresh_selenium()

        selectors = {
            "username": "#uName",
            "password": "#uPassword",
            "submit": "button[type='submit']",
        }

        # search for local cookies
        if os.path.exists("cookies.pkl"):
            # if cookies are found load them
            with open("cookies.pkl", "rb") as file:
                cookies = pickle.load(file)
                
                self.__load_cookies__()
                self.scraper.refresh_selenium()
                
            # Validate login cookies
            current_page = self.scraper.driver.current_url
            if "login" in current_page:
                print("Login failed. Posible cookies expired. Traying again...")
                
                # Delete cookies file
                if os.path.exists(self.cookies_file):
                    os.remove(self.cookies_file)
                
                # Try login again
                self.login()
                
                return None
            else:
                print("Login successful.")
                return None
                        
        # if cookies doesn't exists do login
        username = self.scraper.get_elem(selectors["username"])
        username.send_keys(self.username)

        password = self.scraper.get_elem(selectors["password"])
        password.send_keys(self.password)

        self.scraper.click_js(selectors["submit"])
        
        # Validate login credentials
        current_page = self.scraper.driver.current_url
        if "login" in current_page:
            print("Login factory failed. Check credentials and try again.")
            quit()
        else:
            print("Login successful.")

        # store cookies
        cookies = self.scraper.get_browser().get_cookies()
        with open(self.cookies_file, "wb") as file:
            pickle.dump(cookies, file)

    def __load_cookies__(self) -> None:
        """Load cookies into the current session."""
        
        cookies = pickle.load(open(self.cookies_file, "rb"))
        for cookie in cookies:
            self.scraper.driver.add_cookie(cookie)

        self.scraper.set_page("https://www.boostingfactory.com/profile")
        self.zoom(50)

    def __loop_orders__(self) -> None:
        """Loop through orders and stores it to be processed later."""

        selectors = {
            "orders_tab": ".orders .nav.nav-tabs > li:first-child a",
            "orders": "div#availableOrders .orders-preloader + div",
            "order_button": "div#availableOrders div.single-order' \
                '.order-detail-btn .btn-for-bright",
            "order_link": "a",
            "order_title": "h3",
            "order_accept": "button.btn.order-accept-btn.btn-for-bright",
            "order_ok": ".answer-btn",
        }

        # Move to orders tab
        self.scraper.click_js(selectors["orders_tab"])
        self.scraper.refresh_selenium(time_units=0.1)

        orders = self.scraper.get_elems(selectors["orders"])

        orders_accepted = 0
        for order in range(0, len(orders)):

            # Validate order title
            selector_order = f"{selectors['orders']}:nth-child({(order + 1) * 2})"
            selector_title = f"{selector_order} {selectors['order_title']}"
            title = self.scraper.get_text(selector_title)
            target = self.__filter__(title)

            if not target:
                continue

            # Accept order
            self.scraper.click_js(f"{selector_order} {selectors['order_accept']}")
            self.scraper.refresh_selenium()
            self.scraper.click_js(f"{selectors['order_ok']}")

            print(f"Order {title} accepted")
            orders_accepted += 1

        print(f"Total orders accepted: {orders_accepted}")

    def __filter__(self, title) -> bool:
        """Filter keywords from order titles.

        Args:
            title: (str) title keyword

        Returns: boolean
        """

        for keyword in self.keywords:
            if keyword.strip().lower() == str(title).strip().lower():
                return True
        return False

    def __retrieve_new_orders__(self) -> None:
        """Search for new orders."""
        self.scraper.set_page("https://www.boostingfactory.com/profile")

    def automate_orders(self) -> None:
        """automate accepting orders."""

        while True:

            # Loop available orders and accept by title
            self.__loop_orders__()

            # Wait 1 minute
            print(f"waiting {self.wait_time} milliseconds")
            sleep(self.wait_time / 1000)
