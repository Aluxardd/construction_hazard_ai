#!/usr/bin/env bash
# Quick start script for Construction Safety AI

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================================="
echo " Starting Construction Hazard AI Web Application..."
echo "=========================================================="

# Check if streamlit is available
if ! command -v streamlit &> /dev/null
then
    echo "Streamlit not found in standard PATH. Trying python3 -m streamlit..."
    python3 -m streamlit run app.py
else
    streamlit run app.py
fi
