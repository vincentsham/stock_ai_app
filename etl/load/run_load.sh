#!/bin/bash

# --- Safety & Configuration ---
set -euo pipefail

# Path Configuration
# Assuming script is in project/etl/load/
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)" 
LOG_DIR="$PROJECT_ROOT/logs"
LOG_FILE="$LOG_DIR/load_job_$(date +%F).log"

mkdir -p "$LOG_DIR"

# --- Helper Functions ---

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

handle_error() {
    log "❌ ERROR: Load job failed on line $1. Check logs: $LOG_FILE"
    exit 1
}

trap 'handle_error $LINENO' ERR

run_task() {
    local script_path="$1"
    local full_path="$SCRIPT_DIR/$script_path"

    if [ -f "$full_path" ]; then
        log "Running $script_path..."
        # python3 is safer than python
        python3 "$full_path"
        log "Completed $script_path. Sleeping 5s..."
        sleep 5
    else
        log "⚠️ WARNING: Script not found at $full_path. Skipping."
    fi
}

# --- Main Execution ---

log "🚀 Starting Data Loading & Embedding..."

# 1. Earnings Pipeline (Calendar -> Load -> Chunk -> Embed)
log "--- Processing Earnings ---"
run_task "earnings/load_earnings_calendar_defeatbeta.py"
run_task "earnings/load_earnings.py"

# Critical Chain: Transcript RAG Pipeline
run_task "earnings/load_earnings_transcripts.py"
run_task "earnings/chunk_earnings_transcripts.py"
run_task "earnings/embed_earnings_transcripts.py"

# 2. News Pipeline (Load -> Chunk -> Embed)
log "--- Processing News ---"
run_task "news/load_news.py"
run_task "news/chunk_news.py"
run_task "news/embed_news.py"

# 3. Financial Statements
log "--- Processing Financials ---"
# Note: Toggle comments to switch providers (DefeatBeta vs FMP)

# Balance Sheets
# run_task "financials/load_balance_sheets_quarterly_defeatbeta.py"
run_task "financials/load_balance_sheets_quarterly_fmp.py"

# Income Statements
# run_task "financials/load_income_statements_quarterly_defeatbeta.py"
run_task "financials/load_income_statements_quarterly_fmp.py"

# Cash Flow
# run_task "financials/load_cash_flow_statements_quarterly_defeatbeta.py"
run_task "financials/load_cash_flow_statements_quarterly_fmp.py"

# 4. Analyst Data
log "--- Processing Analysts ---"
run_task "analysts/load_analyst_grades.py"
run_task "analysts/load_analyst_price_targets.py"

log "✅ Load Job completed successfully."