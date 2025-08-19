#!/usr/bin/env python3
"""
Lottery Number Analyzer
Analyzes frequency of lottery numbers and generates optimal entries based on historical data.
"""

import sqlite3
import random
from collections import Counter
from typing import List, Dict, Tuple
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class LotteryAnalyzer:
    def __init__(self, db_path: str = "lottery_results.db"):
        self.db_path = db_path
    
    def get_all_drawn_numbers(self, lottery_type: str) -> List[List[int]]:
        """Get all drawn numbers for a specific lottery type"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        table_name = f"{lottery_type}_results"
        cursor.execute(f"SELECT numbers FROM {table_name}")
        
        all_draws = []
        for row in cursor.fetchall():
            numbers_str = row[0]
            if numbers_str:
                numbers = [int(n) for n in numbers_str.split(',') if n.strip().isdigit()]
                all_draws.append(numbers)
        
        conn.close()
        return all_draws
    
    def calculate_frequency(self, lottery_type: str) -> Dict[int, int]:
        """Calculate frequency of each number drawn"""
        all_draws = self.get_all_drawn_numbers(lottery_type)
        
        frequency = Counter()
        for draw in all_draws:
            frequency.update(draw)
        
        return dict(frequency)
    
    def get_most_frequent_numbers(self, lottery_type: str, count: int = 10) -> List[Tuple[int, int]]:
        """Get the most frequently drawn numbers"""
        frequency = self.calculate_frequency(lottery_type)
        return sorted(frequency.items(), key=lambda x: x[1], reverse=True)[:count]
    
    def get_least_frequent_numbers(self, lottery_type: str, count: int = 10) -> List[Tuple[int, int]]:
        """Get the least frequently drawn numbers"""
        frequency = self.calculate_frequency(lottery_type)
        return sorted(frequency.items(), key=lambda x: x[1])[:count]
    
    def get_number_ranges(self, lottery_type: str) -> Tuple[int, int]:
        """Get the valid number range for a lottery type"""
        if lottery_type == "lotto649":
            return 1, 49
        elif lottery_type == "lottomax":
            return 1, 50
        else:
            return 1, 49
    
    def generate_frequency_based_entry(self, lottery_type: str, strategy: str = "hot") -> List[int]:
        """Generate lottery entry based on frequency analysis"""
        min_num, max_num = self.get_number_ranges(lottery_type)
        numbers_needed = 6 if lottery_type == "lotto649" else 7
        
        frequency = self.calculate_frequency(lottery_type)
        
        if not frequency:
            # Fallback to random if no data
            return sorted(random.sample(range(min_num, max_num + 1), numbers_needed))
        
        if strategy == "hot":
            # Use most frequent numbers with some randomness
            most_frequent = self.get_most_frequent_numbers(lottery_type, numbers_needed * 2)
            candidates = [num for num, freq in most_frequent]
            
            # Select mix of most frequent + some random for variety
            selected = candidates[:numbers_needed - 1]
            remaining_pool = [n for n in range(min_num, max_num + 1) if n not in selected]
            selected.append(random.choice(remaining_pool))
            
        elif strategy == "cold":
            # Use least frequent numbers
            least_frequent = self.get_least_frequent_numbers(lottery_type, numbers_needed * 2)
            candidates = [num for num, freq in least_frequent]
            selected = candidates[:numbers_needed]
            
        elif strategy == "balanced":
            # Mix of hot and cold numbers
            hot_numbers = self.get_most_frequent_numbers(lottery_type, numbers_needed)
            cold_numbers = self.get_least_frequent_numbers(lottery_type, numbers_needed)
            
            hot_picks = [num for num, freq in hot_numbers[:numbers_needed//2]]
            cold_picks = [num for num, freq in cold_numbers[:numbers_needed//2]]
            
            selected = hot_picks + cold_picks
            
            # Fill remaining slots randomly if needed
            while len(selected) < numbers_needed:
                remaining_pool = [n for n in range(min_num, max_num + 1) if n not in selected]
                selected.append(random.choice(remaining_pool))
        
        elif strategy == "random":
            # Pure random selection
            selected = random.sample(range(min_num, max_num + 1), numbers_needed)
        
        else:
            # Default to balanced strategy
            return self.generate_frequency_based_entry(lottery_type, "balanced")
        
        return sorted(selected)
    
    def generate_optimal_entries(self, lottery_type: str, num_entries: int = 5) -> List[Dict]:
        """Generate optimal lottery entries using different strategies"""
        strategies = ["hot", "balanced", "cold", "random", "hot"]
        entries = []
        
        for i in range(num_entries):
            strategy = strategies[i % len(strategies)]
            numbers = self.generate_frequency_based_entry(lottery_type, strategy)
            
            entries.append({
                "entry_number": i + 1,
                "strategy": strategy,
                "numbers": numbers
            })
        
        return entries
    
    def print_frequency_analysis(self, lottery_type: str):
        """Print frequency analysis for a lottery type"""
        frequency = self.calculate_frequency(lottery_type)
        
        if not frequency:
            print(f"No data available for {lottery_type.upper()}")
            return
        
        print(f"\n=== {lottery_type.upper()} FREQUENCY ANALYSIS ===")
        
        # Most frequent numbers
        most_frequent = self.get_most_frequent_numbers(lottery_type, 10)
        print(f"\nMost Frequent Numbers:")
        for num, freq in most_frequent:
            print(f"  {num:2d}: drawn {freq:3d} times")
        
        # Least frequent numbers
        least_frequent = self.get_least_frequent_numbers(lottery_type, 10)
        print(f"\nLeast Frequent Numbers:")
        for num, freq in least_frequent:
            print(f"  {num:2d}: drawn {freq:3d} times")
        
        # Statistics
        total_draws = len(self.get_all_drawn_numbers(lottery_type))
        print(f"\nTotal draws analyzed: {total_draws}")
        print(f"Total unique numbers: {len(frequency)}")
    
    def print_optimal_entries(self, lottery_type: str):
        """Print 5 optimal lottery entries"""
        entries = self.generate_optimal_entries(lottery_type, 5)
        
        print(f"\n=== {lottery_type.upper()} OPTIMAL ENTRIES ===")
        for entry in entries:
            numbers_str = " - ".join([f"{n:2d}" for n in entry["numbers"]])
            print(f"Entry {entry['entry_number']} ({entry['strategy']:>8s}): {numbers_str}")
    
    def analyze_all(self):
        """Run complete analysis for both lottery types"""
        lottery_types = ["lotto649", "lottomax"]
        
        for lottery_type in lottery_types:
            self.print_frequency_analysis(lottery_type)
            self.print_optimal_entries(lottery_type)
            print("\n" + "="*60)

def main():
    analyzer = LotteryAnalyzer()
    
    print("Lottery Number Frequency Analyzer")
    print("=" * 50)
    
    # Check if we have data
    conn = sqlite3.connect(analyzer.db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT COUNT(*) FROM lotto649_results")
        lotto649_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM lottomax_results")
        lottomax_count = cursor.fetchone()[0]
        
        print(f"Database contains:")
        print(f"  Lotto 6/49 draws: {lotto649_count}")
        print(f"  LottoMax draws: {lottomax_count}")
        
        if lotto649_count == 0 and lottomax_count == 0:
            print("\nNo lottery data found in database.")
            print("Please run lottery_scraper.py first to collect data.")
            return
        
        # Run analysis
        analyzer.analyze_all()
        
    except sqlite3.OperationalError as e:
        print(f"Database error: {e}")
        print("Please run lottery_scraper.py first to set up the database.")
    finally:
        conn.close()

if __name__ == "__main__":
    main()