import logging
import random
import time
import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, TimeoutException
from typing import Optional, List


class WebDriverManagement:
    """
    A utility class to manage an authenticated WebDriver session with Chrome.

    This class is responsible for initializing the Chrome WebDriver with stealth options,
    logging into a website with HTTP Basic Authentication, and managing the session.
    """

    def __init__(self, username: str, password: str, base_url: str, proxies: List[str], user_agents: List[str]):
        """
        Initialize the WebDriverManagement instance.

        Args:
            username (str): The username for authentication.
            password (str): The password for authentication.
            base_url (str): The base URL for login.
            proxies (List[str]): A list of proxies to choose from.
            user_agents (List[str]): A list of user agents to choose from.
        """
        self.username = username
        self.password = password
        self.base_url = base_url
        self.proxies = proxies
        self.user_agents = user_agents
        self.driver: Optional[uc.Chrome] = None
        self.is_logged_in = False

    def _setup_driver(self) -> uc.Chrome:
        """
        Setup Chrome WebDriver with proxy, user-agent, and stealth options.

        Returns:
            uc.Chrome: The initialized WebDriver instance.

        Raises:
            WebDriverException: If the WebDriver cannot be initialized.
        """
        options = Options()
        options.add_argument("--headless")  # Run in headless mode (no GUI)
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--incognito")
        options.add_argument("--disable-blink-features=AutomationControlled")  # Disable automation flags
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-features=EnableImageLoading")

        # Select random proxy and user-agent
        random_proxy = random.choice(self.proxies)
        random_user_agent = random.choice(self.user_agents)

        options.add_argument(f'--proxy-server={random_proxy}')
        options.add_argument(f'--user-agent={random_user_agent}')

        try:
            driver = uc.Chrome(options=options)
            logging.info("WebDriver initialized successfully.")
            return driver
        except WebDriverException as e:
            logging.error(f"Error initializing WebDriver: {e}")
            raise  # Re-raise the exception for the caller to handle

    def _login(self) -> bool:
        """
        Attempt to log in using HTTP Basic Authentication.

        Returns:
            bool: True if login is successful, False otherwise.
        """
        if not self.username or not self.password:
            logging.error("Authentication credentials are missing (username or password).")
            return False

        try:
            # Format URL for Basic Authentication
            auth_url = f"https://{self.username}:{self.password}@{self.base_url.split('://')[1]}"
            logging.info(f"Accessing login URL: {auth_url}")

            # Wait for the page to load and check if the body is present
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

            logging.info("Login successful or page loaded.")
            return True
        except TimeoutException:
            logging.error(f"Login page timed out after waiting for: {self.base_url}")
            return False
        except Exception as e:
            logging.error(f"Login failed due to: {e}")
            return False

    def get_driver(self) -> uc.Chrome:
        """
        Get the WebDriver instance.

        If not already initialized, attempts to initialize the WebDriver and log in.

        Returns:
            uc.Chrome: The authenticated WebDriver instance.
        """
        if self.driver is None:
            logging.info("WebDriver not initialized. Initializing WebDriver...")
            self.driver = self._setup_driver()

        if not self.is_logged_in:
            logging.info("Session not authenticated. Attempting to log in...")
            if not self._login():
                logging.error("Failed to authenticate session. Returning unauthenticated WebDriver.")
            else:
                self.is_logged_in = True

        return self.driver

    def cleanup(self) -> None:
        """
        Clean up the WebDriver session by closing windows and quitting the driver.
        """
        try:
            if self.driver and self.driver.window_handles:
                logging.info(f"Closing {len(self.driver.window_handles)} window(s)...")
                time.sleep(1.5)  # Small delay before quitting
                self.driver.quit()
                logging.info("WebDriver session closed.")
            else:
                logging.warning("No open windows or driver already closed.")
        except (OSError, TimeoutException) as e:
            logging.error(f"Error during cleanup: {e}")
        except Exception as e:
            logging.error("Unexpected error during cleanup", exc_info=True)
        finally:
            self.driver = None  # Ensure driver is reset

    def quit(self):
        """End the WebDriver session."""
        self.cleanup()
        logging.info("WebDriver session ended.")
