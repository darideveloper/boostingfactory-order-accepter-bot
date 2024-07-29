from time import sleep
from rich import print

from libs.web_scraping import WebScraping


class FactoryScraper():
    def __init__(
        self,
        scraper: WebScraping,
    ) -> None:
        """starts chrome and initializes the scraper

        args:
            scraper: (WebScraping) instance of the scraper
        """
        
        self.scraper = scraper
        
        self.extracted_orders = {}
        
        self.home_page = "https://www.boostingfactory.com/profile"
        
    def __load_page__(self):
        """ Load main page """
        
        self.scraper.set_page(self.home_page)
        sleep(5)
        self.scraper.refresh_selenium()

    def loop_orders(self, order_ids: list) -> None:
        """Loop through orders and stores it to be processed later.
        
        Args:
            order_ids: (list) list of order ids
        """
        
        print("\nLooping through orders...")
        
        self.__load_page__()

        selectors = {
            "orders_tab": ".orders .nav.nav-tabs > li:first-child a",
            "orders": "div#availableOrders .orders-preloader + div",
            "order_button": "div#availableOrders div.single-order' \
                '.order-detail-btn .btn-for-bright",
            "order_link": "a",
            "order_id": "h3 + span",
            "order_accept": "button.btn.order-accept-btn.btn-for-bright",
            "order_ok": ".answer-btn",
        }
        
        # Set zoom to 50%
        self.scraper.zoom(50)

        # Move to orders tab
        self.scraper.click_js(selectors["orders_tab"])
        sleep(2)
        self.scraper.refresh_selenium()

        orders = self.scraper.get_elems(selectors["orders"])
        
        # Save page html
        with open("orders.html", "w", encoding="utf-8") as file:
            file.write(self.scraper.driver.page_source)
            
        # Save page screenshot
        self.scraper.screenshot("orders.png")

        orders_accepted = 0
        for order in range(0, len(orders)):

            # Validate order title
            selector_order = f"{selectors['orders']}:nth-child({(order + 1) * 2})"
            selector_id = f"{selector_order} {selectors['order_id']}"
            order_id_date = self.scraper.get_elem(selector_id).text
            
            order_id_parts = order_id_date.split(" - ")
            order_id = order_id_parts[-1]
            order_id = order_id.replace("#", "").strip()
            
            # DEBUG: Validte order ids
            if order_id not in order_ids:
                print(f"Order {order_id} not in valid order ids")
                continue

            # Accept order
            self.scraper.click_js(f"{selector_order} {selectors['order_accept']}")
            self.scraper.refresh_selenium()
            self.scraper.click_js(f"{selectors['order_ok']}")

            print(f"Order {order_id} accepted")
            orders_accepted += 1

        print(f"Total orders accepted: {orders_accepted}")
        
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
