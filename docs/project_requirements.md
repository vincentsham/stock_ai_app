# Project Requirements: AI Agent for Stock Analysis

## Overview
The AI agent will provide real-time stock analysis and insights. It will fetch stock-related data, analyze trends, and deliver actionable insights to users. The initial scope focuses on retrieving stock information and news headlines.

---

## AI Agent Requirements

| ID  | Feature | Input | Output  | Source         |
|------|-------|------|----------|----------------|
| AR1  | Extract important news, reddit posts, tweets |  Stock ticker   | news, reddit posts, tweets  |
| AR2  | Analyze the stock financial statements |  Stock ticker   | score, summary and comments  |
| AR3  | Analyze the stock's recent catalysts |  Stock ticker   | score, summary and comments  |

---
## Report Requirements

| ID  | Feature | Input | Output  | Source         |
|------|-------|------|----------|----------------|
| RP1  | Stock Information Retrieval | Stock ticker | Ticker symbol, company name, current stock price, current time         | yfinance  |
| RP2  | News Headlines              | Stock ticker | 5 most recent news headlines                                          |  |

---

## ETL Requirements

| ID  | Feature | Input | Output  | Source         |
|------|-------|------|----------|----------------|
| ETLR1  | Stock price table | Stock ticker symbol (e.g., AAPL, TSLA) | Ticker symbol, company name, current stock price, current time         | yfinance  |
| ETLR2  | News Headlines table | Stock ticker symbol           | 5 most recent news headlines                                          |  |
| ETLR3  | Earnings table | Stock ticker symbol           | historical earnings and earnings date  | CoinCodex |
| ETLR4  | Earning Transcript table | Stock ticker symbol           | earning transcript data | API Ninja |
| ETLR5  | Financial Statement table | Stock ticker symbol           | financial statement data | FMP |
---

## Non-Functional Requirements

| ID   | Requirement   | Description                                                                 |
|------|---------------|-----------------------------------------------------------------------------|
| NFR1 | Performance   | The AI agent should respond to user queries within 2 seconds.              |
| NFR2 | Scalability   | The system should handle multiple concurrent user requests.                |
| NFR3 | Accuracy      | Ensure data fetched from Seeking Alpha is up-to-date and accurate.         |

---

## Technical Requirements

| ID   | Component         | Details                                                                 |
|------|-------------------|-------------------------------------------------------------------------|
| TR1  | Programming Language | Python                                                              |
| TR2  | Frameworks        | FastAPI (API), LangChain (AI-driven conversational capabilities)       |
| TR3  | Data Sources      | Seeking Alpha (for stock and news data)                                |
| TR4  | Libraries         | Requests/HTTPX (API calls), BeautifulSoup (web scraping), Pandas (data manipulation) |

---

## First Scope Functionality

### Included Features

| ID   | Feature                                      | Status |
|------|----------------------------------------------|--------|


### Excluded Features

| ID   | Feature                                      | Status |
|------|----------------------------------------------|--------|


---

## Next Steps
1. Finalize the scope of the first release based on the included features.
2. Design the system architecture and data flow.
3. Implement the core functionality (stock information retrieval and news headlines).
4. Test the system for accuracy and performance.

---

## Sources
1. Yahoo FInance
2. CoinCodex
3. FMP API
4. Twelvedata API
5. News API
6. Benzinga
7. Nasdaq