#!/usr/bin/env python3
"""
Analyze the trading strategy results and show what's happening
"""

import pandas as pd
import numpy as np
import sys
from pathlib import Path

def analyze_strategy_performance():
    """Analyze the actual strategy performance"""
    print("="*80)
    print("TRADING STRATEGY PERFORMANCE ANALYSIS")
    print("="*80)
    
    # Check if we have backtest results
    try:
        # Try to load the Excel file
        excel_file = Path("results/trading_strategy_results.xlsx")
        if excel_file.exists():
            print(f"Found results file: {excel_file}")
            
            # Try to read all sheets
            with pd.ExcelFile(excel_file) as xls:
                sheets = xls.sheet_names
                print(f"Available sheets: {sheets}")
                
                for sheet in sheets:
                    try:
                        df = pd.read_excel(excel_file, sheet_name=sheet)
                        print(f"\nSheet '{sheet}': {df.shape}")
                        if not df.empty:
                            print(f"Columns: {list(df.columns)}")
                            print(f"First few rows:")
                            print(df.head())
                    except Exception as e:
                        print(f"Error reading sheet '{sheet}': {e}")
        else:
            print("No results file found")
            
    except Exception as e:
        print(f"Error analyzing results: {e}")
    
    # Check the backtest data directly
    print("\n" + "="*80)
    print("CHECKING BACKTEST DATA")
    print("="*80)
    
    try:
        # Import the backtester to check results
        sys.path.append('src')
        from evaluation.backtester import Backtester
        from strategies.ma_single import SingleMAStrategyGenerator
        from data.loader import DataLoader
        from data.timeframe_generator import TimeframeGenerator
        from data.feature_engineer import FeatureEngineer
        
        # Load data
        loader = DataLoader()
        data = loader.get_combined_data()
        
        # Generate timeframes
        tf_generator = TimeframeGenerator()
        timeframe_data = tf_generator.generate_all_timeframes(data)
        
        # Engineer features
        feature_engineer = FeatureEngineer()
        enhanced_data = feature_engineer.compute_all_moving_averages(timeframe_data)
        
        # Generate a few simple strategies
        generator = SingleMAStrategyGenerator()
        strategies = generator.generate_strategies(enhanced_data)
        
        print(f"Generated {len(strategies)} strategies")
        
        # Test a few strategies manually
        backtester = Backtester()
        
        for i, strategy in enumerate(strategies[:5]):  # Test first 5
            print(f"\nTesting strategy {i+1}: {strategy.strategy_name}")
            
            try:
                # Get data for this strategy's timeframe
                tf_name = strategy.parameters.get('timeframe', 'M1')
                if tf_name in enhanced_data:
                    data = enhanced_data[tf_name]
                    print(f"  Data shape: {data.shape}")
                    
                    # Generate signals
                    signals = strategy.generate_signals(data)
                    print(f"  Signals shape: {signals.shape}")
                    print(f"  Signal values: {signals.value_counts()}")
                    
                    # Backtest
                    result = backtester.backtest_single_strategy(strategy, data)
                    print(f"  Backtest result:")
                    print(f"    Total Return: {result.metrics.get('total_return', 'N/A')}")
                    print(f"    Win Rate: {result.metrics.get('win_rate', 'N/A')}")
                    print(f"    Sharpe Ratio: {result.metrics.get('sharpe_ratio', 'N/A')}")
                    print(f"    Max Drawdown: {result.metrics.get('max_drawdown', 'N/A')}")
                    print(f"    Profit Factor: {result.metrics.get('profit_factor', 'N/A')}")
                    print(f"    Number of Trades: {result.metrics.get('num_trades', 'N/A')}")
                    
                else:
                    print(f"  No data for timeframe {tf_name}")
                    
            except Exception as e:
                print(f"  Error testing strategy: {e}")
                
    except Exception as e:
        print(f"Error in analysis: {e}")

if __name__ == "__main__":
    analyze_strategy_performance()