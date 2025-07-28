#!/bin/bash

# Semiconductor Learning System - Streamlit Demo Launcher
# This script sets up and launches the Streamlit demo application

echo "🔬 Semiconductor Learning System - Streamlit Demo"
echo "=================================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/upgrade requirements
echo "📥 Installing requirements..."
pip install -r requirements.txt

# Initialize system if needed
echo "🔄 Initializing system..."
python3 main_simple.py init --force

# Launch Streamlit demo
echo "🚀 Launching Streamlit demo..."
echo "📱 The demo will open in your browser at: http://localhost:8501"
echo "💡 Use Ctrl+C to stop the demo"
echo ""

streamlit run streamlit_demo.py --server.port 8501 --server.address localhost
