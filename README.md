# Selenium Scraper - README

## Overview
This Python script automates the process of logging into a website and scraping product data using Selenium WebDriver with undetected ChromeDriver. It is designed to scrape information from dynamic web pages, handle login with authentication, and save the scraped data into a JSON file. The scraper simulates human-like browsing behavior to avoid detection by the website.

## Setup Instructions

### 1. Install Dependencies
To run this scraper, you'll need to install the necessary Python packages. You can do this using `pip`:

```bash
pip install selenium undetected-chromedriver python-dotenv
```

Additionally, you need to download ChromeDriver that matches your version of Google Chrome. If you're using undetected-chromedriver, it will help bypass detection, but make sure you still have the correct version of ChromeDriver.

### 2. Setup Environment Variables
Create a .env file in the same directory as the script and add the following environment variables:

```bash
USER=<your_username>
PASSWORD=<your_password>
BASE_URL=<url_of_the_website_to_scrape>
CHROME_DRIVER_PATH=<path_to_your_chromedriver>
```
Example:

```bash
USER=my_username
PASSWORD=my_password
BASE_URL=https://example.com
CHROME_DRIVER_PATH=/path/to/chromedriver
```

### 3. Configure Logging
Logs will be written to a file called selenium_scraper.log. You can adjust the logging level or format in the script if needed. By default, it logs information, warnings, and errors.

#### Key Selenium Settings
1. Headless Mode
The script runs Chrome in headless mode by default (no GUI), which is useful for running on servers or in CI environments.

2. Incognito Mode
To avoid storing browsing history, the script runs in incognito mode:

3. Automation Flags
To prevent detection as a bot, the script disables automation-related flags:

4. Window Size
The window size is set to 1920x1080 to simulate a typical desktop browser window:


#### Configuration Options
1. Max Pages to Scrape
The scrape_data() function scrapes data from multiple pages. By default, it scrapes up to 5 pages:

2. Page Delay
The script waits for 1-3 seconds between page requests to mimic human-like behavior and avoid being flagged by the website:


#### Functions
1. setup_driver()
This function initializes the Chrome WebDriver with stealth options to avoid detection. It handles setting up the ChromeDriver with appropriate arguments.

2. login(driver, url, username, password)
This function logs into the website using Basic Authentication. It formats the URL with the username and password and waits for the page to load.

3. scrape_data(driver, base_url, max_pages=5)
This function scrapes product data from multiple pages. It navigates through each page, waits for the page content to load, and extracts book details (title, price, availability) into a list. The data is stored in a JSON file.

4. cleanup_driver(driver)
This function ensures the WebDriver session is cleaned up properly after scraping. It quits the WebDriver and closes the browser window.

#### Troubleshooting
1. Common Errors
- TimeoutException: The page failed to load within the allotted time. Check your internet connection and the website’s response time.
- NoSuchElementException: An expected element wasn't found. Ensure the correct classes or tags are used for element selection.
- WebDriverException: The WebDriver failed to start. Verify that your CHROME_DRIVER_PATH is correctly set and the ChromeDriver version is compatible with your installed Chrome version.

2. Logs

    The logs are saved in selenium_scraper.log. Check the log file for detailed information on any issues encountered during execution.

#### Example Usage

Once you've set up your environment variables and dependencies, you can run the scraper with:

```bash
python scraper.py
```
This will log into the website, scrape the data from the specified pages, and save the results into scraped_data.json.


## Conclusion
This scraper provides an automated way to gather product data from websites using Selenium with headless Chrome. By using stealth settings, it minimizes the risk of detection while scraping dynamic content. Be sure to respect the terms of service of the website you are scraping and use the scraper responsibly.