"""
Single MA Strategy Implementation
Normal MA-Based Strategies (Single MA Logic)
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from .base import BaseStrategy
import logging

logger = logging.getLogger(__name__)

class SingleMAStrategy(BaseStrategy):
    """Single Moving Average Strategy"""
    
    def __init__(self, ma_type: str, ma_period: int, timeframe: str, 
                 signal_type: str = 'crossover'):
        """
        Initialize Single MA Strategy
        
        Args:
            ma_type: Type of MA (SMA, EMA, WMA)
            ma_period: MA period
            timeframe: Timeframe for the strategy
            signal_type: Signal type ('crossover' or 'position')
        """
        name = f"Single_{ma_type}_{ma_period}_{timeframe}_{signal_type}"
        super().__init__(name, 'normal_ma')
        
        self.ma_type = ma_type
        self.ma_period = ma_period
        self.timeframe = timeframe
        self.signal_type = signal_type
        
        self.parameters = {
            'ma_type': ma_type,
            'ma_period': ma_period,
            'timeframe': timeframe,
            'signal_type': signal_type
        }
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """
        Generate trading signals based on price vs MA relationship
        
        Args:
            data: DataFrame with OHLCV and MA data
            
        Returns:
            Series with signals (1 for buy, -1 for sell, 0 for hold)
        """
        signals = pd.Series(0, index=data.index)
        
        # Get MA column
        ma_col = f"{self.ma_type.lower()}_{self.ma_period}"
        
        if ma_col not in data.columns:
            logger.warning(f"MA column {ma_col} not found in data")
            return signals
        
        # Get price and MA data
        close_col = 'close' if 'close' in data.columns else data.columns[0]
        price = data[close_col]
        ma = data[ma_col]
        
        # Handle NaN values
        price = price.ffill().bfill()
        ma = ma.ffill().bfill()
        
        if self.signal_type == 'crossover':
            # Generate crossover signals
            price_above_ma = price > ma
            crossover_up = price_above_ma & ~price_above_ma.shift(1)
            crossover_down = ~price_above_ma & price_above_ma.shift(1)
            
            signals[crossover_up] = 1
            signals[crossover_down] = -1
            
        elif self.signal_type == 'position':
            # Generate position-based signals
            signals[price > ma] = 1
            signals[price < ma] = -1
        
        return signals
    
    def get_strategy_description(self) -> str:
        """Get human-readable strategy description"""
        if self.signal_type == 'crossover':
            return f"Buy when price crosses above {self.ma_type}{self.ma_period} on {self.timeframe}, Sell when price crosses below {self.ma_type}{self.ma_period} on {self.timeframe}"
        else:
            return f"Buy when price > {self.ma_type}{self.ma_period} on {self.timeframe}, Sell when price < {self.ma_type}{self.ma_period} on {self.timeframe}"

class SingleMAStrategyGenerator:
    """Generator for Single MA Strategies"""
    
    def __init__(self, ma_types: List[str] = None, ma_periods: List[int] = None, 
                 timeframes: List[str] = None, signal_types: List[str] = None):
        """
        Initialize strategy generator
        
        Args:
            ma_types: List of MA types to test
            ma_periods: List of MA periods to test
            timeframes: List of timeframes to test
            signal_types: List of signal types to test
        """
        from config.settings import MA_TYPES, MA_PERIODS, TIMEFRAMES
        
        self.ma_types = ma_types or MA_TYPES
        self.ma_periods = ma_periods or MA_PERIODS
        self.timeframes = timeframes or list(TIMEFRAMES.keys())
        self.signal_types = signal_types or ['crossover', 'position']
    
    def generate_strategies(self) -> List[SingleMAStrategy]:
        """
        Generate all possible Single MA strategies
        
        Returns:
            List of SingleMAStrategy objects
        """
        strategies = []
        
        for ma_type in self.ma_types:
            for ma_period in self.ma_periods:
                for timeframe in self.timeframes:
                    for signal_type in self.signal_types:
                        strategy = SingleMAStrategy(
                            ma_type=ma_type,
                            ma_period=ma_period,
                            timeframe=timeframe,
                            signal_type=signal_type
                        )
                        strategies.append(strategy)
        
        logger.info(f"Generated {len(strategies)} Single MA strategies")
        return strategies
    
    def generate_filtered_strategies(self, max_periods: int = 50) -> List[SingleMAStrategy]:
        """
        Generate filtered Single MA strategies with reasonable parameters
        
        Args:
            max_periods: Maximum MA period to test
            
        Returns:
            List of filtered SingleMAStrategy objects
        """
        strategies = []
        
        # Filter periods to reasonable range
        filtered_periods = [p for p in self.ma_periods if p <= max_periods]
        
        # Focus on most common MA types and periods
        common_periods = [5, 10, 20, 50, 100, 200]
        common_periods = [p for p in common_periods if p <= max_periods]
        
        for ma_type in self.ma_types:
            for ma_period in common_periods:
                for timeframe in self.timeframes:
                    for signal_type in self.signal_types:
                        strategy = SingleMAStrategy(
                            ma_type=ma_type,
                            ma_period=ma_period,
                            timeframe=timeframe,
                            signal_type=signal_type
                        )
                        strategies.append(strategy)
        
        logger.info(f"Generated {len(strategies)} filtered Single MA strategies")
        return strategies