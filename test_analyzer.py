#!/usr/bin/env python3
"""
Test the lottery analyzer with existing sample data
"""

import sys
import os

# Check if database exists
if not os.path.exists("lottery_results.db"):
    print("Database not found. Loading sample data first...")
    os.system("python3 sample_data_loader.py")

# Run the analyzer
print("Running lottery analysis...")
os.system("python3 lottery_analyzer.py")