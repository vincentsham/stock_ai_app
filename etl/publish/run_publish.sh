# Activate your Python environment if needed
# source /path/to/venv/bin/activate

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Running publish_analyst_rating_yearly_summary.py..."
python "$SCRIPT_DIR/publish_analyst_rating_yearly_summary.py"

echo "Running publish_catalyst_master.py..."
python "$SCRIPT_DIR/publish_catalyst_master.py"

echo "Running publish_earnings.py..."
python "$SCRIPT_DIR/publish_earnings.py"

echo "Running publish_earnings_regime.py..."
python "$SCRIPT_DIR/publish_earnings_regime.py"

echo "Running publish_earnings_transcript_analysis.py..."
python "$SCRIPT_DIR/publish_earnings_transcript_analysis.py"

echo "Running publish_efficiency_metrics.py..."
python "$SCRIPT_DIR/publish_efficiency_metrics.py"

echo "Running publish_financial_health_metrics.py..."
python "$SCRIPT_DIR/publish_financial_health_metrics.py"

echo "Running publish_growth_metrics.py..."
python "$SCRIPT_DIR/publish_growth_metrics.py"

echo "Running publish_profitability_metrics.py..."
python "$SCRIPT_DIR/publish_profitability_metrics.py"

echo "Running publish_stock_profiles.py..."
python "$SCRIPT_DIR/publish_stock_profiles.py"

echo "Running publish_stock_scores.py..."
python "$SCRIPT_DIR/publish_stock_scores.py"

echo "Running publish_valuation_metrics.py..."
python "$SCRIPT_DIR/publish_valuation_metrics.py"
