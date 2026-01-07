#!/bin/bash

# --- Safety & Configuration ---
set -euo pipefail

# Path Configuration
# Assuming script is in project/etl/transform/ (adjust levels if needed)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
LOG_DIR="$PROJECT_ROOT/logs"
LOG_FILE="$LOG_DIR/analysis_job_$(date +%F).log"

mkdir -p "$LOG_DIR"

# --- Helper Functions ---

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

handle_error() {
    log "❌ ERROR: Analysis job failed on line $1. Check logs: $LOG_FILE"
    exit 1
}

trap 'handle_error $LINENO' ERR

run_task() {
    local script_path="$1"
    local full_path="$SCRIPT_DIR/$script_path"

    # Optional: Allow passing a custom sleep time as 2nd argument (default 5s)
    local sleep_time="${2:-5}"

    if [ -f "$full_path" ]; then
        log "Running $script_path..."
        python3 "$full_path"
        log "Completed $script_path. Sleeping ${sleep_time}s..."
        sleep "$sleep_time"
    else
        log "⚠️ WARNING: Script not found at $full_path. Skipping."
    fi
}

# --- Main Execution ---

log "🚀 Starting Analysis & Catalyst Pipeline..."

# 1. Analyst Ratings
# Summarizing grades and consensus
run_task "analysts/main.py"

# 2. Text Analysis & AI Summaries
# This is likely the heaviest step (LLM processing?)
run_task "earnings_transcripts/main.py"

# 3. Signals (Currently Disabled)
# Easy to uncomment when ready:
# run_task "signals/main.py"

# 4. Catalyst Detection
# Identifying upcoming events or triggers
run_task "catalysts/main.py"

log "✅ Analysis Job completed successfully."