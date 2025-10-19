# Project Backlog

## Features
examples:
- Implement AI-driven stock trend analysis
- Add support for additional financial data sources (e.g., Alpha Vantage, Yahoo Finance)
- Enhance user interface for better visualization of stock data
- Integrate notifications for stock price alerts

## Bugs
examples:
- Fix database connection timeout issues
- Resolve duplicate entries in the `earnings` table
- Address API rate limit handling for data fetching

## Technical
examples:
- Refactor ETL pipeline for better modularity
- Optimize database queries for faster performance
- Improve error handling in the server code

## Research
examples:
- Explore integration with real-time stock trading APIs
- Investigate advanced AI models for financial forecasting
- Study user feedback for feature prioritization

## Miscellaneous
examples:
- Update documentation for new features
- Write additional unit tests for critical components

## Backlog Table


### Open Backlog Items
<div style="font-size:smaller">

| ID  | Category | Description | Priority | Status    | Branch | Open Date  | Close Date |
|------|----------|-------------|----------|-----------|--------|------------|------------|
| 15 | Feature | Catalyst logic | High | Open |  |  |  |
| 16 | Feature | uuid for some tables | High | Open |  |  |  |
| 17 | Feature | integrate catalysts into news, analyst ratings and earnings | High | Open |  |  |  |
| 19 | Feature | A job for analyzing balance sheets | High | Open |  |  |  |
| 20 | Feature | A job for analyzing income statements | High | Open |  |  |  |
| 21 | Feature | A job for analyzing cash flows | High | Open |  |  |  |
| 22 | Miscellaneous | Design a survey for classifying stock | High | Open |  |  |  |
| 23 | Miscellaneous | Add columns calendar year, quarter | High | Open |  |  |  |
| 23 | Bugs | raw.earnings table - earnings date is not correct and may be remove fiscal date| High | Open |  |  |  |
| 1007 | Feature | Create and load raw tables in core | Medium | Open |  |  |  |
| 1008 | Miscellaneous | Extract the most recent records via API (not full history) | Medium | Open |  |  |  |
| 1009 | Miscellaneous | Extract news - fetching pages | Medium | Open |  |  |  |
| 10001 | Feature | Transfer Tables that has text to Pinecone | Low | Open |  |  |  |
| 10002 | Feature | Analyze popularity trends | Low | Open |  |  |  |
| 10003 | Feature | Create an advanced ai agent to find the important news, reddit post, tweets | Low | Open |  |  |  |
| 10004 | Miscellaneous | Create psql partition logic | Low | Open |  |  |  |
</div>



### Closed Backlog Items
<div style="font-size:smaller">

| ID  | Category | Description | Priority | Status    | Branch | Open Date  | Close Date |
|------|----------|-------------|----------|-----------|--------|------------|------------|
| 0 | Feature | Create Table - Stock metadata | High | Close | Starter | 2025-09-20 | 2025-09-26 |
| 0 | Feature | Create Table - Stock OHLCV | High | Close | Starter | 2025-09-20 | 2025-09-26 |
| 0 | Feature | Create Table - Earnings | High | Close | Starter | 2025-09-20 | 2025-09-26 |
| 0 | Feature | Create Basic AI Agent | High | Close | Starter | 2025-09-20 | 2025-09-26 |
| 0 | Miscellaneous | Restructure File and Folder Structure | High | Close | Starter | 2025-09-20 | 2025-09-26 |
| 1 | Feature | Create Table - Earnings Transcripts | High | Close | feature_1 | 2025-09-27 | 2025-09-28 |
| 2 | Feature | Create Table - Income Statements | High | Close |feature_2  | 2025-09-28 | 2025-09-29 |
| 2 | Feature | Create Table - Cash Flows | High | Close | feature_2 | 2025-09-28 | 2025-09-29 |
| 2 | Feature | Create Table - Balance Sheets | High | Close | feature_2 | 2025-09-28 | 2025-09-29 |
| 2 | Feature | Add No. of inserted records | Low | Close | feature_2 | 2025-09-28 | 2025-09-29 |
| 3 | Feature | Create Table - News analysis | High | Close | feature_3 | 2025-10-06 | 2025-10-06 |
| 4 | Feature | Create Table - News From FMP API | High | Close | feature_4 | 2025-10-04 | 2025-10-04 |
| 5 | Feature | Create Table - Analyst Ratings From FMP API | High | Close | feat_5 | 2025-10-12 | 2025-10-12 |
| 6 | Feature | Create Table - Dividends From FMP API | High | Close | feat_6 | 2025-10-12 |2025-10-12 |
| 7 | Feature | Create an advanced ai agent to analyze news | High | Close | feature_7 | 2025-10-05 | 2025-10-05 |
| 8 | Feature | Create Table - Earnings Chunks | High | Close | feature_8 | 2025-10-07 | 2025-10-07 |
| 8 | Feature | Create Table - Earnings Embeddings | High | Close | feature_8 | 2025-10-07 | 2025-10-07 |
| 10 | Feature | Create an advanced ai agent to analyze earnings transcripts | High | Close | feature_10 | 2025-10-08 | 2025-10-09 |
| 11 | Feature | Create a data processing task to process the company profile | High | Close | feat_11 | 2025-10-11 | 2025-10-11 |
| 12 | Feature | Extend the earnings transcript ai agent to analyze how company handle the risk | High | Close | feat_12 | 2025-10-09 | 2025-10-10 |
| 13 | Feature | Create Table - Earnings Transcript Analysis | Medium | Close | feat_13 | 2025-10-11 | 2025-10-11 |
| 13 | Feature | Create and load data into earnings_transcript_analysis | Medium | Close | feat_13 | 2025-10-11 | 2025-10-11 |
| 14 | Feature | Create a data processing job for analyzing analyst ratings | High | Close | feat_14 | 2025-10-15 | 2025-10-16 |
| 18 | Feature | A job for earnings metrics | High | Close | feat_18 | 2025-10-16 | 2025-10-16 |
| 1001 | Technical | Rewrite the loading scripts that can just insert and update new data for all tables | Medium | Close | misc_1004 | 2025-10-12 | 2025-10-13 |
| 1002 | Miscellaneous | Create a md doc for table scehma | Medium | Close | miscellaneous_1002 | 2025-09-30 | 2025-09-30 |
| 1002 | Miscellaneous | Create a md doc for source | Medium | Close | miscellaneous_1002 | 2025-09-30 | 2025-09-30 |
| 1003 | Feature | Standardise the db columns | Medium | Close | misc_1004 | 2025-10-12 | 2025-10-13 |
| 1004 | Miscellaneous | Update db schema document | Medium | Close | misc_1004 | 2025-10-12 | 2025-10-13 |
| 1005 | Technical | Make sure no dup records in news on (tic, title) | Medium | Close | tech_1006 | 2025-10-09 | 2025-10-09 |
| 1006 | Technical | Improve news ai agent prompt | Medium | Close | tech_1006 | 2025-10-09 | 2025-10-09 |
| 1010 | Miscellaneous | refactor the insert records function | Medium | Close | misc_1010 | 2025-10-18 | 2025-10-18 |
| 10007 | Miscellaneous | Update the earnings transcipt instruction doc | Low | Close | misc_10007 | 2025-10-10 | 2025-10-10 |
</div>