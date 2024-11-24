
# Selenium Web Scraper

This project is a web scraping utility using Selenium, undetected_chromedriver, and various proxy and user-agent configurations. The scraper logs into a website, navigates through paginated content, and extracts book data. The scraped data is then saved as a JSON file.

## Setup Instructions

### Prerequisites
Ensure you have Python 3.8+ installed and have access to the following:
- ChromeDriver compatible with your version of Google Chrome
- Python packages listed below

### Install Dependencies
1. Clone the repository or download the script files.
2. Install required Python libraries:

```bash
pip install -r requirements.txt
```

### Configuration

1. **Environment Variables**:
   The following environment variables must be set in your `.env` file:
   - `USER`: Your username for HTTP Basic Authentication.
   - `PASSWORD`: Your password for HTTP Basic Authentication.
   - `BASE_URL`: The base URL of the website to scrape.
   - `CHROME_DRIVER_PATH`: The path to your ChromeDriver executable.
   - `USER_AGENTS`: A list of user-agent strings separated by `;; `. Example:
     ```text
     Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36;; Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36
     ```
   - `PROXIES`: A comma-separated list of proxy addresses. Example:
     ```text
     http://proxy1.com:8080,http://proxy2.com:8080
     ```

2. **.env File Example**:
   Create a `.env` file in your project directory with the following structure:

   ```
   USER=your_username
   PASSWORD=your_password
   BASE_URL=https://example.com
   CHROME_DRIVER_PATH=/path/to/chromedriver
   USER_AGENTS=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36;; Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36
   PROXIES=http://proxy1.com:8080,http://proxy2.com:8080
   ```

## Key Selenium Settings

### WebDriver Options

1. **Headless Mode**:
   The script runs the Chrome WebDriver in headless mode (`--headless`), meaning no GUI is displayed. This is ideal for running the scraper on servers without a graphical environment.

2. **Incognito Mode**:
   The WebDriver is set to run in incognito mode (`--incognito`), which prevents storing browsing history, cookies, or other session data.

3. **Disable Automation Flags**:
   The `--disable-blink-features=AutomationControlled` argument disables detection of automation (to bypass bot prevention mechanisms).

4. **Proxy and User-Agent Rotation**:
   The scraper randomly selects a proxy and user-agent for each session to help avoid IP bans or other blocking mechanisms.

5. **Window Size**:
   The default window size is set to 1920x1080 (`--window-size=1920,1080`).

6. **Other Options**:
   - `--disable-gpu`: Disables GPU hardware acceleration (useful in headless mode).
   - `--disable-dev-shm-usage`: Disables the `/dev/shm` file system to avoid issues in Docker containers.
   - `--disable-extensions`: Disables extensions to minimize performance overhead.
   - `--disable-notifications`: Disables notifications that might interfere with the scraping.

### Login Process
The scraper uses HTTP Basic Authentication. The login URL is constructed by embedding the username and password into the URL string:
```
https://<username>:<password>@<base_url>
```

### Scraping Logic
- The scraper iterates through pages of a catalogue (`page-{number}.html`).
- It waits for the page content to load before extracting data from each book entry.
- Data extracted includes the book title, price, and availability.
- The scraper stops after scraping the specified number of pages or if three consecutive page load failures occur.

### Saving the Data
The scraped data is saved in a `scraped_data.json` file in JSON format. Each entry contains the book's name, price, and availability.

## Running the Scraper

To run the scraper, simply execute the `part2_scraper.py` script:

```bash
python part2_scraper.py
```

The scraper will:
1. Initialize the WebDriver.
2. Scrape up to 5 pages of books.
3. Save the data in `scraped_data.json`.

## Troubleshooting
- **Timeout Issues**: If the scraper is timing out while loading pages, try adjusting the `max_pages` parameter or the `WebDriverWait` timeouts.
- **Proxy Errors**: Ensure your proxies are working correctly, and you have enough proxies to rotate between requests.

## License
This project is licensed under the MIT License - see the LICENSE file for details.
