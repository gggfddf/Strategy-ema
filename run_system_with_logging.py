#!/usr/bin/env python3
"""
Run the trading strategy system with comprehensive logging
"""

import sys
import os
import logging
import subprocess
from pathlib import Path
from datetime import datetime

def setup_logging():
    """Setup comprehensive logging"""
    # Create logs directory
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Create timestamp for log file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = logs_dir / f"system_run_{timestamp}.log"
    
    # Setup logging configuration
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info(f"Starting system run at {timestamp}")
    logger.info(f"Log file: {log_file}")
    
    return logger, log_file

def prepare_data():
    """Prepare the data file"""
    print("="*60)
    print("PREPARING DATA FILE")
    print("="*60)
    
    try:
        # Read the original data
        import pandas as pd
        
        # Read the data file
        data_file = Path("data/raw/xauusd_data.csv")
        if not data_file.exists():
            print("❌ Data file not found!")
            return False
            
        print(f"Reading data from: {data_file}")
        df = pd.read_csv(data_file, sep='\t')  # Tab-separated
        
        print(f"Original data shape: {df.shape}")
        print(f"Original columns: {list(df.columns)}")
        
        # Standardize column names
        column_mapping = {
            '<DATE>': 'date',
            '<TIME>': 'time', 
            '<OPEN>': 'open',
            '<HIGH>': 'high',
            '<LOW>': 'low',
            '<CLOSE>': 'close',
            '<TICKVOL>': 'tickvol',
            '<VOL>': 'volume',
            '<SPREAD>': 'spread'
        }
        
        df = df.rename(columns=column_mapping)
        
        # Combine date and time
        df['timestamp'] = pd.to_datetime(df['date'] + ' ' + df['time'])
        
        # Select required columns
        required_columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        df = df[required_columns]
        
        # Sort by timestamp
        df = df.sort_values('timestamp')
        
        # Save standardized data
        output_file = Path("data/raw/xauusd_data_standardized.csv")
        df.to_csv(output_file, index=False)
        
        print(f"✅ Data prepared successfully!")
        print(f"   Final shape: {df.shape}")
        print(f"   Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
        print(f"   Saved to: {output_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error preparing data: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_system():
    """Run the trading strategy system"""
    print("\n" + "="*60)
    print("RUNNING TRADING STRATEGY SYSTEM")
    print("="*60)
    
    try:
        # Run the main system
        result = subprocess.run(
            [sys.executable, "main.py"],
            capture_output=True,
            text=True,
            timeout=3600  # 1 hour timeout
        )
        
        print("System execution completed!")
        print(f"Return code: {result.returncode}")
        
        if result.stdout:
            print("\nSTDOUT:")
            print(result.stdout)
            
        if result.stderr:
            print("\nSTDERR:")
            print(result.stderr)
            
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("❌ System execution timed out after 1 hour")
        return False
    except Exception as e:
        print(f"❌ Error running system: {e}")
        return False

def main():
    """Main execution"""
    # Setup logging
    logger, log_file = setup_logging()
    
    print("TRADING STRATEGY SYSTEM - COMPREHENSIVE RUN")
    print("="*60)
    print(f"Log file: {log_file}")
    print("="*60)
    
    # Step 1: Prepare data
    if not prepare_data():
        print("❌ Data preparation failed!")
        return False
    
    # Step 2: Run system
    success = run_system()
    
    if success:
        print("\n" + "="*60)
        print("✅ SYSTEM RUN COMPLETED SUCCESSFULLY!")
        print("="*60)
        print(f"📊 Check results in: results/")
        print(f"📝 Check logs in: {log_file}")
    else:
        print("\n" + "="*60)
        print("❌ SYSTEM RUN FAILED!")
        print("="*60)
        print(f"📝 Check logs in: {log_file}")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)