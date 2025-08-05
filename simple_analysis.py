#!/usr/bin/env python3
"""
Simple analysis of the trading strategy results
"""

import pandas as pd
import numpy as np
from pathlib import Path

def simple_analysis():
    """Simple analysis of results"""
    print("="*80)
    print("SIMPLE TRADING STRATEGY ANALYSIS")
    print("="*80)
    
    # Check the data files
    print("Checking data files...")
    
    data_files = [
        "data/raw/xauusd_data.csv",
        "data/raw/xauusd_data_standardized.csv"
    ]
    
    for file_path in data_files:
        path = Path(file_path)
        if path.exists():
            try:
                df = pd.read_csv(path)
                print(f"✅ {file_path}: {df.shape}")
                print(f"   Columns: {list(df.columns)}")
                print(f"   Date range: {df.iloc[0, 0]} to {df.iloc[-1, 0]}")
                print(f"   Price range: {df.iloc[:, 2].min():.2f} to {df.iloc[:, 2].max():.2f}")
            except Exception as e:
                print(f"❌ {file_path}: Error - {e}")
        else:
            print(f"❌ {file_path}: Not found")
    
    # Check processed data
    print("\nChecking processed data...")
    processed_dir = Path("data/processed")
    if processed_dir.exists():
        parquet_files = list(processed_dir.glob("*.parquet"))
        print(f"Found {len(parquet_files)} processed files:")
        for file in parquet_files[:5]:  # Show first 5
            print(f"  - {file.name}")
    
    # Check results
    print("\nChecking results...")
    results_dir = Path("results")
    if results_dir.exists():
        files = list(results_dir.glob("*"))
        print(f"Found {len(files)} result files:")
        for file in files:
            print(f"  - {file.name} ({file.stat().st_size} bytes)")
    
    # Try to read the Excel file
    print("\nAnalyzing Excel results...")
    excel_file = Path("results/trading_strategy_results.xlsx")
    if excel_file.exists():
        try:
            with pd.ExcelFile(excel_file) as xls:
                sheets = xls.sheet_names
                print(f"Excel sheets: {sheets}")
                
                for sheet in sheets:
                    df = pd.read_excel(excel_file, sheet_name=sheet)
                    print(f"  Sheet '{sheet}': {df.shape}")
                    if not df.empty:
                        print(f"    Columns: {list(df.columns)}")
                        print(f"    Sample data:")
                        print(df.head())
                    else:
                        print(f"    Empty sheet")
        except Exception as e:
            print(f"Error reading Excel: {e}")
    
    # Check logs
    print("\nChecking logs...")
    logs_dir = Path("logs")
    if logs_dir.exists():
        log_files = list(logs_dir.glob("*.log"))
        print(f"Found {len(log_files)} log files:")
        for log_file in log_files:
            print(f"  - {log_file.name} ({log_file.stat().st_size} bytes)")
            
            # Read last few lines of the most recent log
            try:
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                    print(f"    Last 5 lines:")
                    for line in lines[-5:]:
                        print(f"      {line.strip()}")
            except Exception as e:
                print(f"    Error reading log: {e}")

if __name__ == "__main__":
    simple_analysis()