#!/usr/bin/env python3
"""
Lottery Data Scraper for Lotto 6/49 and LottoMax
Scrapes historical draw results from Canadian lottery websites and stores them in SQLite database.
"""

import sqlite3
import json
import time
import re
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
import logging

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError as e:
    print(f"Missing required packages: {e}")
    print("Please install with: pip install requests beautifulsoup4 lxml")
    print("Or run: python3 setup.py")
    exit(1)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class LotteryScraper:
    def __init__(self, db_path: str = "lottery_results.db"):
        self.db_path = db_path
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.setup_database()
    
    def setup_database(self):
        """Create SQLite database and tables for lottery results"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create table for Lotto 6/49 results
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS lotto649_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                draw_date DATE NOT NULL,
                draw_number INTEGER,
                numbers TEXT NOT NULL,
                bonus_number INTEGER,
                jackpot_amount INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(draw_date, draw_number)
            )
        ''')
        
        # Create table for LottoMax results
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS lottomax_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                draw_date DATE NOT NULL,
                draw_number INTEGER,
                numbers TEXT NOT NULL,
                bonus_number INTEGER,
                jackpot_amount INTEGER,
                maxmillions_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(draw_date, draw_number)
            )
        ''')
        
        conn.commit()
        conn.close()
        logging.info(f"Database setup complete: {self.db_path}")
    
    def get_page_content(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch and parse web page content"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            logging.error(f"Error fetching {url}: {e}")
            return None
    
    def parse_lotto649_results(self, soup: BeautifulSoup) -> List[Dict]:
        """Parse Lotto 6/49 results from OLG website"""
        results = []
        
        # Look for JSON data embedded in script tags
        script_tags = soup.find_all('script')
        for script in script_tags:
            if script.string and 'drawResults' in script.string:
                # Try to extract JSON data from script
                try:
                    json_match = re.search(r'drawResults\s*=\s*(\[.*?\]);', script.string, re.DOTALL)
                    if json_match:
                        draw_data = json.loads(json_match.group(1))
                        for draw in draw_data:
                            if isinstance(draw, dict) and 'drawDate' in draw and 'winningNumbers' in draw:
                                results.append({
                                    'date': draw['drawDate'],
                                    'numbers': draw['winningNumbers'],
                                    'bonus': draw.get('bonusNumber')
                                })
                except (json.JSONDecodeError, KeyError) as e:
                    logging.debug(f"Could not parse JSON from script: {e}")
        
        # Fallback: parse HTML tables if JSON extraction fails
        if not results:
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows[1:]:  # Skip header
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        date_text = cells[0].get_text(strip=True)
                        numbers_text = cells[1].get_text(strip=True)
                        
                        # Extract date
                        date_match = re.search(r'(\d{4}-\d{2}-\d{2})', date_text)
                        if not date_match:
                            date_match = re.search(r'(\w+\s+\d{1,2},\s+\d{4})', date_text)
                            if date_match:
                                try:
                                    parsed_date = datetime.strptime(date_match.group(1), '%B %d, %Y')
                                    date_text = parsed_date.strftime('%Y-%m-%d')
                                except ValueError:
                                    continue
                            else:
                                continue
                        else:
                            date_text = date_match.group(1)
                        
                        # Extract numbers
                        numbers = re.findall(r'\b([1-4]?\d)\b', numbers_text)
                        numbers = [int(n) for n in numbers if 1 <= int(n) <= 49]
                        
                        if len(numbers) >= 6:
                            results.append({
                                'date': date_text,
                                'numbers': numbers[:6],
                                'bonus': numbers[6] if len(numbers) > 6 else None
                            })
        
        return results
    
    def parse_lottomax_results(self, soup: BeautifulSoup) -> List[Dict]:
        """Parse LottoMax results from OLG website"""
        results = []
        
        # Look for JSON data embedded in script tags
        script_tags = soup.find_all('script')
        for script in script_tags:
            if script.string and 'drawResults' in script.string:
                try:
                    json_match = re.search(r'drawResults\s*=\s*(\[.*?\]);', script.string, re.DOTALL)
                    if json_match:
                        draw_data = json.loads(json_match.group(1))
                        for draw in draw_data:
                            if isinstance(draw, dict) and 'drawDate' in draw and 'winningNumbers' in draw:
                                results.append({
                                    'date': draw['drawDate'],
                                    'numbers': draw['winningNumbers'],
                                    'bonus': draw.get('bonusNumber')
                                })
                except (json.JSONDecodeError, KeyError) as e:
                    logging.debug(f"Could not parse JSON from script: {e}")
        
        # Fallback: parse HTML tables if JSON extraction fails
        if not results:
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows[1:]:  # Skip header
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        date_text = cells[0].get_text(strip=True)
                        numbers_text = cells[1].get_text(strip=True)
                        
                        # Extract date
                        date_match = re.search(r'(\d{4}-\d{2}-\d{2})', date_text)
                        if not date_match:
                            date_match = re.search(r'(\w+\s+\d{1,2},\s+\d{4})', date_text)
                            if date_match:
                                try:
                                    parsed_date = datetime.strptime(date_match.group(1), '%B %d, %Y')
                                    date_text = parsed_date.strftime('%Y-%m-%d')
                                except ValueError:
                                    continue
                            else:
                                continue
                        else:
                            date_text = date_match.group(1)
                        
                        # Extract numbers (LottoMax uses 1-50)
                        numbers = re.findall(r'\b([1-5]?\d)\b', numbers_text)
                        numbers = [int(n) for n in numbers if 1 <= int(n) <= 50]
                        
                        if len(numbers) >= 7:
                            results.append({
                                'date': date_text,
                                'numbers': numbers[:7],
                                'bonus': numbers[7] if len(numbers) > 7 else None
                            })
        
        return results
    
    def scrape_olg_lotto649(self, years_back: int = 20) -> List[Dict]:
        """Scrape Lotto 6/49 results from OLG website"""
        logging.info("Scraping Lotto 6/49 results from OLG...")
        
        url = "https://www.olg.ca/en/lottery/play-lotto-649-encore/past-results.html"
        soup = self.get_page_content(url)
        
        if not soup:
            return []
        
        results = self.parse_lotto649_results(soup)
        
        # For demonstration, we'll also try to find any AJAX endpoints or pagination
        # In a real implementation, you'd need to reverse engineer the website's API calls
        
        return results
    
    def scrape_olg_lottomax(self, years_back: int = 20) -> List[Dict]:
        """Scrape LottoMax results from OLG website"""
        logging.info("Scraping LottoMax results from OLG...")
        
        url = "https://www.olg.ca/en/lottery/play-lotto-max-encore/past-results.html"
        soup = self.get_page_content(url)
        
        if not soup:
            return []
        
        results = self.parse_lottomax_results(soup)
        return results
    
    def store_lotto649_results(self, results: List[Dict]):
        """Store Lotto 6/49 results in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for result in results:
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO lotto649_results 
                    (draw_date, numbers, bonus_number) 
                    VALUES (?, ?, ?)
                ''', (
                    result['date'],
                    ','.join(map(str, result['numbers'])),
                    result.get('bonus')
                ))
            except Exception as e:
                logging.error(f"Error storing Lotto 6/49 result: {e}")
        
        conn.commit()
        conn.close()
        logging.info(f"Stored {len(results)} Lotto 6/49 results")
    
    def store_lottomax_results(self, results: List[Dict]):
        """Store LottoMax results in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for result in results:
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO lottomax_results 
                    (draw_date, numbers, bonus_number) 
                    VALUES (?, ?, ?)
                ''', (
                    result['date'],
                    ','.join(map(str, result['numbers'])),
                    result.get('bonus')
                ))
            except Exception as e:
                logging.error(f"Error storing LottoMax result: {e}")
        
        conn.commit()
        conn.close()
        logging.info(f"Stored {len(results)} LottoMax results")
    
    def scrape_all_results(self, years_back: int = 20):
        """Scrape all lottery results and store in database"""
        logging.info(f"Starting lottery data scraping for the last {years_back} years...")
        
        # Scrape Lotto 6/49
        lotto649_results = self.scrape_olg_lotto649(years_back)
        self.store_lotto649_results(lotto649_results)
        
        # Add delay between requests to be respectful
        time.sleep(2)
        
        # Scrape LottoMax
        lottomax_results = self.scrape_olg_lottomax(years_back)
        self.store_lottomax_results(lottomax_results)
        
        logging.info("Scraping completed!")
    
    def get_draw_count(self) -> Tuple[int, int]:
        """Get count of draws stored in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM lotto649_results")
        lotto649_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM lottomax_results")
        lottomax_count = cursor.fetchone()[0]
        
        conn.close()
        return lotto649_count, lottomax_count

def main():
    scraper = LotteryScraper()
    
    # Note: This basic scraper needs to be enhanced with proper HTML parsing
    # for the specific structure of OLG's results pages
    print("Warning: This scraper needs HTML structure analysis for proper data extraction")
    print("Run with caution and verify results manually")
    
    # Uncomment to run scraping
    # scraper.scrape_all_results(20)
    
    lotto649_count, lottomax_count = scraper.get_draw_count()
    print(f"Current database contains:")
    print(f"  Lotto 6/49 draws: {lotto649_count}")
    print(f"  LottoMax draws: {lottomax_count}")

if __name__ == "__main__":
    main()