#!/bin/bash

# Navigate to project directory
cd /home/ubuntu/Desktop/LoanApplicationCapstone

# Add local packages to path
export PATH="/home/ubuntu/.local/bin:$PATH"
export PYTHONPATH="/home/ubuntu/Desktop/LoanApplicationCapstone:$PYTHONPATH"

# Start Streamlit
streamlit run ui/app.py --server.port 8501 --server.address 0.0.0.0
