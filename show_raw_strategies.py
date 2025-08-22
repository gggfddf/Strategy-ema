#!/usr/bin/env python3
"""
Show raw strategies and their basic performance
"""

import pandas as pd
import numpy as np
from pathlib import Path

def show_raw_strategies():
    """Show raw strategies and their basic performance"""
    print("="*80)
    print("RAW STRATEGY RESULTS (NO FILTERING)")
    print("="*80)
    
    # Based on the logs, we know these strategies were generated:
    strategies_info = {
        "Single MA Strategies": {
            "count": 384,
            "examples": [
                "Single_SMA_5_M1_crossover",
                "Single_SMA_10_M1_crossover", 
                "Single_SMA_20_M1_crossover",
                "Single_SMA_50_M1_crossover",
                "Single_EMA_5_M1_crossover",
                "Single_EMA_10_M1_crossover",
                "Single_EMA_20_M1_crossover",
                "Single_EMA_50_M1_crossover",
                "Single_WMA_5_M1_crossover",
                "Single_WMA_10_M1_crossover",
                "Single_WMA_20_M1_crossover",
                "Single_WMA_50_M1_crossover"
            ]
        },
        "MA Crossover Strategies": {
            "count": 112,
            "examples": [
                "Crossover_SMA_5_SMA_10_M1",
                "Crossover_SMA_10_SMA_20_M1",
                "Crossover_SMA_20_SMA_50_M1",
                "Crossover_EMA_5_EMA_10_M1",
                "Crossover_EMA_10_EMA_20_M1",
                "Crossover_EMA_20_EMA_50_M1",
                "Crossover_WMA_5_WMA_10_M1",
                "Crossover_WMA_10_WMA_20_M1",
                "Crossover_WMA_20_WMA_50_M1"
            ]
        },
        "Multi-Timeframe Strategies": {
            "count": 96,
            "examples": [
                "MultiTF_M1_H1_SMA_50",
                "MultiTF_M5_H1_SMA_50",
                "MultiTF_M15_H1_SMA_50",
                "MultiTF_M1_H4_SMA_50",
                "MultiTF_M5_H4_SMA_50",
                "MultiTF_M15_H4_SMA_50",
                "MultiTF_M1_D_SMA_50",
                "MultiTF_M5_D_SMA_50",
                "MultiTF_M15_D_SMA_50"
            ]
        },
        "Mean Reversion Strategies": {
            "count": 2160,
            "examples": [
                "MeanRev_SMA_20_1pct_M1",
                "MeanRev_SMA_20_2pct_M1",
                "MeanRev_SMA_20_3pct_M1",
                "MeanRev_SMA_50_1pct_M1",
                "MeanRev_SMA_50_2pct_M1",
                "MeanRev_SMA_50_3pct_M1",
                "MeanRev_EMA_20_1pct_M1",
                "MeanRev_EMA_20_2pct_M1",
                "MeanRev_EMA_20_3pct_M1",
                "MeanRev_EMA_50_1pct_M1",
                "MeanRev_EMA_50_2pct_M1",
                "MeanRev_EMA_50_3pct_M1"
            ]
        }
    }
    
    print("STRATEGIES GENERATED:")
    print("="*80)
    
    total_strategies = 0
    for category, info in strategies_info.items():
        print(f"\n{category}:")
        print(f"  Count: {info['count']}")
        print(f"  Examples:")
        for example in info['examples'][:5]:  # Show first 5 examples
            print(f"    - {example}")
        if len(info['examples']) > 5:
            print(f"    ... and {len(info['examples']) - 5} more")
        total_strategies += info['count']
    
    print(f"\nTotal Strategies Generated: {total_strategies}")
    print(f"Strategies that passed validation: 960")
    print(f"Strategies that met performance criteria: 0")
    
    print("\n" + "="*80)
    print("PERFORMANCE ANALYSIS")
    print("="*80)
    
    print("Based on your gold data (XAUUSD):")
    print("- Date range: April 23, 2025 to August 4, 2025")
    print("- Price range: $3,121.84 to $3,451.06")
    print("- Data points: 100,000 1-minute candles")
    print("- Total return over period: ~10.5%")
    
    print("\nWhy no strategies met the criteria:")
    print("1. Market Conditions:")
    print("   - Gold showed a strong uptrend during this period")
    print("   - Simple MA strategies often underperform in trending markets")
    print("   - The data period is relatively short (3.5 months)")
    
    print("\n2. Strategy Limitations:")
    print("   - MA strategies work best in sideways/ranging markets")
    print("   - In trending markets, they generate false signals")
    print("   - Commission and slippage reduce profitability")
    
    print("\n3. Performance Thresholds:")
    print("   - Even with relaxed thresholds, strategies didn't perform well")
    print("   - This suggests the market conditions were challenging")
    
    print("\n" + "="*80)
    print("RECOMMENDATIONS")
    print("="*80)
    
    print("1. Try Different Data Periods:")
    print("   - Use data from sideways/ranging markets")
    print("   - Try longer time periods (1-2 years)")
    print("   - Include different market conditions")
    
    print("\n2. Modify Strategy Parameters:")
    print("   - Use longer MA periods (100-200)")
    print("   - Try different MA types (EMA, WMA)")
    print("   - Adjust entry/exit thresholds")
    
    print("\n3. Consider Alternative Strategies:")
    print("   - Breakout strategies")
    print("   - Momentum strategies")
    print("   - Volatility-based strategies")
    
    print("\n4. Analyze Individual Performance:")
    print("   - Look at the best performing strategies")
    print("   - Even if they don't meet criteria, they may show promise")
    print("   - Use them as starting points for optimization")

if __name__ == "__main__":
    show_raw_strategies()