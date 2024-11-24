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

# Load environment variables
load_dotenv()

# Constants
DEFAULT_TIMEOUT: tuple[int, int] = (5, 15)
USER_AGENTS: List[str] = os.getenv("USER_AGENTS", "").split(';; ')
PROXIES: List[str] = os.getenv("PROXIES", "").split(',')
BASE_URL: str = os.getenv("BASE_URL")  # https://books.toscrape.com for scraping
LOGIN_URL: str = os.getenv("LOGIN_URL", "")  # https://httpbin.org/ for basic-auth
USERNAME: str = os.getenv("USER", "")
PASSWORD: str = os.getenv("PASSWORD", "")

# Logging Configuration
logging.basicConfig(
    filename='scraper.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

@retry(
    wait=wait_random(min=3, max=10),
    stop=stop_after_attempt(5),
    before_sleep=before_sleep_log(logging.getLogger(), logging.INFO)
)
def fetch_page(session: requests.Session, url: str, timeout: tuple[int, int] = DEFAULT_TIMEOUT) -> requests.Response:
    """
    Fetch a page with retry logic, using a random proxy and User-Agent for rotation.
    """
    headers = {
        'User-Agent': random.choice(USER_AGENTS),
        "Accept": "application/json, text/plain, */*"
    }
    proxies = {'http': random.choice(PROXIES)}

    logging.info(f"Fetching URL: {url} with Proxy: {proxies} and Headers: {headers}")
    response = session.get(url, headers=headers, proxies=proxies, timeout=timeout)
    response.raise_for_status()  # Raise an exception for HTTP errors
    return response


def extract_data_from_html(html_content: str) -> List[Dict[str, str]]:
    """
    Parse the HTML content and extract book data (title, price, availability).
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    books = []

    book_elements = soup.find_all('article', class_='product_pod')
    if not book_elements:
        logging.warning("No valid book elements found on the page.")
        return books

    for book in book_elements:
        title = book.find('h3').find('a')['title'] if book.find('h3') else "N/A"
        price = book.find('p', class_='price_color').text if book.find('p', class_='price_color') else "N/A"
        availability = book.find('p', class_='instock availability').text.strip() if book.find('p', class_='instock availability') else "N/A"
        price = price.replace("£", "").replace("Â", "").strip()  # Remove currency symbol for normalization

        books.append({
            'name': title,
            'price': price,
            'availability': availability
        })

    return books


def get_max_page(session: requests.Session, base_url: str) -> int:
    """
    Determine the total number of pages from the first page of the catalog.
    """
    try:
        url = f"{base_url}/catalogue/page-1.html"
        logging.info("Fetching the first page to determine pagination...")
        response = fetch_page(session, url)
        soup = BeautifulSoup(response.text, 'html.parser')
        pagination = soup.find("ul", class_="pager")
        if pagination:
            last_page = pagination.find("li", class_="current").text.strip().split()[-1]
            return int(last_page)
        else:
            logging.info("No pagination found. Defaulting to 1 page.")
    except Exception as e:
        logging.warning(f"Error determining max page: {e}. Defaulting to 1 page.")
    return 1


def scrape_paginated_data(session: requests.Session, base_url: str, max_pages: Optional[int] = None) -> List[Dict[str, str]]:
    """
    Scrape data across paginated pages and return a list of extracted book details.
    """
    data = []

    if max_pages is None:
        max_pages = get_max_page(session, base_url)

    for page in range(1, max_pages + 1):
        url = f"{base_url}/catalogue/page-{page}.html"
        logging.info(f"Scraping page {page} of {max_pages}...")

        try:
            response = fetch_page(session, url)
            page_data = extract_data_from_html(response.text)
            data.extend(page_data)
        except RetryError:
            logging.error(f"Max retries reached for page {page}. Skipping...")
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching page {page}: {e}. Skipping...")

        time.sleep(random.uniform(1, 3))  # Randomized delay to mimic human behavior

    return data


def save_data_to_file(data: List[Dict[str, str]], file_name: str) -> None:
    """
    Save the scraped data to a JSON file.
    """
    with open(file_name, 'w') as file:
        json.dump(data, file, indent=4)
    data_length = len(data) if isinstance(data, (list, dict)) else "N/A"
    logging.info(f"Data successfully saved to '{file_name}'. Total items scraped: {data_length}.")


def main() -> None:
    """
    Main function to orchestrate the scraping process.
    """
    logging.info("Initializing the scraping session...")

    # Initialize session management
    session_manager = SessionManagement(username=USERNAME, password=PASSWORD, login_url=LOGIN_URL)
    session = session_manager.get_session()

    if not session_manager.is_login:
        logging.error("Login failed. Exiting...")
        return

    # Start scraping
    logging.info("Starting data scraping...")
    data = scrape_paginated_data(session, BASE_URL)

    # Save the scraped data
    save_data_to_file(data, 'scraped_data.json')

    logging.info("Scraping process completed successfully.")


if __name__ == "__main__":
    main()
