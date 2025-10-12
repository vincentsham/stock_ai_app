# Data Sources Documentation

## yfinance
**Description**: A Python library for accessing historical market data, stock metadata, and financial information.

**Usage**: Used in the following scripts:
- `extract_stock_metadata.py`
- `extract_stock_ohlcv.py`

**Documentation**: [yfinance Documentation](https://pypi.org/project/yfinance/)

---

## Financial Modeling Prep API
**Description**: Provides financial statement data, including income statements, balance sheets, and cash flow statements for publicly traded companies.

**Usage**: Used in the following scripts:
- `extract_income_statements.py`
- `extract_balance_sheets.py`
- `extract_cash_flows.py`

**Limitation**: 250 API calls per day in the free tier.

**Documentation**: [Financial Modeling Prep API](https://site.financialmodelingprep.com/developer/docs)

---

## API Ninjas Earnings Transcript API
**Description**: Offers earnings call transcripts for publicly traded companies.

**Usage**: Used in the following script:
- `extract_earnings_transcripts.py`

**Limitation**: 10,000 API calls per month in the free tier.

**Documentation**: [API Ninjas API](https://api-ninjas.com/api)

---

## CoinCodex API
**Description**: Provides historical earnings data for stocks.

**Usage**: Used in the following script:
- `extract_historical_earnings.py`

**Documentation**: [CoinCodex API](https://coincodex.com/api/)