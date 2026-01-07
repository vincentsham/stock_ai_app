#!/bin/bash

# --- Safety & Configuration ---
set -euo pipefail

# Path Configuration
# Assuming script is in project/etl/publish/
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
LOG_DIR="$PROJECT_ROOT/logs"
LOG_FILE="$LOG_DIR/publish_job_$(date +%F).log"

mkdir -p "$LOG_DIR"

# --- Helper Functions ---

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

handle_error() {
    log "❌ ERROR: Publish job failed on line $1. Check logs: $LOG_FILE"
    exit 1
}

trap 'handle_error $LINENO' ERR

run_task() {
    local script_name="$1"
    local full_path="$SCRIPT_DIR/$script_name"

    if [ -f "$full_path" ]; then
        log "Running $script_name..."
        python3 "$full_path"
        log "Completed $script_name. Sleeping 5s..."
        sleep 5
    else
        log "❌ CRITICAL: Script not found at $full_path"
        exit 1
    fi
}

# --- Main Execution ---

log "🚀 Starting Data Publish (Production Sync)..."

# 1. Core Stock Data
log "--- Publishing Core Profiles ---"
run_task "publish_stock_profiles.py"

# 2. Financial Metrics (The Numbers)
log "--- Publishing Financial Metrics ---"
run_task "publish_efficiency_metrics.py"
run_task "publish_financial_health_metrics.py"
run_task "publish_growth_metrics.py"
run_task "publish_profitability_metrics.py"
run_task "publish_valuation_metrics.py"

# 3. Earnings & Analysis (The Context)
log "--- Publishing Earnings & Analysis ---"
run_task "publish_earnings.py"
run_task "publish_earnings_regime.py"
run_task "publish_earnings_transcript_analysis.py"
run_task "publish_analyst_rating_yearly_summary.py"

# 4. Scores & Insights (The Alpha)
log "--- Publishing Scores & Catalysts ---"
run_task "publish_stock_scores.py"
run_task "publish_catalyst_master.py"

log "✅ Publish Job completed successfully. Production DB is up to date."