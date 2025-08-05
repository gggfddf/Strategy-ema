#!/usr/bin/env python3
"""
Simple data preparation script without external dependencies
"""

import csv
from pathlib import Path
from datetime import datetime

def prepare_data():
    """Prepare the data file"""
    print("="*60)
    print("PREPARING DATA FILE")
    print("="*60)
    
    try:
        # Read the original data
        input_file = Path("data/raw/xauusd_data.csv")
        output_file = Path("data/raw/xauusd_data_standardized.csv")
        
        if not input_file.exists():
            print("❌ Data file not found!")
            return False
            
        print(f"Reading data from: {input_file}")
        
        # Read and process the data
        rows = []
        with open(input_file, 'r') as f:
            reader = csv.reader(f, delimiter='\t')
            header = next(reader)  # Skip header
            print(f"Original columns: {header}")
            
            for row in reader:
                if len(row) >= 6:  # Ensure we have enough columns
                    try:
                        # Parse date and time
                        date_str = row[0]
                        time_str = row[1]
                        timestamp = f"{date_str} {time_str}"
                        
                        # Extract OHLCV data
                        open_price = float(row[2])
                        high_price = float(row[3])
                        low_price = float(row[4])
                        close_price = float(row[5])
                        volume = int(row[7]) if len(row) > 7 else 1000  # Default volume
                        
                        # Create standardized row
                        new_row = [
                            timestamp,
                            open_price,
                            high_price,
                            low_price,
                            close_price,
                            volume
                        ]
                        rows.append(new_row)
                        
                    except (ValueError, IndexError) as e:
                        print(f"Warning: Skipping invalid row: {row} - {e}")
                        continue
        
        # Write standardized data
        with open(output_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            writer.writerows(rows)
        
        print(f"✅ Data prepared successfully!")
        print(f"   Processed {len(rows)} rows")
        print(f"   Saved to: {output_file}")
        
        # Show sample of processed data
        print("\nSample of processed data:")
        for i, row in enumerate(rows[:5]):
            print(f"   Row {i+1}: {row}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error preparing data: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main execution"""
    success = prepare_data()
    if success:
        print("\n✅ Data preparation completed!")
        print("You can now run the main system.")
    else:
        print("\n❌ Data preparation failed!")
    
    return success

if __name__ == "__main__":
    success = main()