# Part 1: Python Requests-Based Scraper

## Overview

This Python script is a web scraper designed for testing session management and data scraping. It logs into a sample website https://httpbin.org/ to simulate session handling using the requests library. For scraping data, it fetches paginated information from the Books to Scrape website, extracting details about books such as title, price, and availability. The script includes retry logic using the tenacity library to manage transient errors like timeouts, and it logs all activities using the logging module.

## Features

- Login to a website using basic authentication.
- Fetch pages with retry logic to handle errors like timeouts.
- Scrape multiple pages of data (with pagination) from a website.
- Extract structured data from HTML content (e.g., book name, price, availability).
- Store scraped data in a JSON file.
- Log all activities to a file (`scraper.log`).

## Requirements

- Python 3.7+
- The following Python libraries:
  - `requests`
  - `tenacity`
  - `beautifulsoup4`
  - `bs4`
  - `logging`
  - `python-dotenv`

## Installation

1. Clone the repository or download the script.

2. Install required dependencies:
   ```bash
   pip install -r requirements.txt