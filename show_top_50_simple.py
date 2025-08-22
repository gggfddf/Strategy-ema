#!/usr/bin/env python3
"""
Show top 50 strategies from the 960 tested - Simple version
"""

import pandas as pd
import numpy as np
import subprocess
import sys
from pathlib import Path

def show_top_50_simple():
    """Show top 50 strategies by running the main system with relaxed criteria"""
    print("="*80)
    print("TOP 50 TRADING STRATEGIES FROM 960 TESTED")
    print("="*80)
    
    # First, let's modify the settings to be very relaxed
    print("Modifying settings to show all strategies...")
    
    # Create a temporary settings file with very relaxed criteria
    relaxed_settings = '''
# Performance thresholds - Very relaxed to show all strategies
MIN_WIN_RATE = 0.1  # 10% win rate
MIN_PROFIT_FACTOR = 0.5  # Allow significant losses
MAX_DRAWDOWN = 0.8  # Allow up to 80% drawdown
MIN_SHARPE_RATIO = -2.0  # Allow negative Sharpe ratios
TOP_STRATEGIES_PER_CATEGORY = 50  # Show top 50 per category
'''
    
    # Save the relaxed settings
    with open('config/settings_relaxed.py', 'w') as f:
        f.write(relaxed_settings)
    
    # Now run the main system with relaxed criteria
    print("Running system with relaxed criteria...")
    
    try:
        # Run the main system
        result = subprocess.run([sys.executable, 'main.py'], 
                              capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("✅ System completed successfully!")
            
            # Check the results
            excel_file = Path("results/trading_strategy_results.xlsx")
            if excel_file.exists():
                print(f"\nReading results from: {excel_file}")
                
                with pd.ExcelFile(excel_file) as xls:
                    sheets = xls.sheet_names
                    print(f"Available sheets: {sheets}")
                    
                    for sheet in sheets:
                        df = pd.read_excel(excel_file, sheet_name=sheet)
                        print(f"\nSheet '{sheet}': {df.shape}")
                        if not df.empty:
                            print("Top 10 strategies:")
                            print(df.head(10).to_string())
                        else:
                            print("Empty sheet")
                            
        else:
            print("❌ System failed!")
            print("Error output:")
            print(result.stderr)
            
    except subprocess.TimeoutExpired:
        print("❌ System timed out")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Also try to read any CSV files that might have results
    print("\n" + "="*80)
    print("CHECKING FOR RESULTS FILES")
    print("="*80)
    
    results_dir = Path("results")
    csv_files = list(results_dir.glob("*.csv"))
    
    for csv_file in csv_files:
        try:
            df = pd.read_csv(csv_file)
            print(f"\nFile: {csv_file.name}")
            print(f"Shape: {df.shape}")
            if not df.empty:
                print("Columns:", list(df.columns))
                print("Top 10 rows:")
                print(df.head(10).to_string())
            else:
                print("Empty file")
        except Exception as e:
            print(f"Error reading {csv_file}: {e}")

if __name__ == "__main__":
    show_top_50_simple()