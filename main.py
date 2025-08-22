"""
Main execution script for Trading Strategy Discovery System
"""

import logging
import sys
from pathlib import Path
from typing import Dict, List
import pandas as pd
import numpy as np

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.data.loader import DataLoader
from src.data.timeframe_generator import TimeframeGenerator
from src.data.feature_engineer import FeatureEngineer
from src.strategies.ma_single import SingleMAStrategyGenerator
from src.strategies.ma_crossover import MACrossoverStrategyGenerator
from src.strategies.multi_tf import MultiTimeframeStrategyGenerator
from src.strategies.mean_reversion import MeanReversionStrategyGenerator
from src.evaluation.backtester import Backtester
from src.evaluation.ranking import StrategyRanker
from src.visualization.reports import ReportGenerator
from config.settings import RESULTS_DIR, DATA_RAW_DIR

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading_strategy_discovery.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class TradingStrategyDiscoverySystem:
    """Main system for discovering trading strategies"""
    
    def __init__(self):
        """Initialize the trading strategy discovery system"""
        self.data_loader = DataLoader()
        self.timeframe_generator = TimeframeGenerator()
        self.feature_engineer = FeatureEngineer()
        self.backtester = Backtester()
        self.ranker = StrategyRanker()
        self.report_generator = ReportGenerator()
        
        # Strategy generators
        self.single_ma_generator = SingleMAStrategyGenerator()
        self.ma_crossover_generator = MACrossoverStrategyGenerator()
        self.multi_tf_generator = MultiTimeframeStrategyGenerator()
        self.mean_reversion_generator = MeanReversionStrategyGenerator()
        
        # Results storage
        self.timeframe_data = {}
        self.enhanced_data = {}
        self.strategy_results = {}
        
    def run(self):
        """Run the complete trading strategy discovery system"""
        try:
            logger.info("Starting Trading Strategy Discovery System")
            
            # Step 1: Load and validate data
            logger.info("Step 1: Loading and validating data...")
            m1_data = self._load_data()
            
            # Step 2: Generate timeframes
            logger.info("Step 2: Generating timeframes...")
            self.timeframe_data = self._generate_timeframes(m1_data)
            
            # Step 3: Feature engineering
            logger.info("Step 3: Feature engineering...")
            self.enhanced_data = self._engineer_features()
            
            # Step 4: Generate strategies
            logger.info("Step 4: Generating strategies...")
            all_strategies = self._generate_strategies()
            
            # Step 5: Backtest strategies
            logger.info("Step 5: Backtesting strategies...")
            self.strategy_results = self._backtest_strategies(all_strategies)
            
            # Step 6: Ranking and selecting top strategies
            logger.info("Step 6: Ranking and selecting top strategies...")
            print("Step 6: Ranking and selecting top strategies...")
            
            # Get all backtest results
            all_results = self.backtester.get_all_results()
            
            # Sort by total return
            all_results.sort(key=lambda x: x.metrics.get('total_return', 0), reverse=True)
            
            # Show ALL results (no filtering)
            print("\n" + "="*80)
            print("ALL STRATEGIES BY TOTAL RETURN (NO FILTERING)")
            print("="*80)
            
            for i, result in enumerate(all_results):
                metrics = result.metrics
                print(f"\n{i+1:3d}. {result.strategy_name}")
                print(f"    Description: {result.get_strategy_description()}")
                print(f"    Total Return: {metrics.get('total_return', 0):.4f}")
                print(f"    Annual Return: {metrics.get('annual_return', 0):.4f}")
                print(f"    Sharpe Ratio: {metrics.get('sharpe_ratio', 0):.4f}")
                print(f"    Win Rate: {metrics.get('win_rate', 0):.4f}")
                print(f"    Max Drawdown: {metrics.get('max_drawdown', 0):.4f}")
                print(f"    Profit Factor: {metrics.get('profit_factor', 0):.4f}")
                print(f"    Number of Trades: {metrics.get('num_trades', 0)}")
                print(f"    Volatility: {metrics.get('volatility', 0):.4f}")
                
                # Stop after showing first 50 for readability
                if i >= 49:
                    print(f"\n... and {len(all_results) - 50} more strategies")
                    break
            
            # Save ALL results to CSV
            all_data = []
            for i, result in enumerate(all_results):
                metrics = result.metrics
                all_data.append({
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
            
            df = pd.DataFrame(all_data)
            output_file = "results/all_strategies_no_filtering.csv"
            df.to_csv(output_file, index=False)
            print(f"\n✅ ALL {len(all_results)} strategies saved to: {output_file}")
            
            # Show summary statistics
            print(f"\n" + "="*80)
            print("SUMMARY STATISTICS")
            print("="*80)
            print(f"Total strategies tested: {len(all_results)}")
            if all_results:
                print(f"Best total return: {all_results[0].metrics.get('total_return', 0):.4f}")
                print(f"Worst total return: {all_results[-1].metrics.get('total_return', 0):.4f}")
                print(f"Average total return: {np.mean([r.metrics.get('total_return', 0) for r in all_results]):.4f}")
                print(f"Average win rate: {np.mean([r.metrics.get('win_rate', 0) for r in all_results]):.4f}")
                print(f"Average Sharpe ratio: {np.mean([r.metrics.get('sharpe_ratio', 0) for r in all_results]):.4f}")
            
            # Continue with ranking
            ranking_report = self._rank_strategies()
            
            # Step 7: Generate reports and visualizations
            logger.info("Step 7: Generating reports and visualizations...")
            self._generate_reports(ranking_report)
            
            logger.info("Trading Strategy Discovery System completed successfully!")
            
        except Exception as e:
            logger.error(f"Error in trading strategy discovery system: {e}")
            raise
    
    def _load_data(self) -> pd.DataFrame:
        """Load and validate 1-minute OHLCV data"""
        logger.info("Loading 1-minute OHLCV data...")
        
        # Check if data files exist
        if not DATA_RAW_DIR.exists() or not list(DATA_RAW_DIR.glob("*.csv")):
            logger.error(f"No CSV files found in {DATA_RAW_DIR}")
            logger.info("Please place your 1-minute OHLCV CSV files in the data/raw/ directory")
            raise FileNotFoundError(f"No CSV files found in {DATA_RAW_DIR}")
        
        # Load data
        m1_data = self.data_loader.get_combined_data()
        
        logger.info(f"Loaded data with shape: {m1_data.shape}")
        logger.info(f"Date range: {m1_data.index.min()} to {m1_data.index.max()}")
        
        return m1_data
    
    def _generate_timeframes(self, m1_data: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """Generate all timeframes from M1 data"""
        logger.info("Generating timeframes from M1 data...")
        
        timeframe_data = self.timeframe_generator.generate_all_timeframes(m1_data)
        
        # Validate generated timeframes
        if not self.timeframe_generator.validate_timeframe_data(timeframe_data):
            raise ValueError("Timeframe validation failed")
        
        # Get timeframe statistics
        tf_stats = self.timeframe_generator.get_timeframe_statistics(timeframe_data)
        logger.info("Timeframe statistics:")
        logger.info(tf_stats.to_string())
        
        return timeframe_data
    
    def _engineer_features(self) -> Dict[str, pd.DataFrame]:
        """Engineer features for all timeframes"""
        logger.info("Engineering features...")
        
        # Compute moving averages
        enhanced_data = self.feature_engineer.compute_all_moving_averages(self.timeframe_data)
        
        # Generate crossover features
        for tf_name, df in enhanced_data.items():
            enhanced_data[tf_name] = self.feature_engineer.generate_crossover_features(df)
        
        # Generate mean reversion features
        for tf_name, df in enhanced_data.items():
            enhanced_data[tf_name] = self.feature_engineer.generate_mean_reversion_features(df)
        
        # Generate multi-timeframe features
        enhanced_data = self.feature_engineer.generate_multi_timeframe_features(enhanced_data)
        
        # Get feature summary
        feature_summary = self.feature_engineer.get_feature_summary(enhanced_data)
        logger.info("Feature summary:")
        logger.info(feature_summary.to_string())
        
        return enhanced_data
    
    def _generate_strategies(self) -> List:
        """Generate strategies for all categories"""
        logger.info("Generating strategies...")
        
        all_strategies = []
        
        # Generate Single MA strategies
        logger.info("Generating Single MA strategies...")
        single_ma_strategies = self.single_ma_generator.generate_filtered_strategies(max_periods=50)
        all_strategies.extend(single_ma_strategies)
        
        # Generate MA Crossover strategies
        logger.info("Generating MA Crossover strategies...")
        ma_crossover_strategies = self.ma_crossover_generator.generate_filtered_strategies(max_periods=100)
        all_strategies.extend(ma_crossover_strategies)
        
        # Generate Multi-Timeframe strategies
        logger.info("Generating Multi-Timeframe strategies...")
        multi_tf_strategies = self.multi_tf_generator.generate_filtered_strategies(max_periods=100)
        all_strategies.extend(multi_tf_strategies)
        
        # Generate Mean Reversion strategies
        logger.info("Generating Mean Reversion strategies...")
        mean_reversion_strategies = self.mean_reversion_generator.generate_filtered_strategies(max_periods=100)
        all_strategies.extend(mean_reversion_strategies)
        
        logger.info(f"Generated {len(all_strategies)} total strategies")
        
        return all_strategies
    
    def _backtest_strategies(self, strategies: List) -> List:
        """Backtest all strategies"""
        logger.info("Backtesting strategies...")
        
        # Use M1 data for backtesting (most granular)
        m1_data = self.enhanced_data['M1']
        
        # Filter valid strategies
        valid_strategies = self.backtester.filter_valid_strategies(strategies, m1_data)
        logger.info(f"Found {len(valid_strategies)} valid strategies out of {len(strategies)}")
        
        # Backtest strategies
        results = self.backtester.backtest_strategies_parallel(valid_strategies, m1_data)
        
        return results
    
    def _rank_strategies(self) -> Dict:
        """Rank and select top strategies"""
        logger.info("Ranking strategies...")
        
        # Generate ranking report
        ranking_report = self.ranker.generate_ranking_report(self.strategy_results)
        
        # Export results
        self.ranker.export_ranking_results(ranking_report, RESULTS_DIR)
        
        return ranking_report
    
    def _generate_reports(self, ranking_report: Dict):
        """Generate reports and visualizations"""
        logger.info("Generating reports and visualizations...")
        
        # Generate comprehensive reports
        self.report_generator.generate_comprehensive_report(ranking_report, RESULTS_DIR)
        
        # Generate strategy recommendations
        recommendations = self.ranker.get_strategy_recommendations(ranking_report)
        
        # Print summary
        self._print_summary(ranking_report, recommendations)
    
    def _print_summary(self, ranking_report: Dict, recommendations: Dict):
        """Print summary of results"""
        print("\n" + "="*80)
        print("TRADING STRATEGY DISCOVERY SYSTEM - RESULTS SUMMARY")
        print("="*80)
        
        overview = ranking_report['overview']
        print(f"\nOverview:")
        print(f"  Total strategies tested: {overview['total_strategies']}")
        print(f"  Strategies meeting criteria: {overview['filtered_strategies']}")
        print(f"  Top strategies selected: {overview['top_strategies_selected']}")
        print(f"  Categories analyzed: {overview['categories_analyzed']}")
        
        print(f"\nTOP 20 BEST STRATEGIES (5 per category):")
        print("="*80)
        
        all_top_strategies = []
        for category, strategies in ranking_report['top_strategies'].items():
            print(f"\n{category.upper()} CATEGORY:")
            print("-" * 50)
            
            for i, strategy in enumerate(strategies[:5]):  # Top 5 per category
                metrics = strategy.metrics
                rank = i + 1
                
                print(f"{rank:2d}. {strategy.strategy_name}")
                print(f"    Description: {strategy.get_strategy_description()}")
                print(f"    Sharpe Ratio: {metrics['sharpe_ratio']:.3f}")
                print(f"    Total Return: {metrics['total_return']:.3f}")
                print(f"    Annual Return: {metrics['annual_return']:.3f}")
                print(f"    Win Rate: {metrics['win_rate']:.3f}")
                print(f"    Max Drawdown: {metrics['max_drawdown']:.3f}")
                print(f"    Profit Factor: {metrics['profit_factor']:.3f}")
                print(f"    Number of Trades: {metrics['num_trades']}")
                print()
                
                # Add to overall list for Excel export
                all_top_strategies.append({
                    'rank': len(all_top_strategies) + 1,
                    'category': category,
                    'strategy_name': strategy.strategy_name,
                    'description': strategy.get_strategy_description(),
                    'sharpe_ratio': metrics['sharpe_ratio'],
                    'total_return': metrics['total_return'],
                    'annual_return': metrics['annual_return'],
                    'win_rate': metrics['win_rate'],
                    'max_drawdown': metrics['max_drawdown'],
                    'profit_factor': metrics['profit_factor'],
                    'num_trades': metrics['num_trades'],
                    'volatility': metrics['volatility'],
                    'avg_trade_return': metrics['avg_trade_return'],
                    'max_consecutive_losses': metrics['max_consecutive_losses']
                })
        
        # Save top 20 strategies to Excel
        if all_top_strategies:
            top_20_df = pd.DataFrame(all_top_strategies)
            excel_file = RESULTS_DIR / 'top_20_strategies.xlsx'
            top_20_df.to_excel(excel_file, index=False, sheet_name='Top_20_Strategies')
            print(f"\n✅ TOP 20 STRATEGIES SAVED TO EXCEL: {excel_file}")
        
        print(f"\n📊 ALL RESULTS SAVED TO EXCEL:")
        print(f"  - {RESULTS_DIR}/trading_strategy_results.xlsx (Complete results)")
        print(f"  - {RESULTS_DIR}/top_20_strategies.xlsx (Top 20 strategies)")
        print(f"  - {RESULTS_DIR}/ (Charts and reports)")
        print("="*80)

def main():
    """Main function"""
    try:
        # Create system instance
        system = TradingStrategyDiscoverySystem()
        
        # Run the system
        system.run()
        
    except Exception as e:
        logger.error(f"Error in main execution: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()