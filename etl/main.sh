#!/bin/bash
# Exit immediately if a script fails
set -e

echo "🚀 Starting Winsanity ETL Pipeline..."

# 1. Extract
bash ./etl/extract/run_extract.sh

# 2. Load
bash ./etl/load/run_load.sh

# 3. Transform
bash ./etl/transform/run_transform.sh

# 4. Analysis
bash ./etl/analysis/run_analysis.sh

# 5. Publish
bash ./etl/publish/run_publish.sh

echo "✅ ETL Pipeline Completed Successfully!"