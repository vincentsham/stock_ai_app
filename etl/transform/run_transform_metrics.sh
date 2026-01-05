#!/bin/bash

# Activate your Python environment if needed
# source /path/to/venv/bin/activate

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Run earnings metrics transformation
echo "Running earnings metrics transformation main.py..."
python "$SCRIPT_DIR/earnings/main.py"

echo "Running EPS diluted metrics computation..."
python "$SCRIPT_DIR/metrics/profitability/compute_eps_diluted_metrics.py"

echo "Running revenue metrics computation..."
python "$SCRIPT_DIR/metrics/revenue/compute_revenue_metrics.py"

echo "Running valuation metrics computation..."
python "$SCRIPT_DIR/metrics/valuation/compute_valuation_metrics.py"

echo "Running profitability metrics computation..."
python "$SCRIPT_DIR/metrics/profitability/compute_profitability_metrics.py"

echo "Running growth metrics computation..."
python "$SCRIPT_DIR/metrics/growth/compute_growth_metrics.py"

echo "Running efficiency metrics computation..."
python "$SCRIPT_DIR/metrics/efficiency/compute_efficiency_metrics.py"

echo "Running financial health metrics computation..."
python "$SCRIPT_DIR/metrics/financial_health/compute_financial_health_metrics.py"

echo "Running percentiles computation..."
python "$SCRIPT_DIR/metrics/percentiles/compute_percentiles.py"

echo "Running stock scores computation..."
python "$SCRIPT_DIR/metrics/stock_scores/compute_stock_scores.py"



