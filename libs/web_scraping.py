import json
import logging
import os
import time
import zipfile

from selenium import webdriver
from selenium.common.exceptions import (NoSuchElementException,
                                        NoSuchFrameException, TimeoutException)
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

current_file = os.path.basename(__file__)


class WebScraping ():
    """
    Class to manage and configure web browser
    """

    service = None
    options = None

    def __init__(self, headless=False, time_out=0,
                 proxy_server="", proxy_port="", proxy_user="", proxy_pass="",
                 chrome_folder="", user_agent=False,
                 download_folder="", extensions=[], incognito=False, experimentals=True,
                 start_killing=False, start_openning: bool = True, width: int = 1280,
                 height: int = 720, mute: bool = True):
        """ Constructor of the class

        Args:
            headless (bool, optional): Hide (True) or Show (False) the google chrome window. Defaults to False.
            time_out (int, optional): Wait time to load each page. Defaults to 0.
            proxy_server (str, optional): Proxy server or host to use in the window. Defaults to "".
            proxy_port (str, optional): Proxy post to use in the window. Defaults to "".
            proxy_user (str, optional): Proxy user to use in the window. Defaults to "".
            proxy_pass (str, optional): Proxy password to use in the window. Defaults to "".
            chrome_folder (str, optional): folder with user google chrome data. Defaults to "".
            user_agent (bool, optional): user agent to setup to chrome. Defaults to False.
            download_folder (str, optional): Default download folder. Defaults to "".
            extensions (list, optional): Paths of extensions in format .crx, to install. Defaults to [].
            incognito (bool, optional): Open chrome in incognito mode. Defaults to False.
            experimentals (bool, optional): Activate the experimentals options. Defaults to True.
            start_killing (bool, optional): Kill chrome process before start. Defaults to False.
            start_openning (bool, optional): Open chrome window before start. Defaults to True.
            width (int, optional): Width of the window. Defaults to 1280.
            height (int, optional): Height of the window. Defaults to 720.
            mute (bool, optional): Mute the audio of the window. Defaults to True.
        """
        # Initialize logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        # Create console handler and set level to debug
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        self.logger.addHandler(ch)

        self.basetime = 1

        # variables of class
        self.current_folder = os.path.dirname(__file__)
        self.__headless__ = headless
        self.__proxy_server__ = proxy_server
        self.__proxy_port__ = proxy_port
        self.__proxy_user__ = proxy_user
        self.__proxy_pass__ = proxy_pass
        self.__pluginfile__ = os.path.join(self.current_folder, 'proxy_auth_plugin.zip')
        self.__chrome_folder__ = chrome_folder
        self.__user_agent__ = user_agent
        self.__download_folder__ = download_folder
        self.__extensions__ = extensions
        self.__incognito__ = incognito
        self.__experimentals__ = experimentals
        self.__start_openning__ = start_openning
        self.__width__ = width
        self.__height__ = height
        self.__mute__ = mute

        self.__web_page__ = None

        # Kill chrome from terminal
        if start_killing:
            print("\nTry to kill chrome...")
            windows = 'taskkill /IM "chrome.exe" /F > nul 2>&1'
            linux = "pkill -9 -f chrome > /dev/null 2>&1"

            if os.name == "nt":
                os.system(windows)
            else:
                os.system(linux)
            print("Ok\n")

        # Create and instance of the web browser
        if self.__start_openning__:
            self.__set_browser_instance__()

        # Get current file name
        self.current_file = os.path.basename(__file__)

        # Set time out
        if time_out > 0:
            self.driver.set_page_load_timeout(time_out)

    def set_cookies(self, cookies: list):
        """ Get list of cookies, formatted, from 'cookies.json' file

        Args:
            cookies (list): cookies generated by 'EditThisCookie' extension
        """

        # Format cookies
        cookies_formatted = []
        for cookie in cookies:

            # rename expiration date
            if "expirationDate" in cookie:
                cookie["expiry"] = int(cookie["expirationDate"])
                del cookie["expirationDate"]

            cookies_formatted.append(cookie)

        for cookie in cookies_formatted:
            try:
                self.driver.add_cookie(cookie)
            except Exception:
                pass

    def save_cookies(self, cookies):
        with open("cookies.json", "w") as file:
            file.write(json.dumps(cookies))

    def __set_browser_instance__(self):
        """
        Open and configure browser
        """

        # Disable logs
        os.environ['WDM_LOG_LEVEL'] = '0'
        os.environ['WDM_PRINT_FIRST_LINE'] = 'False'

        # Configure browser
        if not WebScraping.options:

            WebScraping.options = webdriver.ChromeOptions()
            WebScraping.options.add_argument('--no-sandbox')
            WebScraping.options.add_argument('--start-maximized')
            WebScraping.options.add_argument('--output=/dev/null')
            WebScraping.options.add_argument('--log-level=3')
            WebScraping.options.add_argument("--disable-notifications")
            WebScraping.options.add_argument("--disable-infobars")
            WebScraping.options.add_argument("--safebrowsing-disable-download-protection")

            WebScraping.options.add_argument("--disable-dev-shm-usage")
            WebScraping.options.add_argument("--disable-renderer-backgrounding")
            WebScraping.options.add_argument("--disable-background-timer-throttling")
            WebScraping.options.add_argument("--disable-backgrounding-occluded-windows")
            WebScraping.options.add_argument("--disable-client-side-phishing-detection")
            WebScraping.options.add_argument("--disable-crash-reporter")
            WebScraping.options.add_argument("--disable-oopr-debug-crash-dump")
            WebScraping.options.add_argument("--no-crash-upload")
            WebScraping.options.add_argument("--disable-gpu")
            WebScraping.options.add_argument("--disable-extensions")
            WebScraping.options.add_argument("--disable-low-res-tiling")
            WebScraping.options.add_argument("--log-level=3")
            WebScraping.options.add_argument("--silent")

            ''' Hardcoded for testing purposes '''
            WebScraping.options.add_experimental_option("detach", True)

            # Experimentals
            if self.__experimentals__:
                WebScraping.options.add_experimental_option(
                    'excludeSwitches', ['enable-logging', "enable-automation"])
                WebScraping.options.add_experimental_option('useAutomationExtension', False)

            # screen size
            WebScraping.options.add_argument(f"--window-size={self.__width__},{self.__height__}")

            # headless mode
            if self.__headless__:
                WebScraping.options.add_argument("--headless=new")

            if self.__mute__:
                WebScraping.options.add_argument("--mute-audio")

            # Set chrome folder
            if self.__chrome_folder__:
                WebScraping.options.add_argument(f"--user-data-dir={self.__chrome_folder__}")

            # Set default user agent
            if self.__user_agent__:
                WebScraping.options.add_argument
                \
                '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                \
                '(KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'

            if self.__download_folder__:
                prefs = {"download.default_directory": f"{self.__download_folder__}",
                         "download.prompt_for_download": "false",
                         'profile.default_content_setting_values.automatic_downloads': 1,
                         'profile.default_content_settings.popups': 0,
                         "download.directory_upgrade": True,
                         "plugins.always_open_pdf_externally": True,
                         "plugins.plugins_list": [{"enabled": False, "name": "Chrome PDF Viewer"}],
                         'download.extensions_to_open': 'xml',
                         'safebrowsing.enabled': True
                         }

                WebScraping.options.add_experimental_option("prefs", prefs)

            if self.__extensions__:
                for extension in self.__extensions__:
                    WebScraping.options.add_extension(extension)

            if self.__incognito__:
                WebScraping.options.add_argument("--incognito")

            if self.__experimentals__:
                WebScraping.options.add_argument(
                    "--disable-blink-features=AutomationControlled")

        # Set proxy without autentication
        if (self.__proxy_server__ and self.__proxy_port__
                and not self.__proxy_user__ and not self.__proxy_pass__):

            proxy = f"{self.__proxy_server__}:{self.__proxy_port__}"
            WebScraping.options.add_argument(f"--proxy-server={proxy}")

        # Set proxy with autentification
        # seleniumwire_options = {}
        if (self.__proxy_server__ and self.__proxy_port__
                and self.__proxy_user__ and self.__proxy_pass__):

            self.__create_proxy_extesion__()
            WebScraping.options.add_extension(self.__pluginfile__)

        # Autoinstall driver with selenium
        if not WebScraping.service:
            WebScraping.service = Service()

        # Auto download driver
        self.driver = webdriver.Chrome(
            service=WebScraping.service,
            options=WebScraping.options
        )

    def __create_proxy_extesion__(self):
        """Create a proxy chrome extension"""

        # plugin data
        manifest_json = """
        {
            "version": "1.0.0",
            "manifest_version": 2,
            "name": "Chrome Proxy",
            "permissions": [
                "proxy",
                "tabs",
                "unlimitedStorage",
                "storage",
                "<all_urls>",
                "webRequest",
                "webRequestBlocking"
            ],
            "background": {
                "scripts": ["background.js"]
            },
            "minimum_chrome_version":"22.0.0"
        }
        """

        background_js = """
        var config = {
                mode: "fixed_servers",
                rules: {
                singleProxy: {
                    scheme: "http",
                    host: "%s",
                    port: parseInt(%s)
                },
                bypassList: ["localhost"]
                }
            };

        chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

        function callbackFn(details) {
            return {
                authCredentials: {
                    username: "%s",
                    password: "%s"
                }
            };
        }

        chrome.webRequest.onAuthRequired.addListener(
                    callbackFn,
                    {urls: ["<all_urls>"]},
                    ['blocking']
        );
        """ % (self.__proxy_server__, self.__proxy_port__, self.__proxy_user__, self.__proxy_pass__)

        # Compress file
        with zipfile.ZipFile(self.__pluginfile__, 'w') as zp:
            zp.writestr("manifest.json", manifest_json)
            zp.writestr("background.js", background_js)

    def end_browser(self):
        if self.driver is not None:
            self.driver.quit()
            self.driver = None

    def __create_proxy_extension__(self):
        manifest_json = """
        {
            "version": "1.0.0",
            "manifest_version": 2,
            "name": "Chrome Proxy",
            "permissions": [
                "proxy",
                "tabs",
                "unlimitedStorage",
                "storage",
                "<all_urls>",
                "webRequest",
                "webRequestBlocking"
            ],
            "background": {
                "scripts": ["background.js"]
            },
            "minimum_chrome_version":"22.0.0"
        }
        """

        background_js = """
        var config = {
                mode: "fixed_servers",
                rules: {
                singleProxy: {
                    scheme: "http",
                    host: "%s",
                    port: parseInt(%s)
                },
                bypassList: ["localhost"]
                }
            };

        chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

        function callbackFn(details) {
            return {
                authCredentials: {
                    username: "%s",
                    password: "%s"
                }
            };
        }

        chrome.webRequest.onAuthRequired.addListener(
                    callbackFn,
                    {urls: ["<all_urls>"]},
                    ['blocking']
        );
        """ % (self.__proxy_server__, self.__proxy_port__, self.__proxy_user__, self.__proxy_pass__)

        with zipfile.ZipFile(self.__pluginfile__, 'w') as zp:
            zp.writestr("manifest.json", manifest_json)
            zp.writestr("background.js", background_js)

    def handle_browser_error(self, error):
        if "Selenium session deleted" in str(error):
            self.logger.error(f"Browser instance crashed: {error}")
            self.end_browser()
            self.__set_browser_instance__()
        elif "connection refused" in str(error):
            self.logger.error(f"Connection refused error: {error}")
        else:
            self.logger.error(f"Unhandled browser error: {error}")

    def __reload_browser__(self):
        """
        Close the current instance of the web browser and reload in the same page
        """
        self.end_browser()
        self.__set_browser_instance__()
        self.driver.get(self.__web_page__)

    def get_browser(self):
        """
        Return the current instance of web browser
        """
        return self.driver

    def screenshot(self, base_name):
        """
        Take a screenshot of the current browser window
        """
        if str(base_name).endswith(".png"):
            file_name = base_name
        else:
            file_name = f"{base_name}.png"

        self.driver.save_screenshot(file_name)

    def full_screenshot(self, path: str):
        original_size = self.driver.get_window_size()
        required_width = self.driver.execute_script(
            'return document.body.parentNode.scrollWidth')
        required_height = self.driver.execute_script(
            'return document.body.parentNode.scrollHeight')
        self.driver.set_window_size(required_width, required_height)
        self.screenshot(path)
        self.driver.set_window_size(
            original_size['width'], original_size['height'])

    def send_data(self, selector, data):
        """
        Send data to specific input fill
        """
        elem = self.driver.find_element(By.CSS_SELECTOR, selector)
        elem.send_keys(data)

    def click(self, selector):
        """
        Send click to specific element in the page
        """
        if isinstance(selector, str):
            elem = self.driver.find_element(By.CSS_SELECTOR, selector)
            elem.click()
        else:
            selector.click()

    def wait_load(self, selector, time_out=10, refresh_back_tab=-1):
        """
        Wait for a specific element to load on the page.

        Args:
            selector (str): CSS selector for the element to wait for.
            time_out (int, optional): Maximum time to wait in seconds. Defaults to 10.
            refresh_back_tab (int, optional): Number of times to refresh the page
            or go back (-1 means no action). Defaults to -1.
        """
        total_time = 0

        while total_time < time_out:
            try:
                elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                elem.text
                return  # Element found, exit the loop
            except NoSuchElementException:
                # Element not found, continue waiting
                total_time += 1

                # Refresh the page or go back if specified
                if refresh_back_tab != -1:
                    self.refresh_selenium(back_tab=refresh_back_tab)
                else:
                    time.sleep(self.basetime)

        # If the loop completes without finding the element, log an error
        self.logger.error(f"Timed out: Element '{selector}' not found on the page.")

    def implicit_wait(self, selector):
        try:
            WebDriverWait(self.get_browser(), 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
        except Exception:
            raise Exception("Time out exeded. The element {} is until in the page".format(selector))

    def wait_die(self, selector, time_out=10):
        """
        Wait for an element to vanish from the page.

        Args:
            selector (str): CSS selector for the element to wait for.
            time_out (int, optional): Maximum time to wait in seconds. Defaults to 10.
        """
        try:
            # Wait until the element vanishes from the page
            WebDriverWait(self.driver, time_out).until_not(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
        except TimeoutException:
            # If the element is still present after the timeout, log an error
            self.logger.error(f"Timed out: Element '{selector}' is still on the page.")
            raise

    def get_text(self, selector, item: str = None):
        """
        Return text for a specific element on the page.

        Args:
            selector (WebElement or str): WebElement or CSS selector for the element.
            item (str, optional): CSS selector for a nested element. Defaults to None.

        Returns:
            str or None: Text of the element if found, otherwise None.
        """
        try:
            if isinstance(selector, str):
                elem = self.driver.find_element(By.CSS_SELECTOR, selector)
            else:
                elem = selector

            if item is not None:
                elem = elem.find_element(By.CSS_SELECTOR, item)

            return elem.text
        except NoSuchElementException:
            error_message = "Element "
            if isinstance(selector, str):
                error_message += f"'{selector}'"
            else:
                error_message += f"'{selector.tag_name}'"

            if item:
                error_message += f" (nested element '{item}')"

            error_message += " not found on the page."

            self.logger.error(error_message)
            return None

    def get_texts(self, selector, item: str = None):
        """
        Return a list of text for a specific selector.

        Args:
            selector (str): CSS selector for the elements.
            item (str, optional): CSS selector for a nested element. Defaults to None.

        Returns:
            list: List of texts of the elements if found, otherwise an empty list.
        """
        texts = []

        try:
            if isinstance(selector, str):
                elems = self.driver.find_elements(By.CSS_SELECTOR, selector)
            else:
                elems = [selector]

            for elem in elems:
                try:
                    if item is not None:
                        nested_elem = elem.find_element(By.CSS_SELECTOR, item)
                        texts.append(nested_elem.text)
                    else:
                        texts.append(elem.text)
                except NoSuchElementException:
                    error_message = f"Element '{elem}'"
                    if item:
                        error_message += f" (nested element '{item}')"
                    error_message += " not found on the page."
                    self.logger.error(error_message)
        except NoSuchElementException:
            self.logger.error(f"No elements found for selector '{selector}' on the page.")

        return texts

    def get_attrib(self, attrib_name, selector, item: str = None):
        """
        Return the value of a specific attribute from an element on the page.

        Args:
            attrib_name (str): Name of the attribute to retrieve.
            selector (str): CSS selector for the element.
            item (str, optional): CSS selector for a nested element. Defaults to None.

        Returns:
            str or None: Value of the specified attribute if found, otherwise None.
        """
        try:
            if item is None:
                elem = self.driver.find_element(By.CSS_SELECTOR, selector)
            else:
                elem = selector.find_element(By.CSS_SELECTOR, item)

            return elem.get_attribute(attrib_name)
        except NoSuchElementException:
            error_message = f"Element '{selector}'"
            if item:
                error_message += f" (nested element '{item}')"
            error_message += " not found on the page."
            self.logger.error(error_message)
            return None

    def get_attribs(self, attrib_name, selector, item: str = None, allow_duplicates=True, allow_empty=True):
        """
        Return the attribute values from specific elements on the page.

        Args:
            attrib_name (str): Name of the attribute to retrieve.
            selector (str): CSS selector for the elements.
            item (str, optional): CSS selector for a nested element. Defaults to None.
            allow_duplicates (bool, optional): Flag to allow duplicate attribute values. Defaults to True.
            allow_empty (bool, optional): Flag to allow empty attribute values. Defaults to True.

        Returns:
            list: List of attribute values of the elements if found, otherwise an empty list.
        """
        attributes = []
        elems = self.driver.find_elements(By.CSS_SELECTOR, selector)

        for elem in elems:
            try:
                if item is not None:
                    elem = elem.find_element(By.CSS_SELECTOR, item)
                attribute = elem.get_attribute(attrib_name)

                # Skip duplicates if not allowed
                if not allow_duplicates and attribute in attributes:
                    continue

                # Skip empty results if not allowed
                if not allow_empty and attribute.strip() == "":
                    continue

                attributes.append(attribute)

            except NoSuchElementException:
                self.logger.error(f"Element '{selector}' (nested element '{item}') not found on the page.")
                continue

        return attributes

    def set_attrib(self, selector, attrib_name, attrib_value):
        """
        Set the value of a specific attribute for an element on the page.

        Args:
            selector (str): CSS selector for the element.
            attrib_name (str): Name of the attribute to set.
            attrib_value (str): Value to set for the attribute.
        """
        try:
            elem = self.driver.find_element(By.CSS_SELECTOR, selector)
            self.driver.execute_script(
                f"arguments[0].setAttribute('{attrib_name}', '{attrib_value}');", elem)
        except NoSuchElementException:
            self.logger.error(f"Element '{selector}' not found on the page.")

    def get_elem(self, selector, item: str = None):
        """
        Return a specific element on the page.

        Args:
            selector (WebElement or str): WebElement or CSS selector for the element.
            item (str, optional): CSS selector for a nested element. Defaults to None.

        Returns:
            WebElement or None: WebElement object representing the found element
            or None if not found.
        """
        try:
            if isinstance(selector, str):
                elem = self.driver.find_element(By.CSS_SELECTOR, selector)
            else:
                elem = selector

            if item is not None:
                elem = elem.find_element(By.CSS_SELECTOR, item)

            return elem
        except NoSuchElementException:
            error_message = "Element "
            if isinstance(selector, str):
                error_message += f"'{selector}'"
            else:
                error_message += f"'{selector.tag_name}'"

            if item:
                error_message += f" (nested element '{item}')"

            error_message += " not found on the page."

            self.logger.error(error_message)
            return None

    def get_elems(self, selector, item: str = None):
        """
        Return a list of specific elements on the page.

        Args:
            selector (str): CSS selector for the elements.
            item (str, optional): CSS selector for a nested element. Defaults to None.

        Returns:
            list: List of WebElement objects representing the found elements.
        """
        try:
            elems = self.driver.find_elements(By.CSS_SELECTOR, selector)
            if item is not None:
                elems = [elem.find_element(By.CSS_SELECTOR, item) for elem in elems]
            return elems
        except NoSuchElementException:
            error_message = "Elements "
            error_message += f"'{selector}'"
            if item:
                error_message += f" (nested element '{item}')"
            error_message += " not found on the page."
            self.logger.error(error_message)
            return []

    def open_page(self, web_page, new_tab=False):
        """
        Open a web page using JavaScript, either in the current tab or a new tab.

        Args:
            web_page (str): The URL of the web page to open.
            new_tab (bool, optional): Whether to open the page in a new tab. Defaults to False.
        """
        self.__web_page__ = web_page
        try:
            if new_tab:
                script = f'window.open("{web_page}");'
            else:
                script = f'window.open("{web_page}").focus();'

            self.driver.execute_script(script)
        except Exception as e:
            self.logger.error(f"Error opening page: {e}")

    def set_page(self, web_page, time_out=0, break_time_out=False):
        """
        Update the web page in the browser
        """
        try:
            # Save the web page URL
            self.__web_page__ = web_page

            # Set the page load timeout if greater than 0
            if time_out > 0:
                self.driver.set_page_load_timeout(time_out)

            # Load the web page
            self.driver.get(self.__web_page__)

        # Catch any exceptions that occur during page load
        except Exception as err:
            self.logger.error(err)

            # Raise an exception if break_time_out is True
            if break_time_out:
                self.logger.error(f"Timeout occurred while loading page: {web_page}")

            # Otherwise, ignore the error and continue
            else:
                try:
                    # Attempt to stop the page loading
                    self.driver.execute_script("window.stop();")
                except Exception as e:
                    self.logger.error(f"Error opening page: {e}")

    def set_page_js(self, web_page, new_tab=False):
        """
        Open a web page using JavaScript, either in the current tab or a new tab.

        Args:
            web_page (str): The URL of the web page to open.
            new_tab (bool, optional): Whether to open the page in a new tab. Defaults to False.
        """
        self.__web_page__ = web_page
        try:
            if new_tab:
                script = f'window.open("{web_page}");'
            else:
                script = f'window.open("{web_page}").focus();'

            self.driver.execute_script(script)
        except Exception as e:
            self.logger.error(f"Error opening page: {e}")

    def click_js(self, selector, item: str = None):
        """
        Send a click using JavaScript, useful for hidden elements.

        Args:
            selector (str): CSS selector of the element to click.
        """
        try:
            if isinstance(selector, str):
                elem = self.driver.find_element(By.CSS_SELECTOR, selector)
            else:
                elem = selector

            if item is not None:
                elem = elem.find_element(By.CSS_SELECTOR, item)

            self.driver.execute_script("arguments[0].click();", elem)
        except NoSuchElementException as e:
            self.logger.error(f"Element '{selector}' not found: {e}")

    def select_drop_down_index(self, selector, index):
        """
        Select a specific element (by index) in a drop-down element.

        Args:
            selector (str): CSS selector of the drop-down element.
            index (int): Index of the option to select.
        """
        try:
            select_elem = Select(self.get_elem(selector))
            select_elem.select_by_index(index)
        except NoSuchElementException as e:
            self.logger.error(f"Element '{selector}' not found: {e}")
        except IndexError as e:
            self.logger.error(f"Index {index} is out of range: {e}")

    def select_drop_down_text(self, selector, text):
        """
        Select a value in a drop-down element by its visible text.

        Args:
            selector (str): CSS selector of the drop-down element.
            text (str): Visible text of the option to select.
        """
        try:
            select_elem = Select(self.get_elem(selector))
            select_elem.select_by_visible_text(text)
        except NoSuchElementException as e:
            self.logger.error(f"Element '{selector}' not found: {e}")
        except NoSuchElementException as e:
            self.logger.error(f"Option with text '{text}' not found in drop-down '{selector}': {e}")

    def go_bottom(self, selector: str = "body"):
        """
        Scroll to the bottom of the page.

        Args:
            selector (str, optional): CSS selector of the element to scroll within. Defaults to "body".
        """
        try:
            elem = self.driver.find_element(By.CSS_SELECTOR, selector)
            elem.send_keys(Keys.CONTROL + Keys.END)
        except NoSuchElementException as e:
            self.logger.error(f"Element '{selector}' not found: {e}")

    def go_top(self, selector: str = "body"):
        """
        Scroll to the top of the page.

        Args:
            selector (str, optional): CSS selector of the element to scroll within. Defaults to "body".
        """
        try:
            elem = self.driver.find_element(By.CSS_SELECTOR, selector)
            elem.send_keys(Keys.CONTROL + Keys.HOME)
        except NoSuchElementException as e:
            self.logger.error(f"Element '{selector}' not found: {e}")

    def go_down(self, selector: str = "body"):
        """
        Scroll down the page.

        Args:
            selector (str, optional): CSS selector of the element to scroll within. Defaults to "body".
        """
        try:
            elem = self.driver.find_element(By.CSS_SELECTOR, selector)
            elem.send_keys(Keys.PAGE_DOWN)
        except NoSuchElementException as e:
            self.logger.error(f"Element '{selector}' not found: {e}")

    def go_up(self, selector: str = "body"):
        """
        Scroll up the page.

        Args:
            selector (str, optional): CSS selector of the element to scroll within. Defaults to "body".
        """
        try:
            elem = self.driver.find_element(By.CSS_SELECTOR, selector)
            elem.send_keys(Keys.PAGE_UP)
        except NoSuchElementException as e:
            self.logger.error(f"Element '{selector}' not found: {e}")

    def infinite_scroll(self, selector, button=None):
        """
        Scroll down infinitely until reaching the bottom of the page or a specified button.

        Args:
            selector (str): CSS selector of the element to scroll within.
            button (str, optional): CSS selector of a button to click instead of scrolling. Defaults to None.
        """
        # Scroll down the whole page to load all results in the D.O.M
        if button is None:
            while True:
                try:
                    # Scroll down
                    self.go_down(selector)

                    # Give some time to load new items
                    time.sleep(5)

                except NoSuchElementException as e:
                    self.logger.error(f"Element '{selector}' not found: {e}")
                    break
        else:
            # Pending: implement functionality when infinite scroll requires clicking a button
            self.logger.warning("Functionality for infinite scroll with button click is not yet implemented")

    def switch_to_main_frame(self):
        """
        Switch to the main content of the page.
        """
        try:
            self.driver.switch_to.default_content()
        except NoSuchFrameException as e:
            self.logger.error(f"Failed to switch to main frame: {e}")

    def switch_to_frame(self, frame_selector):
        """
        Switch to iframe inside the main content.
        """
        try:
            frame = self.get_elem(frame_selector)
            self.driver.switch_to.frame(frame)
        except NoSuchFrameException as e:
            self.logger.error(f"Failed to switch to frame '{frame_selector}': {e}")

    def open_tab(self):
        """
        Create a new empty tab in the browser.
        """
        self.driver.execute_script("window.open('','_blank');")

    def close_tab(self):
        """
        Close the current tab in the browser.
        """
        self.driver.close()

    def switch_to_tab(self, number):
        """
        Switch to a specific tab by its index.

        Args:
            number (int): Index of the tab to switch to.
        """
        windows = self.driver.window_handles
        self.driver.switch_to.window(windows[number])

    def refresh_selenium(self, time_units=1, back_tab=0):
        """
        Refresh the Selenium data by creating and closing a new tab.

        Args:
            time_units (int, optional): Number of time units to wait after refreshing. Defaults to 1.
            back_tab (int, optional): Index of the tab to switch back to after refreshing. Defaults to 0.
        """

        # Open new tab and switch to it
        self.open_tab()
        self.switch_to_tab(len(self.driver.window_handles) - 1)

        # Wait for specified time units
        time.sleep(self.basetime * time_units)

        # Close the new tab and switch back to the specified tab
        self.close_tab()
        self.switch_to_tab(back_tab)

        # Wait for specified time units
        time.sleep(self.basetime * time_units)

    def save_page(self, file_html):
        """
        Save the current page source to a local file.

        Args:
            file_html (str): Name of the file to save the page source.
        """
        try:
            page_html = self.driver.page_source
            current_folder = os.path.dirname(__file__)
            page_file = open(os.path.join(current_folder, file_html), "w", encoding='utf-8')
            page_file.write(page_html)
            page_file.close()
        except Exception as e:
            self.logger.error(f"Failed to save page: {e}")

    def zoom(self, percentage=50):
        """
        Adjust the page zoom using JavaScript.

        Args:
            percentage (int, optional): Percentage value for zoom. Defaults to 50.
        """
        try:
            script = f"document.body.style.zoom='{percentage}%'"
            self.driver.execute_script(script)
        except Exception as e:
            self.logger.error(f"Failed to adjust page zoom: {e}")

    def kill(self):
        """
        Close all tabs and end the browser session.
        """
        try:
            tabs = self.driver.window_handles
            for _ in tabs:
                self.switch_to_tab(0)
                self.end_browser()
        except Exception as e:
            self.logger.error(f"Failed to close all tabs: {e}")

    def scroll(self, selector, scroll_x, scroll_y):
        """
        Scroll horizontally or vertically within a specific element on the page.

        Args:
            selector (str): CSS selector for the element.
            scroll_x (int): The horizontal scroll position.
            scroll_y (int): The vertical scroll position.
        """
        try:
            elem = self.get_elem(selector)
            self.driver.execute_script(
                "arguments[0].scrollTo(arguments[1], arguments[2])",
                elem,
                scroll_x,
                scroll_y
            )
        except Exception as e:
            self.logger.error(f"Failed to scroll: {e}")

    def set_local_storage(self, key: str, value: str):
        """
        Set a value in the local storage using JavaScript.

        Args:
            key (str): The key for the local storage.
            value (str): The value to be stored.
        """
        try:
            script = f"window.localStorage.setItem('{key}', '{value}')"
            self.driver.execute_script(script)
        except Exception as e:
            self.logger.error(f"Failed to set local storage: {e}")

    def remove_elems(self, selector: str):
        """
        Remove all elements with a specific CSS selector.

        Args:
            selector (str): CSS selector of the elements to remove.
        """
        try:
            script = f"document.querySelectorAll('{selector}').forEach(e => e.remove())"
            self.driver.execute_script(script)
        except Exception as e:
            self.logger.error(f"Failed to remove elements: {e}")
