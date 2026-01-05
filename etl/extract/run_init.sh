#!/bin/bash

# Activate your Python environment if needed
# source /path/to/venv/bin/activate

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Running extract_stock_profiles_yf.py..."
python "$SCRIPT_DIR/stocks/extract_stock_profiles_yf.py"

echo "Running company profile transformation main.py..."
python "$SCRIPT_DIR/../transform/company_profiles/main.py"
