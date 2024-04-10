import os
import pickle
from time import sleep

from libs import WebScraping


class FactoryScraper(WebScraping):
    def __init__(self, username: str, password: str, headless: bool = False) -> None:
        """starts chrome and initializes the scraper

        args:
            headless: (bool) enables headless mode.
            username: (str) username from .env
            password: (str) passsword from .env
        """

        # start scraper class
        super().__init__(headless=headless)

        # credentials
        self.username = username
        self.password = password

    def __login__(self) -> None:
        """checks if session cookies exists

        if the cookies are found load them
        ifnot perfoms login.
        """

        self.set_page("https://www.boostingfactory.com/login")

        sleep(3)

        selectors = {
            "username": "input#uName",
            "password": "input[type='password'][name='uPassword']",
            "submit": "button[type='submit']",
        }

        # search for local cookies
        if os.path.exists("cookies.pkl"):
            # if cookies are found load them
            with open("cookies.pkl", "rb") as file:
                cookies = pickle.load(file)
            return self.__load_cookies__(cookies)

        # if cookies doesn't exists perform login
        username = self.get_elem(selectors["username"])
        username.send_keys(self.username)

        password = self.get_elem(selectors["password"])
        password.send_keys(self.password)

        self.click_js(selectors["submit"])

        # store cookies
        cookies = self.get_browser().get_cookies()
        with open("cookies.pkl", "wb") as file:
            pickle.dump(cookies, file)

    def __load_cookies__(self, cookies) -> None:
        """Load cookies into the current session."""
        for cookie in cookies:
            self.driver.add_cookie(cookie)

        self.set_page("https://www.boostingfactory.com/profile")

    def __loop_orders__(self) -> None:
        """Loop through orders and accept them."""

        selectors = {
            "orders": "div#ongoingOrders div.single-order",
            "order_button": "a",
            "order_title": "h3",
        }

        orders = self.get_elems(selectors["orders"])

        for order in range(0, len(orders)):
            title = self.get_text(orders[order], selectors["order_title"])
            print(f"Accepting {title}")

            self.click_js(selectors["order_button"])

    def automate_orders(self) -> None:
        """automate accepting orders."""

        selectors = {
            "current_orders": "a[href='#ongoingOrders']",
        }

        self.__login__()

        # Select 'Current order' tab
        self.click_js(selectors["current_orders"])

        # Loop available orders and automatic accept them.
        self.__loop_orders__()
