#!/usr/bin/env python3
"""
Sample Data Loader for Testing
Loads sample lottery data to test the analyzer functionality.
"""

import sqlite3
import random
from datetime import datetime, timedelta
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SampleDataLoader:
    def __init__(self, db_path: str = "lottery_results.db"):
        self.db_path = db_path
        self.setup_database()
    
    def setup_database(self):
        """Create SQLite database and tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
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
    
    def generate_sample_lotto649_data(self, years: int = 20) -> List[Dict]:
        """Generate realistic sample Lotto 6/49 data"""
        results = []
        
        # Lotto 6/49 draws happen twice per week (Wednesday and Saturday)
        start_date = datetime.now() - timedelta(days=years * 365)
        current_date = start_date
        draw_number = 1
        
        # Some numbers that appear more frequently in real data (hot numbers)
        hot_numbers = [7, 13, 20, 23, 31, 34, 38, 42, 45]
        
        while current_date <= datetime.now():
            # Wednesday and Saturday draws
            if current_date.weekday() == 2 or current_date.weekday() == 5:  # Wed=2, Sat=5
                
                # Generate numbers with slight bias toward hot numbers
                numbers = []
                while len(numbers) < 6:
                    if random.random() < 0.3 and hot_numbers:  # 30% chance for hot number
                        num = random.choice(hot_numbers)
                    else:
                        num = random.randint(1, 49)
                    
                    if num not in numbers:
                        numbers.append(num)
                
                numbers.sort()
                bonus = random.randint(1, 49)
                while bonus in numbers:
                    bonus = random.randint(1, 49)
                
                results.append({
                    'date': current_date.strftime('%Y-%m-%d'),
                    'draw_number': draw_number,
                    'numbers': ','.join(map(str, numbers)),
                    'bonus': bonus,
                    'jackpot': random.randint(5000000, 50000000)
                })
                
                draw_number += 1
            
            current_date += timedelta(days=1)
        
        return results
    
    def generate_sample_lottomax_data(self, years: int = 20) -> List[Dict]:
        """Generate realistic sample LottoMax data"""
        results = []
        
        # LottoMax draws happen twice per week (Tuesday and Friday)
        start_date = datetime.now() - timedelta(days=years * 365)
        current_date = start_date
        draw_number = 1
        
        # Hot numbers for LottoMax
        hot_numbers = [7, 14, 21, 28, 33, 39, 42, 46, 49]
        
        while current_date <= datetime.now():
            # Tuesday and Friday draws
            if current_date.weekday() == 1 or current_date.weekday() == 4:  # Tue=1, Fri=4
                
                # Generate 7 numbers with slight bias toward hot numbers
                numbers = []
                while len(numbers) < 7:
                    if random.random() < 0.25 and hot_numbers:  # 25% chance for hot number
                        num = random.choice(hot_numbers)
                    else:
                        num = random.randint(1, 50)
                    
                    if num not in numbers:
                        numbers.append(num)
                
                numbers.sort()
                bonus = random.randint(1, 50)
                while bonus in numbers:
                    bonus = random.randint(1, 50)
                
                results.append({
                    'date': current_date.strftime('%Y-%m-%d'),
                    'draw_number': draw_number,
                    'numbers': ','.join(map(str, numbers)),
                    'bonus': bonus,
                    'jackpot': random.randint(10000000, 70000000),
                    'maxmillions': random.randint(0, 10) if random.random() < 0.3 else 0
                })
                
                draw_number += 1
            
            current_date += timedelta(days=1)
        
        return results
    
    def load_sample_data(self):
        """Load sample data into database"""
        logging.info("Generating and loading sample lottery data...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Generate and load Lotto 6/49 data
        lotto649_data = self.generate_sample_lotto649_data(20)
        for result in lotto649_data:
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO lotto649_results 
                    (draw_date, draw_number, numbers, bonus_number, jackpot_amount) 
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    result['date'],
                    result['draw_number'],
                    result['numbers'],
                    result['bonus'],
                    result['jackpot']
                ))
            except Exception as e:
                logging.error(f"Error loading Lotto 6/49 sample data: {e}")
        
        # Generate and load LottoMax data
        lottomax_data = self.generate_sample_lottomax_data(20)
        for result in lottomax_data:
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO lottomax_results 
                    (draw_date, draw_number, numbers, bonus_number, jackpot_amount, maxmillions_count) 
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    result['date'],
                    result['draw_number'],
                    result['numbers'],
                    result['bonus'],
                    result['jackpot'],
                    result['maxmillions']
                ))
            except Exception as e:
                logging.error(f"Error loading LottoMax sample data: {e}")
        
        conn.commit()
        conn.close()
        
        logging.info(f"Sample data loaded: {len(lotto649_data)} Lotto 6/49 draws, {len(lottomax_data)} LottoMax draws")

def main():
    loader = SampleDataLoader()
    loader.load_sample_data()
    
    print("Sample lottery data has been loaded into the database.")
    print("You can now run lottery_analyzer.py to see frequency analysis and optimal entries.")

if __name__ == "__main__":
    main()