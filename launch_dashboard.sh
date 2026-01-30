#!/bin/bash
# Launch Car Valuation Dashboard

echo "🚗 Starting Car Valuation Dashboard..."
echo ""

# Activate virtual environment
source venv/bin/activate

# Launch Streamlit
streamlit run dashboard.py --server.port 8501 --server.headless false

# Deactivate when done
deactivate
