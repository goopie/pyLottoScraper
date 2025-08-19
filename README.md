# PyLottoScraper

A Python-based lottery data scraper and analyzer for Canadian Lotto 6/49 and LottoMax draws.

## Features

- Scrapes historical lottery data from official Canadian lottery websites
- Stores data in SQLite database for fast analysis
- Calculates most/least frequently drawn numbers
- Generates 5 optimal lottery entries based on frequency analysis
- Supports both Lotto 6/49 and LottoMax

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Load sample data for testing:**
   ```bash
   python sample_data_loader.py
   ```

3. **Run frequency analysis:**
   ```bash
   python lottery_analyzer.py
   ```

4. **Scrape real data (optional):**
   ```bash
   python lottery_scraper.py
   ```

## Files

- `lottery_scraper.py` - Main scraper for collecting lottery data from websites
- `lottery_analyzer.py` - Analyzes frequency and generates optimal entries
- `sample_data_loader.py` - Loads sample data for testing (20 years of simulated draws)
- `requirements.txt` - Python dependencies
- `lottery_results.db` - SQLite database (created automatically)

## Database Schema

### lotto649_results
- `draw_date` - Date of the draw
- `draw_number` - Sequential draw number
- `numbers` - Comma-separated winning numbers (6 numbers)
- `bonus_number` - Bonus number
- `jackpot_amount` - Jackpot amount in dollars

### lottomax_results
- `draw_date` - Date of the draw
- `draw_number` - Sequential draw number
- `numbers` - Comma-separated winning numbers (7 numbers)
- `bonus_number` - Bonus number
- `jackpot_amount` - Jackpot amount in dollars
- `maxmillions_count` - Number of MaxMillions prizes

## Analysis Output

The analyzer provides:
- Most frequent numbers (hot numbers)
- Least frequent numbers (cold numbers)
- 5 optimal lottery entries using different strategies:
  1. Hot numbers strategy
  2. Balanced strategy (mix of hot/cold)
  3. Cold numbers strategy
  4. Random strategy
  5. Hot numbers strategy (variant)

## Note

The web scraper is designed to work with official Canadian lottery websites. Please be respectful of their terms of service and implement appropriate delays between requests.