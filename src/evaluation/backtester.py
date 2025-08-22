"""
Backtesting module for strategy evaluation
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from ..strategies.base import BaseStrategy, StrategyResult
import logging
from config.settings import INITIAL_CAPITAL, COMMISSION_RATE, SLIPPAGE

logger = logging.getLogger(__name__)

class Backtester:
    """Backtesting engine for strategy evaluation"""
    
    def __init__(self, commission_rate=0.001, slippage=0.0001):
        self.initial_capital = 100000  # Add initial capital
        self.commission_rate = commission_rate
        self.slippage = slippage
        self.save_results = True  # Always save results
    
    def backtest_strategy(self, strategy: BaseStrategy, data: pd.DataFrame) -> StrategyResult:
        """
        Backtest a single strategy
        
        Args:
            strategy: Strategy to backtest
            data: OHLCV DataFrame with features
            
        Returns:
            StrategyResult object
        """
        try:
            result = strategy.backtest(
                data=data,
                initial_capital=self.initial_capital,
                commission_rate=self.commission_rate,
                slippage=self.slippage
            )
            
            logger.info(f"Backtested {strategy.name}: Sharpe={result.metrics['sharpe_ratio']:.3f}, "
                       f"Return={result.metrics['total_return']:.3f}, "
                       f"WinRate={result.metrics['win_rate']:.3f}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error backtesting {strategy.name}: {e}")
            # Return empty result
            return StrategyResult(
                strategy_name=strategy.name,
                parameters=strategy.parameters,
                signals=pd.Series(0, index=data.index),
                returns=pd.Series(0, index=data.index),
                positions=pd.Series(0, index=data.index),
                equity_curve=pd.Series(self.initial_capital, index=data.index),
                trades=pd.DataFrame(),
                metrics={'total_return': 0, 'sharpe_ratio': 0, 'win_rate': 0}
            )
    
    def backtest_strategies(self, strategies: List[BaseStrategy], 
                           data: pd.DataFrame) -> List[StrategyResult]:
        """
        Backtest multiple strategies
        
        Args:
            strategies: List of strategies to backtest
            data: OHLCV DataFrame with features
            
        Returns:
            List of StrategyResult objects
        """
        results = []
        
        logger.info(f"Starting backtest of {len(strategies)} strategies...")
        
        for i, strategy in enumerate(strategies):
            logger.info(f"Backtesting strategy {i+1}/{len(strategies)}: {strategy.name}")
            
            result = self.backtest_strategy(strategy, data)
            results.append(result)
        
        logger.info(f"Completed backtest of {len(strategies)} strategies")
        
        return results
    
    def backtest_strategies_parallel(self, strategies: List[BaseStrategy], 
                                   data: pd.DataFrame, n_jobs: int = -1) -> List[StrategyResult]:
        """
        Backtest multiple strategies in parallel
        
        Args:
            strategies: List of strategies to backtest
            data: OHLCV DataFrame with features
            n_jobs: Number of parallel jobs (-1 for all cores)
            
        Returns:
            List of StrategyResult objects
        """
        from joblib import Parallel, delayed
        
        logger.info(f"Starting parallel backtest of {len(strategies)} strategies...")
        
        def backtest_single(strategy):
            return self.backtest_strategy(strategy, data)
        
        results = Parallel(n_jobs=n_jobs)(
            delayed(backtest_single)(strategy) for strategy in strategies
        )
        
        logger.info(f"Completed parallel backtest of {len(strategies)} strategies")
        
        return results
    
    def validate_strategy(self, strategy: BaseStrategy, data: pd.DataFrame) -> bool:
        """
        Validate if a strategy can be backtested with the given data
        
        Args:
            strategy: Strategy to validate
            data: OHLCV DataFrame with features
            
        Returns:
            True if strategy can be backtested, False otherwise
        """
        try:
            # Try to generate signals
            signals = strategy.generate_signals(data)
            
            # Check if signals were generated
            if signals is None or signals.empty:
                return False
            
            # Check if there are any non-zero signals
            if signals.sum() == 0:
                return False
            
            return True
            
        except Exception as e:
            logger.warning(f"Strategy validation failed for {strategy.name}: {e}")
            return False
    
    def filter_valid_strategies(self, strategies: List[BaseStrategy], 
                              data: pd.DataFrame) -> List[BaseStrategy]:
        """
        Filter strategies that can be backtested with the given data
        
        Args:
            strategies: List of strategies to filter
            data: OHLCV DataFrame with features
            
        Returns:
            List of valid strategies
        """
        valid_strategies = []
        
        logger.info(f"Validating {len(strategies)} strategies...")
        
        for strategy in strategies:
            if self.validate_strategy(strategy, data):
                valid_strategies.append(strategy)
        
        logger.info(f"Found {len(valid_strategies)} valid strategies out of {len(strategies)}")
        
        return valid_strategies
    
    def get_backtest_summary(self, results: List[StrategyResult]) -> pd.DataFrame:
        """
        Generate summary of backtest results
        
        Args:
            results: List of StrategyResult objects
            
        Returns:
            DataFrame with backtest summary
        """
        summary_data = []
        
        for result in results:
            summary_data.append({
                'strategy_name': result.strategy_name,
                'category': result.parameters.get('category', 'unknown'),
                'total_return': result.metrics['total_return'],
                'annual_return': result.metrics['annual_return'],
                'sharpe_ratio': result.metrics['sharpe_ratio'],
                'max_drawdown': result.metrics['max_drawdown'],
                'volatility': result.metrics['volatility'],
                'win_rate': result.metrics['win_rate'],
                'profit_factor': result.metrics['profit_factor'],
                'num_trades': result.metrics['num_trades'],
                'avg_trade_return': result.metrics['avg_trade_return'],
                'max_consecutive_losses': result.metrics['max_consecutive_losses']
            })
        
        return pd.DataFrame(summary_data)
    
    def compare_strategies(self, results: List[StrategyResult]) -> pd.DataFrame:
        """
        Compare strategies based on key metrics
        
        Args:
            results: List of StrategyResult objects
            
        Returns:
            DataFrame with strategy comparison
        """
        summary_df = self.get_backtest_summary(results)
        
        # Sort by Sharpe ratio
        summary_df = summary_df.sort_values('sharpe_ratio', ascending=False)
        
        # Add rankings
        summary_df['sharpe_rank'] = summary_df['sharpe_ratio'].rank(ascending=False)
        summary_df['return_rank'] = summary_df['total_return'].rank(ascending=False)
        summary_df['winrate_rank'] = summary_df['win_rate'].rank(ascending=False)
        
        # Calculate composite score
        summary_df['composite_score'] = (
            summary_df['sharpe_ratio'].fillna(0) * 0.4 +
            summary_df['total_return'].fillna(0) * 0.3 +
            summary_df['win_rate'].fillna(0) * 0.2 +
            (1 - abs(summary_df['max_drawdown'].fillna(0))) * 0.1
        )
        
        summary_df['composite_rank'] = summary_df['composite_score'].rank(ascending=False)
        
        # Add composite score to summary
        summary_df['composite_score'] = summary_df.apply(self._calculate_composite_score, axis=1)
        
        # Store all results
        self.all_results = results
        
        # Save backtest results if requested
        if hasattr(self, 'save_results') and self.save_results:
            import pickle
            from pathlib import Path
            
            results_dir = Path("results")
            results_dir.mkdir(exist_ok=True)
            
            # Save all results
            with open(results_dir / "all_backtest_results.pkl", 'wb') as f:
                pickle.dump(results, f)
            
            # Save summary
            with open(results_dir / "backtest_summary.pkl", 'wb') as f:
                pickle.dump(summary_df, f)
            
            print(f"✅ Saved {len(results)} backtest results to results/all_backtest_results.pkl")
        
        return summary_df
    
    def get_strategy_details(self, result: StrategyResult) -> Dict:
        """
        Get detailed information about a strategy result
        
        Args:
            result: StrategyResult object
            
        Returns:
            Dictionary with detailed strategy information
        """
        details = {
            'strategy_name': result.strategy_name,
            'parameters': result.parameters,
            'metrics': result.metrics,
            'num_signals': len(result.signals[result.signals != 0]),
            'signal_frequency': len(result.signals[result.signals != 0]) / len(result.signals),
            'avg_position_duration': self._calculate_avg_position_duration(result.positions),
            'max_position_duration': self._calculate_max_position_duration(result.positions),
            'equity_curve_stats': {
                'final_value': result.equity_curve.iloc[-1],
                'peak_value': result.equity_curve.max(),
                'trough_value': result.equity_curve.min(),
                'volatility': result.equity_curve.pct_change().std()
            }
        }
        
        return details
    
    def _calculate_avg_position_duration(self, positions: pd.Series) -> float:
        """Calculate average position duration"""
        position_changes = positions.diff().abs()
        position_periods = []
        current_period = 0
        
        for change in position_changes:
            if change > 0:  # Position changed
                if current_period > 0:
                    position_periods.append(current_period)
                current_period = 1
            elif positions.iloc[current_period] != 0:  # In position
                current_period += 1
        
        if position_periods:
            return np.mean(position_periods)
        else:
            return 0
    
    def _calculate_max_position_duration(self, positions: pd.Series) -> int:
        """Calculate maximum position duration"""
        position_changes = positions.diff().abs()
        max_period = 0
        current_period = 0
        
        for change in position_changes:
            if change > 0:  # Position changed
                max_period = max(max_period, current_period)
                current_period = 1
            elif positions.iloc[current_period] != 0:  # In position
                current_period += 1
        
        return max_period

    def get_all_results(self) -> List[StrategyResult]:
        """Get all backtest results"""
        return self.all_results if hasattr(self, 'all_results') else []