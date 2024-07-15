from time import sleep
from rich import print

from libs.web_scraping import WebScraping


class FactoryScraper():
    def __init__(
        self,
        keywords: list,
        scraper: WebScraping,
    ) -> None:
        """starts chrome and initializes the scraper

        args:
            keywords: (list, str) filter titles for the targeted orders.
            scraper: (WebScraping) instance of the scraper
        """
        
        self.scraper = scraper

        # Title filter
        self.keywords = keywords

        self.extracted_orders = {}
        
        self.home_page = "https://www.boostingfactory.com/profile"
        
    def __load_page__(self):
        """ Load main page """
        
        self.scraper.set_page(self.home_page)
        sleep(5)
        self.scraper.refresh_selenium()

    def loop_orders(self) -> None:
        """Loop through orders and stores it to be processed later."""
        
        print("\nLooping through orders...")
        
        self.__load_page__()

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
        
    def validate_login(self):
        """ Validate if user is logged in """
        
        print("Validating Boostingfactory login...")
                
        self.__load_page__()
        current_url = self.scraper.driver.current_url
        if "/login" in current_url:
            print("Boostingfactory not logged in. Login again in Chrome.")
            quit()
            
        print("Logged in Boostingfactory.")
        sleep(5)
        self.scraper.refresh_selenium()
