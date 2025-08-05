"""
MA Crossover Strategy Implementation
MA Crossover Strategies (Fast MA crosses above/below Slow MA)
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from .base import BaseStrategy
import logging

logger = logging.getLogger(__name__)

class MACrossoverStrategy(BaseStrategy):
    """Moving Average Crossover Strategy"""
    
    def __init__(self, fast_ma_type: str, fast_ma_period: int, 
                 slow_ma_type: str, slow_ma_period: int, timeframe: str):
        """
        Initialize MA Crossover Strategy
        
        Args:
            fast_ma_type: Type of fast MA (SMA, EMA, WMA)
            fast_ma_period: Fast MA period
            slow_ma_type: Type of slow MA (SMA, EMA, WMA)
            slow_ma_period: Slow MA period
            timeframe: Timeframe for the strategy
        """
        name = f"Crossover_{fast_ma_type}{fast_ma_period}_{slow_ma_type}{slow_ma_period}_{timeframe}"
        super().__init__(name, 'ma_crossover')
        
        self.fast_ma_type = fast_ma_type
        self.fast_ma_period = fast_ma_period
        self.slow_ma_type = slow_ma_type
        self.slow_ma_period = slow_ma_period
        self.timeframe = timeframe
        
        self.parameters = {
            'fast_ma_type': fast_ma_type,
            'fast_ma_period': fast_ma_period,
            'slow_ma_type': slow_ma_type,
            'slow_ma_period': slow_ma_period,
            'timeframe': timeframe
        }
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """
        Generate trading signals based on MA crossover
        
        Args:
            data: OHLCV DataFrame with MA features
            
        Returns:
            Series with signals (1 for buy, -1 for sell, 0 for hold)
        """
        # Get MA column names
        fast_ma_col = f"{self.fast_ma_type.lower()}_{self.fast_ma_period}"
        slow_ma_col = f"{self.slow_ma_type.lower()}_{self.slow_ma_period}"
        
        if fast_ma_col not in data.columns or slow_ma_col not in data.columns:
            logger.error(f"MA columns not found: {fast_ma_col}, {slow_ma_col}")
            return pd.Series(0, index=data.index)
        
        # Get crossover feature names
        crossover_up = f"crossover_{self.fast_ma_type.lower()}_{self.fast_ma_period}_above_{self.slow_ma_type.lower()}_{self.slow_ma_period}"
        crossover_down = f"crossover_{self.fast_ma_type.lower()}_{self.fast_ma_period}_below_{self.slow_ma_type.lower()}_{self.slow_ma_period}"
        
        signals = pd.Series(0, index=data.index)
        
        # Check if crossover features exist
        if crossover_up in data.columns and crossover_down in data.columns:
            # Use pre-computed crossover features
            signals[data[crossover_up]] = 1
            signals[data[crossover_down]] = -1
        else:
            # Calculate crossovers manually
            fast_ma = data[fast_ma_col]
            slow_ma = data[slow_ma_col]
            
            # Buy signal: fast MA crosses above slow MA
            buy_signal = (fast_ma > slow_ma) & (fast_ma.shift(1) <= slow_ma.shift(1))
            
            # Sell signal: fast MA crosses below slow MA
            sell_signal = (fast_ma < slow_ma) & (fast_ma.shift(1) >= slow_ma.shift(1))
            
            signals[buy_signal] = 1
            signals[sell_signal] = -1
        
        return signals
    
    def get_strategy_description(self) -> str:
        """Get human-readable strategy description"""
        return f"Buy: {self.fast_ma_type}{self.fast_ma_period} crosses above {self.slow_ma_type}{self.slow_ma_period} on {self.timeframe}, Sell: {self.fast_ma_type}{self.fast_ma_period} crosses below {self.slow_ma_type}{self.slow_ma_period} on {self.timeframe}"

class MultiMACrossoverStrategy(BaseStrategy):
    """Multi-MA Crossover Strategy (3-MA and 4-MA combinations)"""
    
    def __init__(self, ma_configs: List[Dict], timeframe: str, strategy_type: str = 'triple'):
        """
        Initialize Multi-MA Crossover Strategy
        
        Args:
            ma_configs: List of MA configurations [{'type': 'SMA', 'period': 10}, ...]
            timeframe: Timeframe for the strategy
            strategy_type: Type of strategy ('triple', 'quadruple')
        """
        ma_names = [f"{config['type']}{config['period']}" for config in ma_configs]
        name = f"Multi_{strategy_type}_{'_'.join(ma_names)}_{timeframe}"
        super().__init__(name, 'ma_crossover')
        
        self.ma_configs = ma_configs
        self.timeframe = timeframe
        self.strategy_type = strategy_type
        
        self.parameters = {
            'ma_configs': ma_configs,
            'timeframe': timeframe,
            'strategy_type': strategy_type
        }
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """
        Generate trading signals based on multi-MA alignment
        
        Args:
            data: OHLCV DataFrame with MA features
            
        Returns:
            Series with signals (1 for buy, -1 for sell, 0 for hold)
        """
        signals = pd.Series(0, index=data.index)
        
        # Get MA values
        ma_values = []
        for config in self.ma_configs:
            ma_col = f"{config['type'].lower()}_{config['period']}"
            if ma_col in data.columns:
                ma_values.append(data[ma_col])
            else:
                logger.error(f"MA column {ma_col} not found")
                return signals
        
        if len(ma_values) < 2:
            logger.error("Need at least 2 MAs for crossover strategy")
            return signals
        
        # Sort MAs by period (fastest to slowest)
        periods = [config['period'] for config in self.ma_configs]
        sorted_indices = np.argsort(periods)
        ma_values = [ma_values[i] for i in sorted_indices]
        
        if self.strategy_type == 'triple' and len(ma_values) >= 3:
            # Triple MA strategy: fastest > middle > slowest
            fast_ma, middle_ma, slow_ma = ma_values[0], ma_values[1], ma_values[2]
            
            # Buy: fast > middle > slow (all aligned upward)
            buy_condition = (fast_ma > middle_ma) & (middle_ma > slow_ma)
            buy_signal = buy_condition & ~buy_condition.shift(1)
            
            # Sell: fast < middle < slow (all aligned downward)
            sell_condition = (fast_ma < middle_ma) & (middle_ma < slow_ma)
            sell_signal = sell_condition & ~sell_condition.shift(1)
            
            signals[buy_signal] = 1
            signals[sell_signal] = -1
            
        elif self.strategy_type == 'quadruple' and len(ma_values) >= 4:
            # Quadruple MA strategy: all MAs aligned
            ma1, ma2, ma3, ma4 = ma_values[:4]
            
            # Buy: all MAs in ascending order
            buy_condition = (ma1 > ma2) & (ma2 > ma3) & (ma3 > ma4)
            buy_signal = buy_condition & ~buy_condition.shift(1)
            
            # Sell: all MAs in descending order
            sell_condition = (ma1 < ma2) & (ma2 < ma3) & (ma3 < ma4)
            sell_signal = sell_condition & ~sell_condition.shift(1)
            
            signals[buy_signal] = 1
            signals[sell_signal] = -1
            
        else:
            # Fallback to simple crossover
            fast_ma, slow_ma = ma_values[0], ma_values[-1]
            
            buy_signal = (fast_ma > slow_ma) & (fast_ma.shift(1) <= slow_ma.shift(1))
            sell_signal = (fast_ma < slow_ma) & (fast_ma.shift(1) >= slow_ma.shift(1))
            
            signals[buy_signal] = 1
            signals[sell_signal] = -1
        
        return signals
    
    def get_strategy_description(self) -> str:
        """Get human-readable strategy description"""
        ma_names = [f"{config['type']}{config['period']}" for config in self.ma_configs]
        ma_str = " > ".join(ma_names)
        
        if self.strategy_type == 'triple':
            return f"Buy when {ma_str} on {self.timeframe}, Sell when reversed"
        else:
            return f"Buy when {ma_str} aligned on {self.timeframe}, Sell when reversed"

class MACrossoverStrategyGenerator:
    """Generator for MA Crossover Strategies"""
    
    def __init__(self, ma_types: List[str] = None, ma_periods: List[int] = None, 
                 timeframes: List[str] = None):
        """
        Initialize strategy generator
        
        Args:
            ma_types: List of MA types to test
            ma_periods: List of MA periods to test
            timeframes: List of timeframes to test
        """
        from config.settings import MA_TYPES, MA_PERIODS, TIMEFRAMES
        
        self.ma_types = ma_types or MA_TYPES
        self.ma_periods = ma_periods or MA_PERIODS
        self.timeframes = timeframes or list(TIMEFRAMES.keys())
    
    def generate_strategies(self) -> List[MACrossoverStrategy]:
        """
        Generate all possible MA crossover strategies
        
        Returns:
            List of MACrossoverStrategy objects
        """
        strategies = []
        
        for fast_ma_type in self.ma_types:
            for fast_period in self.ma_periods:
                for slow_ma_type in self.ma_types:
                    for slow_period in self.ma_periods:
                        # Only create strategies where fast MA period < slow MA period
                        if fast_period < slow_period:
                            for timeframe in self.timeframes:
                                strategy = MACrossoverStrategy(
                                    fast_ma_type=fast_ma_type,
                                    fast_ma_period=fast_period,
                                    slow_ma_type=slow_ma_type,
                                    slow_ma_period=slow_period,
                                    timeframe=timeframe
                                )
                                strategies.append(strategy)
        
        logger.info(f"Generated {len(strategies)} MA crossover strategies")
        return strategies
    
    def generate_filtered_strategies(self, max_periods: int = 100) -> List[MACrossoverStrategy]:
        """
        Generate filtered MA crossover strategies with reasonable parameters
        
        Args:
            max_periods: Maximum MA period to test
            
        Returns:
            List of filtered MACrossoverStrategy objects
        """
        strategies = []
        
        # Common MA combinations
        common_combinations = [
            # (fast_type, fast_period, slow_type, slow_period)
            ('EMA', 5, 'SMA', 20),
            ('EMA', 10, 'SMA', 30),
            ('EMA', 12, 'EMA', 26),
            ('SMA', 10, 'SMA', 50),
            ('EMA', 20, 'SMA', 50),
            ('WMA', 10, 'SMA', 50),
            ('EMA', 50, 'SMA', 200),
            ('SMA', 20, 'SMA', 100),
        ]
        
        for fast_type, fast_period, slow_type, slow_period in common_combinations:
            if fast_period <= max_periods and slow_period <= max_periods:
                for timeframe in self.timeframes:
                    strategy = MACrossoverStrategy(
                        fast_ma_type=fast_type,
                        fast_ma_period=fast_period,
                        slow_ma_type=slow_type,
                        slow_ma_period=slow_period,
                        timeframe=timeframe
                    )
                    strategies.append(strategy)
        
        logger.info(f"Generated {len(strategies)} filtered MA crossover strategies")
        return strategies
    
    def generate_multi_ma_strategies(self, max_periods: int = 100) -> List[MultiMACrossoverStrategy]:
        """
        Generate multi-MA crossover strategies
        
        Args:
            max_periods: Maximum MA period to test
            
        Returns:
            List of MultiMACrossoverStrategy objects
        """
        strategies = []
        
        # Triple MA combinations
        triple_combinations = [
            [
                {'type': 'EMA', 'period': 5},
                {'type': 'SMA', 'period': 20},
                {'type': 'SMA', 'period': 50}
            ],
            [
                {'type': 'EMA', 'period': 10},
                {'type': 'EMA', 'period': 30},
                {'type': 'SMA', 'period': 100}
            ],
            [
                {'type': 'WMA', 'period': 12},
                {'type': 'EMA', 'period': 26},
                {'type': 'SMA', 'period': 200}
            ]
        ]
        
        for ma_configs in triple_combinations:
            if all(config['period'] <= max_periods for config in ma_configs):
                for timeframe in self.timeframes:
                    strategy = MultiMACrossoverStrategy(
                        ma_configs=ma_configs,
                        timeframe=timeframe,
                        strategy_type='triple'
                    )
                    strategies.append(strategy)
        
        logger.info(f"Generated {len(strategies)} multi-MA strategies")
        return strategies