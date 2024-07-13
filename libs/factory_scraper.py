from time import sleep
from rich import print

from libs.web_scraping import WebScraping


class FactoryScraper():
    def __init__(
        self,
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

        # Title filter
        self.keywords = keywords
        
        # Refresh time
        self.wait_time = wait_time

        self.extracted_orders = {}
        
        self.home_page = "https://www.boostingfactory.com/profile"

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
        
    def __validate_login__(self):
        """ Validate if user is logged in """
        
        self.scraper.set_page(self.home_page)
        current_url = self.scraper.driver.current_url
        if "/login" in current_url:
            print("You need to login in Discord.")
            input("Please login and press any key to continue...")
            
            # Try to load main pae again
            self.scraper.set_page(self.server_link)
            self.refresh_selenium()
            self.__validate_login__()
        else:
            print("Logged in Discord.")

    def automate_orders(self) -> None:
        """automate accepting orders."""
        
        self.validate_login()

        while True:

            # Loop available orders and accept by title
            self.__loop_orders__()

            # Wait 1 minute
            print(f"waiting {self.wait_time} milliseconds")
            sleep(self.wait_time / 1000)
