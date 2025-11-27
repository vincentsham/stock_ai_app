import pytest
import asyncio
import time
from tools import get_stock_info, get_stock_info_selenium, get_stock_info_yfinance

@pytest.mark.asyncio
async def test_get_stock_info():
    symbol = "AAPL"
    try:
        response = await get_stock_info(symbol)
        print("get_stock_info result:", response)  # Print the result for debugging
        assert "Apple" in response["company_name"]  # Check if the response contains expected content
    except Exception as e:
        pytest.fail(f"get_stock_info failed with exception: {e}")

@pytest.mark.asyncio
async def test_get_stock_info_selenium():
    symbol = "AAPL"
    try:
        response = await get_stock_info_selenium(symbol)
        print("get_stock_info_selenium result:", response)  # Print the result for debugging
        assert "Apple" in response["company_name"]  # Check if the response contains expected content
    except Exception as e:
        pytest.fail(f"get_stock_info_selenium failed with exception: {e}")

@pytest.mark.asyncio
async def test_get_stock_info_yfinance():
    symbol = "AAPL"
    try:
        response = await get_stock_info_yfinance(symbol)
        print("get_stock_info_yfinance result:", response)  # Print the result for debugging
        assert "Apple" in response["company_name"]  # Check if the response contains expected content
    except Exception as e:
        pytest.fail(f"get_stock_info_yfinance failed with exception: {e}")

@pytest.mark.asyncio
async def test_function_speeds():
    symbol = "AAPL"

    # Measure speed of get_stock_info
    start_time = time.time()
    response_httpx = await get_stock_info(symbol)
    httpx_duration = time.time() - start_time
    print("get_stock_info duration:", httpx_duration, "seconds")
    print("get_stock_info result:", response_httpx)

    # Measure speed of get_stock_info_selenium
    start_time = time.time()
    response_selenium = await get_stock_info_selenium(symbol)
    selenium_duration = time.time() - start_time
    print("get_stock_info_selenium duration:", selenium_duration, "seconds")
    print("get_stock_info_selenium result:", response_selenium)

    # Measure speed of get_stock_info_yfinance
    start_time = time.time()
    response_yfinance = await get_stock_info_yfinance(symbol)
    yfinance_duration = time.time() - start_time
    print("get_stock_info_yfinance duration:", yfinance_duration, "seconds")
    print("get_stock_info_yfinance result:", response_yfinance)

    # Print summary
    print("Summary of function speeds:")
    print(f"get_stock_info: {httpx_duration:.2f} seconds")
    print(f"get_stock_info_selenium: {selenium_duration:.2f} seconds")
    print(f"get_stock_info_yfinance: {yfinance_duration:.2f} seconds")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_get_stock_info())
    asyncio.run(test_get_stock_info_selenium())
    asyncio.run(test_get_stock_info_yfinance())
