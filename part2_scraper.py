import undetected_chromedriver as uc
from selenium.common.exceptions import TimeoutException, NoSuchElementException
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

from web_driver_management import WebDriverManagement

# Load environment variables from .env file
load_dotenv()

# Setup Logging
logging.basicConfig(filename='selenium_scraper.log', level=logging.INFO, format='%(asctime)s - %(message)s')

# Environment variables
USERNAME = os.getenv("USER")
PASSWORD = os.getenv("PASSWORD")
BASE_URL = os.getenv("BASE_URL")
CHROME_DRIVER_PATH = os.getenv("CHROME_DRIVER_PATH")

# Proxy and User-Agent settings
USER_AGENTS: List[str] = os.getenv("USER_AGENTS", "").split(';; ')
PROXIES: List[str] = os.getenv("PROXIES", "").split(',')


def process_book(book) -> Optional[Dict[str, str]]:
    """
    Extracts data from a book element.

    Args:
        book (WebElement): The book element to extract data from.

    Returns:
        Optional[Dict[str, str]]: A dictionary with book details or None if data is missing.
    """
    try:
        title = book.find_element(By.TAG_NAME, "h3").find_element(By.TAG_NAME, "a").get_attribute("title")
        price = book.find_element(By.CLASS_NAME, "price_color").text.replace("\u00a3", "").strip()
        availability = book.find_element(By.CLASS_NAME, "instock").text.strip()

        return {
            "name": title,
            "price": price,
            "availability": availability
        }
    except NoSuchElementException as e:
        logging.warning(f"Missing data in one book entry. Error: {e}")
        return None


def scrape_data(driver: uc.Chrome, base_url: str, max_pages: int = 5) -> List[Dict[str, str]]:
    """
    Scrapes paginated catalogue data and returns book details.

    Args:
        driver (uc.Chrome): The initialized WebDriver.
        base_url (str): The base URL to scrape from.
        max_pages (int): The maximum number of pages to scrape.

    Returns:
        List[Dict[str, str]]: A list of dictionaries containing book details.
    """
    data: List[Dict[str, str]] = []
    page = 1
    consecutive_failures = 0  # To track consecutive failed page loads

    while page <= max_pages:
        url = f"{base_url}/catalogue/page-{page}.html"
        driver.get(url)

        try:
            # Wait for page content to load
            WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "product_pod")))
            logging.info(f"Page {page} loaded successfully.")

            # Extract book data
            book_elements = driver.find_elements(By.CLASS_NAME, "product_pod")
            if not book_elements:
                logging.info("No more books found. Stopping scraper.")
                break

            for book in book_elements:
                book_data = process_book(book)
                if book_data:
                    data.append(book_data)

            # Increment page number and handle sleep
            page += 1
            time.sleep(random.randint(1, 3))

        except TimeoutException:
            logging.warning(f"Timeout while loading page {page}.")
            consecutive_failures += 1
            if consecutive_failures >= 3:
                logging.warning("3 consecutive page load failures. Ending scraping.")
                break
        except Exception as e:
            logging.error(f"Error while scraping page {page}: {e}")
            break

    logging.info(f"Scraping complete. Total books scraped: {len(data)}.")
    return data


def main() -> None:
    """
    Initializes WebDriver, scrapes data, and saves the results to a JSON file.
    """
    web_driver_manager = WebDriverManagement(USERNAME, PASSWORD, BASE_URL, PROXIES, USER_AGENTS)

    try:
        driver = web_driver_manager.get_driver()

        # Start scraping
        data = scrape_data(driver, BASE_URL, max_pages=5)

        # Save the scraped data to a JSON file
        with open('scraped_data.json', 'w') as f:
            json.dump(data, f, indent=4)
        logging.info("Data saved successfully to 'scraped_data.json'.")

    except Exception as e:
        logging.error(f"Unexpected error: {e}")

    finally:
        # Clean up the WebDriver session
        web_driver_manager.quit()


if __name__ == "__main__":
    main()
