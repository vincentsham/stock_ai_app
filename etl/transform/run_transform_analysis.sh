#!/bin/bash

# Activate your Python environment if needed
# source /path/to/venv/bin/activate

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# echo "Running analyst ratings summary computation..."
# python "$SCRIPT_DIR/analysts/main.py"

echo "Running earnings transcript analysis..."
python "$SCRIPT_DIR/earnings_transcripts/main.py"

# echo "Running signal classification for news and earnings transcripts..."
# python "$SCRIPT_DIR/signals/main.py"

echo "Running catalyst pipeline..."
python "$SCRIPT_DIR/catalysts/main.py"