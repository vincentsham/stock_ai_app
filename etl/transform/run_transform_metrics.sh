#!/bin/bash

# --- Safety & Configuration ---
set -euo pipefail

# Path Configuration
# Assuming script is in project/etl/transform/
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
LOG_DIR="$PROJECT_ROOT/logs"
LOG_FILE="$LOG_DIR/transform_job_$(date +%F).log"

mkdir -p "$LOG_DIR"

# --- Helper Functions ---

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

handle_error() {
    log "❌ ERROR: Transform job failed on line $1. Stopping pipeline."
    log "Check details in: $LOG_FILE"
    exit 1
}

trap 'handle_error $LINENO' ERR

run_task() {
    local script_path="$1"
    local full_path="$SCRIPT_DIR/$script_path"

    if [ -f "$full_path" ]; then
        log "Running $script_path..."
        python3 "$full_path"
        log "Completed $script_path. Sleeping 5s..."
        sleep 5
    else
        log "❌ CRITICAL: Script not found at $full_path"
        exit 1
    fi
}

# --- Main Execution ---

log "🚀 Starting Metrics Transformation..."

# 1. Base Transformation
log "--- Phase 1: Base Data Preparation ---"
run_task "earnings/main.py"

# 2. Domain-Specific Metrics
# These are likely independent of each other, but must complete before Phase 3
log "--- Phase 2: Computing Domain Metrics ---"
run_task "metrics/profitability/compute_eps_diluted_metrics.py"
run_task "metrics/revenue/compute_revenue_metrics.py"
run_task "metrics/valuation/compute_valuation_metrics.py"
run_task "metrics/profitability/compute_profitability_metrics.py"
run_task "metrics/growth/compute_growth_metrics.py"
run_task "metrics/efficiency/compute_efficiency_metrics.py"
run_task "metrics/financial_health/compute_financial_health_metrics.py"

# 3. Aggregation & Scoring (Dependent on Phase 2)
# If Phase 2 failed, these would calculate based on incomplete data, so strict error handling is vital.
log "--- Phase 3: Aggregation & Scoring ---"
run_task "metrics/percentiles/compute_percentiles.py"
run_task "metrics/stock_scores/compute_stock_scores.py"

log "✅ Transform Job and Scoring completed successfully."