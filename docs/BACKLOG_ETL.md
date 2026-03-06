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
| 46 | Technical | update Catalyst logic to reduce the run time | High | Close | feat_46 |  |  |
| 46.1 | Technical | existing catalyst | High | Close | feat_46 |  |  |
| 46.2 | Technical | sorting chunks by date | High | Close | feat_46 |  |  |
| 46.3 | Technical | main | High | Close | feat_46 |  |  |
| 46.4 | Technical | catalyst tables | High | Close | feat_46 |  |  |
| 46.5 | Technical | stage 2 - considering the chunks' timeline | High | Close | feat_46 |  |  |
| 1007 | Miscellaneous | Extract the most recent records via API (not full history) | Medium | Open |  |  |  |
| 1008 | Feature | Add a consolidated tag logic| Medium | Open |  |  |  |
| 1013 | Miscellaneous | Design a survey for classifying stock | High | Open |  |  |  |
| 10002 | Feature | Analyze popularity trends | Low | Open |  |  |  |
| 10003 | Feature | Create an advanced ai agent to find the important news, reddit post, tweets | Low | Open |  |  |  |
| 10004 |  |  | Low | Open |  |  |  |
| 10005 | Technical | Improve the speed of ai agent (async + concurrent) | Low | Open |  |  |  |
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
| 13 | Feature | Create Table - Earnings Transcript Analysis | High | Close | feat_13 | 2025-10-11 | 2025-10-11 |
| 13 | Feature | Create and load data into earnings_transcript_analysis | High | Close | feat_13 | 2025-10-11 | 2025-10-11 |
| 14 | Feature | Create a data processing job for analyzing analyst ratings | High | Close | feat_14 | 2025-10-15 | 2025-10-16 |
| 15 | Feature | Catalyst logic | High | Close | feat_15 | 2025-10-28 | 2025-11-01 |
| 16 | Feature | uuid for some tables | High | Close | feat_16 | 2025-10-25 | 2025-10-27 |
| 17 | Feature | integrate catalysts into news and earnings transcripts | High | Close | feat_15 | 2025-10-28 | 2025-11-01 |
| 18 | Feature | A job for earnings metrics | High | Close | feat_18 | 2025-10-16 | 2025-10-16 |
| 19 | Feature | cash flow analysis | High | Close | feat_19 | 2025-10-23 | 2025-10-23 |
| 20 | Feature | load income statements into core | High | Close | feat_20 | 2025-10-18 | 2025-10-18 |
| 21 | Feature | balance sheet analysis | High | Close | feat_21 | 2025-10-24 | 2025-10-24 |
| 22 | Feature | efficiency analysis | High | Close | feat_22 | 2025-10-24 | 2025-10-24 |
| 23 | Miscellaneous | Add columns calendar year, quarter | High | Close | feat_23 | 2025-10-19 | 2025-10-19 |
| 23 | Bugs | raw.earnings table - earnings date is not correct and may be remove fiscal date| High | Close | feat_23 | 2025-10-19 | 2025-10-19 |
| 24 | Feature | growth, stability, acceleration framework | High | Close | feat_24 | 2025-10-20 | 2025-10-21 |
| 25 | Feature | revenue analysis | High | Close | feat_25 | 2025-10-22 | 2025-10-23 |
| 26 | Feature | profitability analysis | High | Close | feat_26 | 2025-10-23 | 2025-10-23 |
| 28 | Feature | load cash flows into core | High | Close | feat_28 | 2025-10-21 | 2025-10-22 |
| 29 | Feature | load balance sheets into core | High | Close | feat_28 | 2025-10-21 | 2025-10-22 |
| 30 | Feature | surprise analysis | High | Close | feat_30 | 2025-10-21 | 2025-10-21 |
| 31 | Feature | analyst reports analysis extending to mid and long term comparison | High | Close | feat_31 | 2025-10-24 | 2025-10-24 |
| 32 | Feature | Catalyst Logic needs to be improved. e.g. each quote can be assigned one catalyst only. | High | Close | feat_32 | 2025-12-02 | 2025-12-03 |
| 33 | Feature | Modify the Catalyst Analysis Logic to only have positive and negative sentiment | High | Close | feat_33 | 2024-12-22 | 2024-12-22 |
| 34 | Feature | Fix the earning transcript extraction (The old website blocks the access. Use https://discountingcashflows.com/company/AAPL/transcripts/) | High | Close | feat_34 | 2025-12-18 | 2025-12-18 |
| 34 | Feature | Fix the earning transcript extraction with DefeatBeta | High | Close | feat_34 | 2025-12-18 | 2025-12-18 |
| 35 | Feature | Working on the metric etl jobs | High | Close | feat_35 | 2025-12-15 | 2025-12-16 |
| 36 | Feature | Fully integrate with DefeatBeta | High | Close | feat_36 | 2025-12-19 | 2025-12-22 |
| 37 | Miscellaneous | Finetune the ai agent process | High | Close | misc_37 | 2025-12-23 | 2025-12-23 |
| 38 | Feature | Add a pre-filter job to filter out or expire news and transcript chunks | High | Close | feat_38 | 2025-12-23 | 2025-12-23 |
| 39 | Miscellaneous | update Catalyst logic to have more bear cases | High | Close | feat_39 | 2025-12-28 | 2025-12-29 |
| 40 | Miscellaneous | update catalyst logic to seperate stage 2 into a and b; rewrite the retriveal current catalysts logic to include embedding lookup | High | Close | feat_40 | 2025-12-30 | 2025-12-31 |
| 41 | Miscellaneous | Add shell scripts for running etl jobs; small update on catalyst prompt; small update on catalyst query; small update on ETL processing | High | Close | feat_41 | 2025-12-31 | 2026-01-05 |
| 42 | Miscellaneous | Integrate with Supabase psql and run script logs | High | Close | feat_42  | 2026-01-05 | 2026-01-06 |
| 43 | Miscellaneous | moving raw, core, ref into local and mart into supabase | High | Close | misc_43  | 2026-01-07 | 2026-01-07 |
| 44 | Bug | fix a bug in etl | High | Close | bug_44  | 2026-01-07 | 2026-01-07 |
| 45 | Bug | fix a bug for null stock score in etl | High | Close | bug_45  | 2026-01-26 | 2026-01-26 |
| 1001 | Technical | Rewrite the loading scripts that can just insert and update new data for all tables | Medium | Close | misc_1004 | 2025-10-12 | 2025-10-13 |
| 1002 | Miscellaneous | Create a md doc for table scehma | Medium | Close | miscellaneous_1002 | 2025-09-30 | 2025-09-30 |
| 1002 | Miscellaneous | Create a md doc for source | Medium | Close | miscellaneous_1002 | 2025-09-30 | 2025-09-30 |
| 1003 | Feature | Standardise the db columns | Medium | Close | misc_1004 | 2025-10-12 | 2025-10-13 |
| 1004 | Miscellaneous | Update db schema document | Medium | Close | misc_1004 | 2025-10-12 | 2025-10-13 |
| 1005 | Technical | Make sure no dup records in news on (tic, title) | Medium | Close | tech_1006 | 2025-10-09 | 2025-10-09 |
| 1006 | Technical | Improve news ai agent prompt | Medium | Close | tech_1006 | 2025-10-09 | 2025-10-09 |
| 1009 | Miscellaneous | Create DataMart Table for catalyst section | Medium | Close | misc_1009 | 2025-12-23 | 2025-12-24 |
| 1010 | Miscellaneous | refactor the insert records function | Medium | Close | misc_1010 | 2025-10-18 | 2025-10-18 |
| 1012 | Miscellaneous | Modify Metrics table column name | Medium | Close | misc_1012 | 2025-12-10 | 2025-12-10 |
| 10001 | Miscellaneous | Improve earnings transcript prompt | Low | Close | misc_10001 | 2025-10-26 | 2025-10-26 |
| 10006 | Technical | Add a validation for earnings calendar | Low | Close | tech_10006 | 2025-11-02 | 2025-11-02 |
| 10007 | Miscellaneous | Update the earnings transcipt instruction doc | Low | Close | misc_10007 | 2025-10-10 | 2025-10-10 |
</div>