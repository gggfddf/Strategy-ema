#!/usr/bin/env python3
"""
Show top 50 strategies from the 960 tested
"""

import pandas as pd
import numpy as np
import sys
from pathlib import Path

def show_top_50_strategies():
    """Show top 50 strategies by performance"""
    print("="*80)
    print("TOP 50 TRADING STRATEGIES FROM 960 TESTED")
    print("="*80)
    
    try:
        # Import the backtester to get raw results
        sys.path.append('src')
        from evaluation.backtester import Backtester
        from strategies.ma_single import SingleMAStrategyGenerator
        from strategies.ma_crossover import MACrossoverStrategyGenerator
        from strategies.multi_tf import MultiTimeframeStrategyGenerator
        from strategies.mean_reversion import MeanReversionStrategyGenerator
        from data.loader import DataLoader
        from data.timeframe_generator import TimeframeGenerator
        from data.feature_engineer import FeatureEngineer
        
        print("Loading data and generating strategies...")
        
        # Load data
        loader = DataLoader()
        data = loader.get_combined_data()
        
        # Generate timeframes
        tf_generator = TimeframeGenerator()
        timeframe_data = tf_generator.generate_all_timeframes(data)
        
        # Engineer features
        feature_engineer = FeatureEngineer()
        enhanced_data = feature_engineer.compute_all_moving_averages(timeframe_data)
        
        # Generate strategies
        generators = [
            SingleMAStrategyGenerator(),
            MACrossoverStrategyGenerator(),
            MultiTimeframeStrategyGenerator(),
            MeanReversionStrategyGenerator()
        ]
        
        all_strategies = []
        for generator in generators:
            strategies = generator.generate_strategies(enhanced_data)
            all_strategies.extend(strategies)
        
        print(f"Generated {len(all_strategies)} total strategies")
        
        # Backtest all strategies
        backtester = Backtester()
        results = []
        
        print("Backtesting strategies...")
        for i, strategy in enumerate(all_strategies):
            try:
                # Get data for this strategy's timeframe
                tf_name = strategy.parameters.get('timeframe', 'M1')
                if tf_name in enhanced_data:
                    data = enhanced_data[tf_name]
                    result = backtester.backtest_single_strategy(strategy, data)
                    results.append(result)
                    
                    if (i + 1) % 100 == 0:
                        print(f"Processed {i + 1} strategies...")
                        
            except Exception as e:
                print(f"Error with strategy {strategy.strategy_name}: {e}")
                continue
        
        print(f"Successfully backtested {len(results)} strategies")
        
        # Sort by total return (or another metric)
        results.sort(key=lambda x: x.metrics.get('total_return', 0), reverse=True)
        
        # Show top 50
        print(f"\n" + "="*80)
        print("TOP 50 STRATEGIES BY TOTAL RETURN")
        print("="*80)
        
        for i, result in enumerate(results[:50]):
            metrics = result.metrics
            print(f"\n{i+1:2d}. {result.strategy_name}")
            print(f"    Description: {result.get_strategy_description()}")
            print(f"    Total Return: {metrics.get('total_return', 0):.4f}")
            print(f"    Annual Return: {metrics.get('annual_return', 0):.4f}")
            print(f"    Sharpe Ratio: {metrics.get('sharpe_ratio', 0):.4f}")
            print(f"    Win Rate: {metrics.get('win_rate', 0):.4f}")
            print(f"    Max Drawdown: {metrics.get('max_drawdown', 0):.4f}")
            print(f"    Profit Factor: {metrics.get('profit_factor', 0):.4f}")
            print(f"    Number of Trades: {metrics.get('num_trades', 0)}")
            print(f"    Volatility: {metrics.get('volatility', 0):.4f}")
        
        # Save to CSV
        top_50_data = []
        for i, result in enumerate(results[:50]):
            metrics = result.metrics
            top_50_data.append({
                'rank': i + 1,
                'strategy_name': result.strategy_name,
                'description': result.get_strategy_description(),
                'category': result.parameters.get('category', 'Unknown'),
                'timeframe': result.parameters.get('timeframe', 'Unknown'),
                'total_return': metrics.get('total_return', 0),
                'annual_return': metrics.get('annual_return', 0),
                'sharpe_ratio': metrics.get('sharpe_ratio', 0),
                'win_rate': metrics.get('win_rate', 0),
                'max_drawdown': metrics.get('max_drawdown', 0),
                'profit_factor': metrics.get('profit_factor', 0),
                'num_trades': metrics.get('num_trades', 0),
                'volatility': metrics.get('volatility', 0)
            })
        
        df = pd.DataFrame(top_50_data)
        output_file = "results/top_50_strategies.csv"
        df.to_csv(output_file, index=False)
        print(f"\n✅ Top 50 strategies saved to: {output_file}")
        
        # Show summary statistics
        print(f"\n" + "="*80)
        print("SUMMARY STATISTICS")
        print("="*80)
        print(f"Total strategies tested: {len(results)}")
        print(f"Best total return: {results[0].metrics.get('total_return', 0):.4f}")
        print(f"Worst total return: {results[-1].metrics.get('total_return', 0):.4f}")
        print(f"Average total return: {np.mean([r.metrics.get('total_return', 0) for r in results]):.4f}")
        print(f"Average win rate: {np.mean([r.metrics.get('win_rate', 0) for r in results]):.4f}")
        print(f"Average Sharpe ratio: {np.mean([r.metrics.get('sharpe_ratio', 0) for r in results]):.4f}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    show_top_50_strategies()