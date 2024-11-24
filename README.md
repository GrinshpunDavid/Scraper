
# README: Web Scraper for Paginated Data

## Overview

This project is a web scraping tool designed to extract data from paginated websites. It leverages **Python**, **Requests**, and **BeautifulSoup** to fetch and parse HTML, with **Tenacity** for robust retry mechanisms. The scraper includes login functionality using HTTP Basic Authentication and supports dynamic proxy and user-agent rotation for improved reliability and anonymity.

---

## Features
- **Authentication**: Supports HTTP Basic Authentication with session management.
- **Proxy and User-Agent Rotation**: Dynamically rotates proxies and user agents for better scraping performance.
- **Retry Mechanism**: Implements robust retry logic using the Tenacity library to handle transient network errors.
- **Pagination Handling**: Automatically detects and handles multi-page websites.
- **Data Extraction**: Parses structured data from HTML and saves it as a JSON file.

---

## Setup

### Prerequisites
Ensure you have the following installed:
- Python 3.8 or higher
- pip (Python package manager)

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/web-scraper.git
   cd web-scraper
   ```
2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up the environment variables:
   - Create a `.env` file in the root directory:
     ```env
     USER=<your_username>
     PASSWORD=<your_password>
     BASE_URL=https://books.toscrape.com
     LOGIN_URL=<your_login_url>
     USER_AGENTS=Mozilla/5.0 (Windows NT 10.0; Win64; x64);; Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)
     PROXIES=http://proxy1.com:8080,http://proxy2.com:8080
     ```

---

## Usage

### Running the Scraper
1. Execute the main script:
   ```bash
   python main.py
   ```
2. The scraper will:
   - Authenticate using the provided credentials.
   - Fetch and scrape data from the paginated website.
   - Save the extracted data to a file named `scraped_data.json` in the current directory.

### Output
The output is a JSON file containing the scraped data in the following format:
```json
[
    {
        "name": "Book Title 1",
        "price": "£23.99",
        "availability": "In stock"
    },
    {
        "name": "Book Title 2",
        "price": "£15.99",
        "availability": "Out of stock"
    }
]
```

---

## Configuration

### Environment Variables
All configuration options are managed via environment variables. Add these variables to the `.env` file:
| Variable       | Description                                      | Default Value                      |
|----------------|--------------------------------------------------|------------------------------------|
| `USER`         | Username for authentication                     | Required                          |
| `PASSWORD`     | Password for authentication                     | Required                          |
| `BASE_URL`     | Base URL of the website to scrape                | `https://books.toscrape.com`      |
| `LOGIN_URL`    | Login endpoint URL                               | Required for authentication       |
| `USER_AGENTS`  | List of user agents separated by `;;`            | See example above                 |
| `PROXIES`      | Comma-separated list of proxy servers            | `http://proxy1.com,http://proxy2` |

### Proxy & User-Agent Rotation
- Proxies are rotated automatically using the `PROXIES` environment variable.
- User-Agent strings are randomly selected from the `USER_AGENTS` environment variable.

### Retry Logic
The `fetch_page` function retries failed requests up to **5 times**, with a random wait of **3 to 10 seconds** between attempts.

---

## Project Structure
```
web-scraper/
├── main.py                  # Main script for running the scraper
├── session_management.py    # Handles session management and authentication
├── requirements.txt         # Python dependencies
├── scraper.log              # Logs runtime information
├── scraped_data.json        # Extracted data (output file)
├── .env                     # Configuration file (environment variables)
└── README.md                # Documentation
```

---

## Logging
- Logs are saved to `scraper.log` in the project root.
- Example log entries:
  ```
  2024-11-24 10:00:00 - INFO - Login successful.
  2024-11-24 10:01:00 - INFO - Scraping page 1...
  2024-11-24 10:02:00 - ERROR - Max retries reached for page 5. Skipping...
  ```

---

## Extending the Project
1. **Custom Parsers**: Modify the `extract_data_from_html` function to scrape additional fields.
2. **Error Handling**: Add specific error-handling cases in the `fetch_page` or `_login` methods.
3. **Integration**: Use the output JSON in other pipelines, such as a database loader.

---

## License
This project is licensed under the MIT License.

---

## Support
For questions or support, feel free to open an issue on the repository or contact the project owner.
