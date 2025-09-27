from langchain_community.tools.tavily_search import TavilySearchResults
from dotenv import load_dotenv
import os
import httpx
from bs4 import BeautifulSoup
from datetime import datetime
import pytz
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import lxml.html
import yfinance as yf
from langchain_core.tools import tool

# Load environment variables
load_dotenv()

# Retrieve the Tavily API key from the environment
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# Initialize TavilySearchResults tool
tavily_search_results_json = TavilySearchResults(max_results=4, tavily_api_key=TAVILY_API_KEY)


@tool
async def get_stock_info(ticker: str, user_timezone: str = "UTC") -> dict:
    """
    Fetch stock information for a given ticker by scraping Yahoo Finance and save the HTML for debugging.

    Args:
        ticker (str): The stock ticker symbol (e.g., AAPL, TSLA).
        user_timezone (str): The user's local timezone (default is UTC).

    Returns:
        dict: A dictionary containing the ticker, company name, current stock price, and current time.
    """
    try:
        # Scrape Yahoo Finance for stock information
        url = f"https://finance.yahoo.com/quote/{ticker}/"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Referer": "https://www.google.com/"
        }
        async with httpx.AsyncClient(headers=headers) as client:
            response = await client.get(url)
            response.raise_for_status()

        # # Save the HTML content to a file for debugging
        # save_html_to_file(response.text, filename="debug_yahoo_finance.html")

        # Parse the HTML content using lxml for XPath support
        tree = lxml.html.fromstring(response.text)

        # Extract stock information using XPath
        company_name = tree.xpath("//h1[contains(@class, 'yf-4vbjci')]/text()")
        company_name = company_name[0].strip() if company_name else None

        stock_price = tree.xpath("//fin-streamer[@data-field='regularMarketPrice']/text()")
        stock_price = stock_price[0].strip() if stock_price else None

        # Get the current time in the user's local timezone
        utc_now = datetime.now(pytz.utc)
        local_time = utc_now.astimezone(pytz.timezone(user_timezone))
        current_time = local_time.strftime('%Y-%m-%d %H:%M:%S %Z')

        return {
            "ticker": ticker,
            "company_name": company_name,
            "stock_price": stock_price,
            "current_time": current_time
        }

    except httpx.RequestError as e:
        return {"error": f"Failed to fetch data for ticker {ticker}: {str(e)}"}
    except AttributeError:
        return {"error": f"Failed to parse data for ticker {ticker}. The structure of the page may have changed."}

@tool
async def get_stock_info_selenium(ticker: str, user_timezone: str = "UTC") -> dict:
    """
    Fetch stock information for a given ticker using Selenium to scrape Yahoo Finance and save the HTML for debugging.

    Args:
        ticker (str): The stock ticker symbol (e.g., AAPL, TSLA).
        user_timezone (str): The user's local timezone (default is UTC).

    Returns:
        dict: A dictionary containing the ticker, company name, current stock price, and current time.
    """
    try:
        # Set up Selenium WebDriver with Chrome
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in headless mode
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

        # Navigate to the Yahoo Finance page for the ticker
        url = f"https://finance.yahoo.com/quote/{ticker}"
        driver.get(url)

        # # Save the HTML content to a file for debugging
        # save_html_to_file(driver.page_source, filename="debug_yahoo_finance_selenium.html")

        # Wait for the page to load
        driver.implicitly_wait(10)

        # Get the current time in the user's local timezone
        utc_now = datetime.now(pytz.utc)
        local_time = utc_now.astimezone(pytz.timezone(user_timezone))
        current_time = local_time.strftime('%Y-%m-%d %H:%M:%S %Z')

        # Extract stock information
        try:
            # Extract stock information using XPath
            company_name_element = driver.find_element(By.XPATH, "//h1[contains(@class, 'yf-4vbjci')]")
            company_name = company_name_element.text

            stock_price_element = driver.find_element(By.XPATH, "//fin-streamer[@data-field='regularMarketPrice']")
            stock_price = stock_price_element.text

        except Exception as e:
            raise ValueError("Failed to locate elements on the page. The structure may have changed.") from e

        driver.quit()

        return {
            "ticker": ticker,
            "company_name": company_name,
            "stock_price": stock_price,
            "current_time": current_time
        }

    except Exception as e:
        if 'driver' in locals():
            driver.quit()
        return {"error": f"Failed to fetch data for ticker {ticker}: {str(e)}"}

@tool
async def get_stock_info_yfinance(ticker: str, user_timezone: str = "UTC") -> dict:
    """
    Fetch stock information for a given ticker using the yfinance library.

    Args:
        ticker (str): The stock ticker symbol (e.g., AAPL, TSLA).
        user_timezone (str): The user's local timezone (default is UTC).

    Returns:
        dict: A dictionary containing the ticker, company name, current stock price, and current time.
    """
    try:
        # Fetch stock data using yfinance
        stock = yf.Ticker(ticker)
        stock_info = stock.info

        company_name = stock_info.get("longName", None)
        stock_price = stock_info.get("regularMarketPrice", None)

        # Get the current time in the user's local timezone
        utc_now = datetime.now(pytz.utc)
        local_time = utc_now.astimezone(pytz.timezone(user_timezone))
        current_time = local_time.strftime('%Y-%m-%d %H:%M:%S %Z')

        return {
            "ticker": ticker,
            "company_name": company_name,
            "stock_price": stock_price,
            "current_time": current_time
        }

    except Exception as e:
        return {"error": f"Failed to fetch data for ticker {ticker}: {str(e)}"}




