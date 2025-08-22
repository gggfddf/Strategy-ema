#!/usr/bin/env python3
"""
Show all strategy results in a simple way
"""

import pandas as pd
import numpy as np
from pathlib import Path

def show_results_simple_final():
    """Show all results in a simple way"""
    print("="*80)
    print("ALL 960 STRATEGY RESULTS (NO FILTERING)")
    print("="*80)
    
    # Check if we have any results files
    results_dir = Path("results")
    
    # Check Excel file
    excel_file = results_dir / "trading_strategy_results.xlsx"
    if excel_file.exists():
        print(f"Found Excel file: {excel_file}")
        try:
            with pd.ExcelFile(excel_file) as xls:
                sheets = xls.sheet_names
                print(f"Available sheets: {sheets}")
                
                for sheet in sheets:
                    df = pd.read_excel(excel_file, sheet_name=sheet)
                    print(f"\nSheet: {sheet}")
                    print(f"Shape: {df.shape}")
                    if not df.empty:
                        print("First 10 rows:")
                        print(df.head(10).to_string())
                    else:
                        print("Sheet is empty")
                        
        except Exception as e:
            print(f"Error reading Excel file: {e}")
    
    # Check CSV files
    csv_files = list(results_dir.glob("*.csv"))
    if csv_files:
        print(f"\nFound CSV files: {csv_files}")
        for csv_file in csv_files:
            try:
                df = pd.read_csv(csv_file)
                print(f"\nFile: {csv_file.name}")
                print(f"Shape: {df.shape}")
                if not df.empty:
                    print("First 10 rows:")
                    print(df.head(10).to_string())
                else:
                    print("File is empty")
            except Exception as e:
                print(f"Error reading {csv_file}: {e}")
    
    # Check parquet files
    parquet_files = list(results_dir.glob("*.parquet"))
    if parquet_files:
        print(f"\nFound parquet files: {parquet_files}")
        for parquet_file in parquet_files:
            try:
                df = pd.read_parquet(parquet_file)
                print(f"\nFile: {parquet_file.name}")
                print(f"Shape: {df.shape}")
                if not df.empty:
                    print("First 10 rows:")
                    print(df.head(10).to_string())
                else:
                    print("File is empty")
            except Exception as e:
                print(f"Error reading {parquet_file}: {e}")
    
    # If no results found, create a simple analysis
    if not excel_file.exists() and not csv_files and not parquet_files:
        print("\nNo results files found. Creating simple analysis...")
        
        # Create a simple analysis of what we have
        print("\nChecking data files...")
        
        # Check processed data
        processed_dir = Path("data/processed")
        if processed_dir.exists():
            parquet_files = list(processed_dir.glob("*.parquet"))
            print(f"Found {len(parquet_files)} processed data files")
            
            for parquet_file in parquet_files:
                try:
                    df = pd.read_parquet(parquet_file)
                    print(f"{parquet_file.name}: {df.shape}")
                except Exception as e:
                    print(f"Error reading {parquet_file}: {e}")
        
        # Check raw data
        raw_dir = Path("data/raw")
        if raw_dir.exists():
            csv_files = list(raw_dir.glob("*.csv"))
            print(f"\nFound {len(csv_files)} raw data files")
            
            for csv_file in csv_files:
                try:
                    df = pd.read_csv(csv_file)
                    print(f"{csv_file.name}: {df.shape}")
                except Exception as e:
                    print(f"Error reading {csv_file}: {e}")

if __name__ == "__main__":
    show_results_simple_final()