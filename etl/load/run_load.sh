#!/bin/bash

# Activate your Python environment if needed
# source /path/to/venv/bin/activate

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Running earnings calendar loader load_earnings_calendar_defeatbeta.py..."
python "$SCRIPT_DIR/earnings/load_earnings_calendar_defeatbeta.py"

echo "Running earnings loader load_earnings.py..."
python "$SCRIPT_DIR/earnings/load_earnings.py"

echo "Running earnings transcripts loader load_earnings_transcripts.py..."
python "$SCRIPT_DIR/earnings/load_earnings_transcripts.py"

echo "Running chunk earnings transcripts..."
python "$SCRIPT_DIR/earnings/chunk_earnings_transcripts.py"

echo "Running embed earnings transcripts..."
python "$SCRIPT_DIR/earnings/embed_earnings_transcripts.py"

echo "Running news loader load_news.py..."
python "$SCRIPT_DIR/news/load_news.py"

echo "Running chunk news..."
python "$SCRIPT_DIR/news/chunk_news.py"

echo "Running embed news..."
python "$SCRIPT_DIR/news/embed_news.py"

echo "Running balance sheets loader load_balance_sheets_quarterly_defeatbeta.py..."
# python "$SCRIPT_DIR/financials/load_balance_sheets_quarterly_defeatbeta.py"
python "$SCRIPT_DIR/financials/load_balance_sheets_quarterly_fmp.py"

echo "Running income statements loader load_income_statements_quarterly_defeatbeta.py..."
# python "$SCRIPT_DIR/financials/load_income_statements_quarterly_defeatbeta.py"
python "$SCRIPT_DIR/financials/load_income_statements_quarterly_fmp.py"

echo "Running cash flow statements loader load_cash_flow_statements_quarterly_defeatbeta.py..."
# python "$SCRIPT_DIR/financials/load_cash_flow_statements_quarterly_defeatbeta.py"
python "$SCRIPT_DIR/financials/load_cash_flow_statements_quarterly_fmp.py"


echo "Running analyst grades loader load_analyst_grades.py..."
python "$SCRIPT_DIR/analysts/load_analyst_grades.py"

echo "Running analyst price targets loader load_analyst_price_targets.py..."
python "$SCRIPT_DIR/analysts/load_analyst_price_targets.py"