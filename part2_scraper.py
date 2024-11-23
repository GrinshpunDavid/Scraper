from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv
import logging
import random
import os
import json
import time

# Load environment variables from .env file
load_dotenv()

# Setup Logging
logging.basicConfig(filename='selenium_scraper.log', level=logging.INFO, format='%(asctime)s - %(message)s')

# Environment variables
USERNAME = os.getenv("USER")
PASSWORD = os.getenv("PASSWORD")
BASE_URL = os.getenv("BASE_URL")
LOGIN_URL = os.getenv("LOGIN_URL")  # JavaScript-heavy login URL
CHROME_DRIVER_PATH = os.getenv("CHROME_DRIVER_PATH", r"C:\WebDrivers\chromedriver.exe")


# Initialize ChromeDriver with options
def setup_driver():
    options = Options()
    options.add_argument("--headless")  # Run in headless mode (no GUI)
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--incognito")
    driver = webdriver.Chrome(options=options)
    return driver


# Login to the site and manage the session
def login(driver, url, username, password):
    try:
        logging.info(f"Opening login page: {url}")
        # Format the URL for Basic Authentication
        auth_url = f"https://{username}:{password}@{url.split('://')[1]}"
        logging.info(auth_url)
        driver.get(auth_url)

        # Check if the page loaded correctly
        logging.info("Login successful or page loaded.")
        return True
    except Exception as e:
        logging.error(f"Login failed: {e}")
        return False


# Function to scrape dynamically loaded data
def scrape_data(driver, base_url, max_pages=5):
    data = []
    page = 1

    while True:
        url = f"{base_url}/catalogue/page-{page}.html"
        driver.get(url)

        try:
            # Wait for dynamic content to load
            WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "product_pod")))
            logging.info(f"{url}: page {page} loaded successfully.")

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
            logging.warning(f"Timeout occurred while loading page {page}. Ending scraping.")
            break

    logging.info(f"Scraping complete. Total books scraped: {len(data)}")
    return data


# Main function to execute the scraper
def main():
    driver = setup_driver()
    try:
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

    finally:
        driver.quit()
        logging.info("WebDriver session closed.")


if __name__ == "__main__":
    main()
