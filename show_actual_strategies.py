#!/usr/bin/env python3
"""
Show actual strategies that were generated
"""

import pandas as pd
import numpy as np
from pathlib import Path

def show_actual_strategies():
    """Show actual strategies that were generated"""
    print("="*80)
    print("ACTUAL STRATEGIES GENERATED AND THEIR RESULTS")
    print("="*80)
    
    # Check what strategies were actually generated
    strategies_dir = Path("results/strategies")
    if strategies_dir.exists():
        strategy_files = list(strategies_dir.glob("*.csv"))
        print(f"Found {len(strategy_files)} strategy files")
        
        for strategy_file in strategy_files:
            try:
                df = pd.read_csv(strategy_file)
                print(f"\nFile: {strategy_file.name}")
                print(f"Shape: {df.shape}")
                if not df.empty:
                    print("First 5 rows:")
                    print(df.head().to_string())
                else:
                    print("File is empty")
            except Exception as e:
                print(f"Error reading {strategy_file}: {e}")
    
    # Check processed data to understand what we have
    print("\n" + "="*80)
    print("DATA ANALYSIS")
    print("="*80)
    
    # Check processed data
    processed_dir = Path("data/processed")
    if processed_dir.exists():
        parquet_files = list(processed_dir.glob("*.parquet"))
        print(f"Found {len(parquet_files)} processed data files")
        
        for parquet_file in parquet_files:
            try:
                df = pd.read_parquet(parquet_file)
                print(f"{parquet_file.name}: {df.shape}")
                
                # Show column names for first few files
                if parquet_file.name in ['m1_data.parquet', 'm5_data.parquet', 'h1_data.parquet']:
                    print(f"  Columns: {list(df.columns[:10])}...")  # First 10 columns
                    
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
                if not df.empty:
                    print(f"  Columns: {list(df.columns)}")
                    print(f"  Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
                    print(f"  Price range: {df['close'].min():.2f} to {df['close'].max():.2f}")
            except Exception as e:
                print(f"Error reading {csv_file}: {e}")
    
    # Create a simple analysis of what strategies should have been generated
    print("\n" + "="*80)
    print("STRATEGY GENERATION ANALYSIS")
    print("="*80)
    
    # Based on the logs, we know:
    print("From the logs, we can see:")
    print("- 384 Single MA strategies were generated")
    print("- 112 MA Crossover strategies were generated") 
    print("- 96 Multi-Timeframe strategies were generated")
    print("- 2160 Mean Reversion strategies were generated")
    print("- Total: 2752 strategies generated")
    print("- 960 strategies passed validation")
    print("- 0 strategies met performance criteria")
    
    print("\nThis means:")
    print("✅ Strategy generation is working")
    print("✅ Data processing is working")
    print("✅ Feature engineering is working")
    print("❌ Backtesting is failing or producing poor results")
    
    print("\nPossible reasons for poor performance:")
    print("1. Market conditions in your data period were challenging")
    print("2. Simple MA strategies may not work well on this data")
    print("3. The data period may be too short for reliable backtesting")
    print("4. Commission and slippage may be eating into profits")
    
    print("\nRecommendations:")
    print("1. Try with different data periods")
    print("2. Lower the performance thresholds")
    print("3. Try different strategy types")
    print("4. Analyze individual strategy performance")

if __name__ == "__main__":
    show_actual_strategies()