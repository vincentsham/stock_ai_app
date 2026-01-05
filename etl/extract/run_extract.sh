#!/bin/bash

# Activate your Python environment if needed
# source /path/to/venv/bin/activate

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}" )" && pwd)"

echo "Running extract_stock_ohlcv_daily_yf.py..."
python "$SCRIPT_DIR/stocks/extract_stock_ohlcv_daily_yf.py"

echo "Running extract_news_fmp.py..."
python "$SCRIPT_DIR/news/extract_news_fmp.py"

echo "Running extract_balance_sheets_quarterly_fmp.py..."
# python "$SCRIPT_DIR/financials/extract_balance_sheets_quarterly_defeatbeta.py"
python "$SCRIPT_DIR/financials/extract_balance_sheets_quarterly_fmp.py"

echo "Running extract_income_statements_quarterly_fmp.py..."
# python "$SCRIPT_DIR/financials/extract_income_statements_quarterly_defeatbeta.py"
python "$SCRIPT_DIR/financials/extract_income_statements_quarterly_fmp.py"

echo "Running extract_cash_flow_statements_quarterly_fmp.py..."
# python "$SCRIPT_DIR/financials/extract_cash_flow_statements_quarterly_defeatbeta.py"
python "$SCRIPT_DIR/financials/extract_cash_flow_statements_quarterly_fmp.py"

echo "Running extract_earnings.py..."
python "$SCRIPT_DIR/earnings/extract_earnings.py"

echo "Running extract_earnings_transcripts_defeatbeta.py..."
python "$SCRIPT_DIR/earnings/extract_earnings_transcripts_defeatbeta.py"

echo "Running extract_analyst_grades_fmp.py..."
python "$SCRIPT_DIR/analysts/extract_analyst_grades_fmp.py"

echo "Running extract_analyst_price_targets_fmp.py..."
python "$SCRIPT_DIR/analysts/extract_analyst_price_targets_fmp.py"


