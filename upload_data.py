"""
Data upload helper for Trading Strategy Discovery System
"""

import shutil
import os
from pathlib import Path
import pandas as pd
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def prepare_data_file():
    """Help user prepare their data file for the system"""
    
    print("="*60)
    print("TRADING STRATEGY DISCOVERY SYSTEM - DATA PREPARATION")
    print("="*60)
    
    # Check if data file exists in current directory
    possible_files = [
        "xauusd data.csv",
        "xauusd_data.csv", 
        "xauusddata.csv",
        "data.csv",
        "XAUUSD.csv",
        "gold.csv"
    ]
    
    found_file = None
    for file in possible_files:
        if os.path.exists(file):
            found_file = file
            break
    
    if found_file:
        print(f"Found data file: {found_file}")
        
        # Create data/raw directory if it doesn't exist
        data_dir = Path("data/raw")
        data_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy file to data/raw directory
        destination = data_dir / "xauusd_data.csv"
        shutil.copy2(found_file, destination)
        
        print(f"Copied {found_file} to {destination}")
        
        # Validate the data
        try:
            df = pd.read_csv(destination)
            print(f"\nData validation:")
            print(f"  Shape: {df.shape}")
            print(f"  Columns: {list(df.columns)}")
            print(f"  Date range: {df.iloc[0, 0]} to {df.iloc[-1, 0]}")
            
            # Check if we need to standardize column names
            required_cols = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
            current_cols = list(df.columns)
            
            if not all(col in current_cols for col in required_cols):
                print(f"\nStandardizing column names...")
                # Common column name variations
                column_mapping = {
                    'date': 'timestamp',
                    'time': 'timestamp', 
                    'datetime': 'timestamp',
                    'o': 'open',
                    'h': 'high',
                    'l': 'low',
                    'c': 'close',
                    'v': 'volume',
                    'vol': 'volume'
                }
                
                # Rename columns if they exist
                for old_name, new_name in column_mapping.items():
                    if old_name in df.columns:
                        df = df.rename(columns={old_name: new_name})
                
                # Save standardized file
                df.to_csv(destination, index=False)
                print(f"Standardized column names and saved to {destination}")
            
            print(f"\n✅ Data file ready for processing!")
            print(f"File location: {destination}")
            
        except Exception as e:
            print(f"Error validating data: {e}")
            return False
            
    else:
        print("No data file found in current directory.")
        print("\nPlease ensure your data file is in the current directory.")
        print("Expected file names:")
        for file in possible_files:
            print(f"  - {file}")
        print("\nOr upload your file manually to the data/raw/ directory.")
        return False
    
    return True

def main():
    """Main function"""
    try:
        success = prepare_data_file()
        if success:
            print("\n" + "="*60)
            print("DATA PREPARATION COMPLETED!")
            print("="*60)
            print("\nYou can now run the trading strategy discovery system:")
            print("python main.py")
            print("\nThe system will:")
            print("1. Load your XAUUSD data")
            print("2. Generate all timeframes")
            print("3. Compute 600 moving averages")
            print("4. Discover top 20 strategies in each category")
            print("5. Save all results in Excel format")
            print("\nResults will be saved in:")
            print("- results/trading_strategy_results.xlsx (Excel file)")
            print("- results/ (charts and reports)")
        else:
            print("\n❌ Data preparation failed. Please check your data file.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()