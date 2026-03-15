#!/bin/bash

# --- Safety & Configuration ---
set -euo pipefail

# Paths (Assuming script is in project/etl/extract/)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
LOG_DIR="$PROJECT_ROOT/logs"
LOG_FILE="$LOG_DIR/daily_extract_$(date +%F).log"

mkdir -p "$LOG_DIR"

# --- Helper Functions ---

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

handle_error() {
    log "❌ ERROR: Batch job failed on line $1. Check log: $LOG_FILE"
    exit 1
}

trap 'handle_error $LINENO' ERR

# This function runs the python script and handles the sleep logic
run_task() {
    local script_name="$1"
    local full_path="$SCRIPT_DIR/$script_name"

    if [ -f "$full_path" ]; then
        log "Running $script_name..."
        python3 "$full_path"
        log "Completed $script_name. Sleeping 30s..."
        sleep 30
    else
        log "⚠️ WARNING: Script not found at $full_path. Skipping."
    fi
}

# --- Main Execution ---

log "🚀 Starting Daily Extraction Batch..."

# 1. Market Data
run_task "stocks/extract_stock_ohlcv_daily_yf.py"

# 2. News
run_task "news/extract_news_fmp.py"

# 3. Financial Statements (Quarterly)
# Note: Swap comments below to switch data providers (DefeatBeta vs FMP)
# run_task "financials/extract_balance_sheets_quarterly_defeatbeta.py"
run_task "financials/extract_balance_sheets_quarterly_fmp.py"

# run_task "financials/extract_income_statements_quarterly_defeatbeta.py"
run_task "financials/extract_income_statements_quarterly_fmp.py"

# run_task "financials/extract_cash_flow_statements_quarterly_defeatbeta.py"
run_task "financials/extract_cash_flow_statements_quarterly_fmp.py"

# 4. Earnings & Analysis
run_task "earnings/extract_earnings.py"
run_task "analysts/extract_analyst_grades_fmp.py"
run_task "analysts/extract_analyst_price_targets_fmp.py"
run_task "earnings/extract_earnings_transcripts_defeatbeta.py"

log "✅ All extraction jobs finished successfully."