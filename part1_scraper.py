import requests
import random
import time
import json
from tenacity import retry, wait_random, stop_after_attempt, before_sleep_log, RetryError
import logging
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
from typing import List, Dict, Optional
from session_management import SessionManagement

# Load environment variables from .env file
load_dotenv()

# Setup Logging
logging.basicConfig(filename='scraper.log', level=logging.INFO, format='%(asctime)s - %(message)s')

# Sample credentials and URLs from environment variables
USERNAME: str = os.getenv("USER", "")
PASSWORD: str = os.getenv("PASSWORD", "")
DEFAULT_TIMEOUT: tuple[int, int] = (5, 15)
BASE_URL: str = os.getenv("BASE_URL", "")
LOGIN_URL: str = os.getenv("LOGIN_URL", "")  # HTTP Basic Auth URL (for testing)

# Proxy and User-Agent List for rotation from environment variables
USER_AGENTS: List[str] = os.getenv("USER_AGENTS", "").split(';; ')
PROXIES: List[str] = os.getenv("PROXIES", "").split(',')


# Retry logic using tenacity
@retry(wait=wait_random(min=3, max=10), stop=stop_after_attempt(5),
       before_sleep=before_sleep_log(logging.getLogger(), logging.INFO))
def fetch_page(session: requests.Session, url: str, timeout: tuple[int, int] = DEFAULT_TIMEOUT) -> requests.Response:
    head: Dict[str, str] = {'User-Agent': random.choice(USER_AGENTS),
                            "Accept": "application/json, text/plain, */*"}
    prox: Dict[str, str] = {'http': random.choice(PROXIES)}

    logging.info(f"Proxy-Agent: {prox}, {head}")
    try:
        response = session.get(url, headers=head, proxies=prox, timeout=timeout)
        response.raise_for_status()
    except requests.exceptions.Timeout:
        logging.warning(f"Timeout error for {url}. Retrying...")
        raise
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching {url}: {e}")
        raise
    return response


# Function to parse HTML and extract structured data (name, price, availability for books)
def extract_data_from_html(page_html: str) -> List[Dict[str, str]]:
    soup = BeautifulSoup(page_html, 'html.parser')
    books: List[Dict[str, str]] = []

    # Find all book containers (each book is inside an article with class 'product_pod')
    book_elements = soup.find_all('article', class_='product_pod')

    # Data validation
    if not soup or not book_elements:
        logging.warning("No valid content found on the page. Skipping extraction.")
        return books

    for book in book_elements:
        title = book.find('h3').find('a')['title'] if book.find('h3') else "N/A"
        price = book.find('p', class_='price_color').text if book.find('p', class_='price_color') else "N/A"
        availability = book.find('p', class_='instock availability').text.strip() if book.find('p', class_='instock availability') else "N/A"
        price = price.replace("\u00c2\u00a3", "").strip()  # Clean the price by removing unwanted characters

        books.append({
            'name': title,
            'price': price,
            'availability': availability
        })

    return books


def get_max_page(session: requests.Session, base_url: str) -> int:
    """
    Fetch the first page and parse it to find the maximum page number.
    """
    try:
        url = f"{base_url}/catalogue/page-1.html"
        logging.info("Determining the total number of pages...")
        soup = BeautifulSoup(fetch_page(session, url).text, 'html.parser')
        last_page = soup.find("ul", class_="pager").find("li", class_="current").text.strip().split()[-1]
        logging.info(f"Max page number determined: {last_page}")
        return int(last_page)
    except Exception as e:
        logging.warning(f"Pagination not found or error occurred ({e}). Defaulting to 1 page.")
        return 1


# Function to scrape paginated data
def scrape_paginated_data(session: requests.Session, base_url: str, max_pages: int = 0) -> List[Dict[str, str]]:
    page: int = 1
    data: List[Dict[str, str]] = []

    # https://httpbin.org/ has no data to scrap, so I am using books.toscrape.com
    base_url = "https://books.toscrape.com"

    # Determine max_pages dynamically if not provided
    if max_pages == 0:
        max_pages = get_max_page(session, base_url)

    while page <= max_pages:  # Stop scraping after max_pages
        url = f"{base_url}/catalogue/page-{page}.html"
        logging.info(f"Scraping page {page}...")

        try:
            response = fetch_page(session, url)  # This will retry if necessary
        except RetryError:
            logging.error(f"Max retries reached for page {page}. Skipping...")
            break
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching page {page} with exception {e}. Skipping...")
            break

        page_html = response.text  # Get the raw HTML content
        if page_html:
            page_data = extract_data_from_html(page_html)  # Parse and extract data
            data.extend(page_data)

        page += 1
        time.sleep(random.randint(1, 3))  # Random sleep to mimic human-like behavior

    return data


# Main function to execute the scraper
def main() -> None:

    # Initialize the session management
    session_manager = SessionManagement(username=USERNAME, password=PASSWORD, login_url=LOGIN_URL)
    session = session_manager.get_session()

    # Check if login was successful
    if not session_manager.is_login:
        logging.error("Login failed. Exiting...")
        return

    # 2. Scrape paginated data
    logging.info("Starting to scrape paginated data:")
    data = scrape_paginated_data(session, BASE_URL)

    # 3. Save data to a JSON file
    with open('scraped_data.json', 'w') as f:
        json.dump(data, f, indent=4)
    logging.info("Data saved successfully to 'scraped_data.json'.")

    logging.info("Scraping completed.")


# Entry point of the script
if __name__ == "__main__":
    main()
