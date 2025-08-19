#!/usr/bin/env python3
"""
Setup script for PyLottoScraper
Installs dependencies and loads sample data for immediate testing.
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    print("Installing required packages...")
    try:
        # Try installing with --user flag first
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", "-r", "requirements.txt"])
        print("✓ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("Note: Some packages may already be installed or require virtual environment")
        print("If you get import errors, try:")
        print("  python3 -m venv venv")
        print("  source venv/bin/activate")
        print("  pip install -r requirements.txt")
        return True

def load_sample_data():
    """Load sample data for testing"""
    print("Loading sample lottery data...")
    try:
        subprocess.check_call([sys.executable, "sample_data_loader.py"])
        print("✓ Sample data loaded successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error loading sample data: {e}")
        return False

def main():
    print("PyLottoScraper Setup")
    print("=" * 30)
    
    # Check if we're in the right directory
    required_files = ["lottery_scraper.py", "lottery_analyzer.py", "requirements.txt"]
    for file in required_files:
        if not os.path.exists(file):
            print(f"✗ Required file not found: {file}")
            print("Please run this script from the PyLottoScraper directory")
            sys.exit(1)
    
    # Install dependencies
    if not install_requirements():
        sys.exit(1)
    
    # Load sample data
    if not load_sample_data():
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("✓ Setup complete!")
    print("\nNext steps:")
    print("  python3 lottery_analyzer.py  - Run frequency analysis")
    print("  python3 lottery_scraper.py   - Scrape real lottery data")

if __name__ == "__main__":
    main()