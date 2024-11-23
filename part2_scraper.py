import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from dotenv import load_dotenv
import logging
import random
import os
import json
import time
from typing import List, Dict, Optional

# Load environment variables from .env file
load_dotenv()

# Setup Logging
logging.basicConfig(filename='selenium_scraper.log', level=logging.INFO, format='%(asctime)s - %(message)s')

# Environment variables
USERNAME = os.getenv("USER")
PASSWORD = os.getenv("PASSWORD")
BASE_URL = os.getenv("BASE_URL")
CHROME_DRIVER_PATH = os.getenv("CHROME_DRIVER_PATH")


# Initialize ChromeDriver with stealth options
def setup_driver() -> uc.Chrome:
    """Sets up and returns the Chrome WebDriver."""
    # Set up Chrome options
    options = Options()
    options.add_argument("--headless")  # Run in headless mode (no GUI)
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--incognito")
    options.add_argument("--disable-blink-features=AutomationControlled")  # Disable automation-related flags
    options.add_argument("--disable-extensions")  # Disable extensions that might reveal the bot
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-features=EnableImageLoading")

    # Initialize the WebDriver with undetected_chromedriver
    try:
        driver = uc.Chrome(options=options)
        logging.info("WebDriver initialized successfully.")
        return driver
    except WebDriverException as e:
        logging.error(f"Error initializing WebDriver: {e}")
        raise


# Login to the site and manage the session
def login(driver: uc.Chrome, url: str, username: str, password: str) -> bool:
    """Logs into the website and returns whether the login was successful."""
    try:
        logging.info(f"Opening login page: {url}")
        # Format the URL for Basic Authentication
        auth_url = f"https://{username}:{password}@{url.split('://')[1]}"
        logging.info(f"Accessing login URL: {auth_url}")
        driver.get(auth_url)

        # Wait for page to load
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        logging.info("Login successful or page loaded.")
        return True
    except TimeoutException:
        logging.error(f"Login page timed out. URL: {url}")
        return False
    except Exception as e:
        logging.error(f"Login failed: {e}")
        return False


# Function to scrape dynamically loaded data
def scrape_data(driver: uc.Chrome, base_url: str, max_pages: int = 5) -> List[Dict[str, str]]:
    """Scrapes data from a paginated catalogue and returns a list of books' details."""
    data: List[Dict[str, str]] = []
    page = 1
    consecutive_failures = 0  # Counter for consecutive page load failures

    while True:
        url = f"{base_url}/catalogue/page-{page}.html"
        driver.get(url)

        try:
            # Wait for dynamic content to load
            WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "product_pod")))
            logging.info(f"{url} loaded successfully.")

            # Reset consecutive failures on successful page load
            consecutive_failures = 0

            # Extract book data
            book_elements = driver.find_elements(By.CLASS_NAME, "product_pod")
            if not book_elements:
                logging.info("No more data found. Stopping scraper.")
                break

            for book in book_elements:
                try:
                    title = book.find_element(By.TAG_NAME, "h3").find_element(By.TAG_NAME, "a").get_attribute("title")
                    price = book.find_element(By.CLASS_NAME, "price_color").text
                    availability = book.find_element(By.CLASS_NAME, "instock").text.strip()
                    price = price.replace("\u00a3", "").strip()  # Clean the price by removing unwanted characters

                    data.append({
                        "name": title,
                        "price": price,
                        "availability": availability
                    })
                except NoSuchElementException as e:
                    logging.warning(f"Missing data in one book entry. Skipping. Error: {e}")
                    continue

            # Increment page number
            page += 1
            if max_pages and page > max_pages:
                logging.info("Reached the maximum number of pages.")
                break

            time.sleep(random.randint(1, 3))  # Random sleep to mimic human-like behavior

        except TimeoutException:
            logging.warning(f"Timeout occurred while loading page {page}.")
            consecutive_failures += 1
            if consecutive_failures >= 3:
                logging.warning("Failed to load 3 consecutive pages. Ending scraping.")
                break
        except Exception as e:
            logging.error(f"Error while scraping page {page}: {e}")
            break

    logging.info(f"Scraping complete. Total books scraped: {len(data)}")
    return data


# Improved WebDriver cleanup handling
def cleanup_driver(driver: Optional[uc.Chrome]) -> None:
    """Cleans up the WebDriver instance by closing open windows."""
    try:
        if driver and driver.window_handles:
            logging.info(f"Closing {len(driver.window_handles)} window(s)...")
            time.sleep(1.5)
            driver.quit()
            logging.info("WebDriver session closed.")
        else:
            logging.warning("No open windows or driver already closed.")
    except (OSError, TimeoutException) as e:
        logging.error(f"Error during cleanup: {e}")
    except Exception as e:
        logging.error("Unexpected error during cleanup", exc_info=True)


# Main function to execute the scraper
def main() -> None:
    driver: Optional[uc.Chrome] = None
    try:
        # Initialize WebDriver
        driver = setup_driver()

        # Login
        if not login(driver, BASE_URL, USERNAME, PASSWORD):
            logging.error("Login failed. Exiting...")
            return

        logging.info("Logged in successfully.")

        # Start scraping
        data = scrape_data(driver, BASE_URL, max_pages=5)  # Adjust max_pages if needed

        # Save data to a JSON file
        with open('scraped_data.json', 'w') as f:
            json.dump(data, f, indent=4)
        logging.info("Data saved successfully to 'scraped_data.json'.")

    except Exception as e:
        logging.error(f"Unexpected error during scraping process: {e}", exc_info=True)

    finally:
        if driver:
            cleanup_driver(driver)


if __name__ == "__main__":
    main()
