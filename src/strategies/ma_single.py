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
            data: OHLCV DataFrame with MA features
            
        Returns:
            Series with signals (1 for buy, -1 for sell, 0 for hold)
        """
        # Get MA column name
        ma_col = f"{self.ma_type.lower()}_{self.ma_period}"
        
        if ma_col not in data.columns:
            logger.error(f"MA column {ma_col} not found in data")
            return pd.Series(0, index=data.index)
        
        # Get price vs MA features
        price_above_col = f"price_above_{ma_col}"
        price_below_col = f"price_below_{ma_col}"
        
        if price_above_col not in data.columns or price_below_col not in data.columns:
            logger.error(f"Price vs MA feature columns not found")
            return pd.Series(0, index=data.index)
        
        signals = pd.Series(0, index=data.index)
        
        if self.signal_type == 'crossover':
            # Crossover signals
            # Buy when price crosses above MA
            buy_signal = (data[price_above_col] & ~data[price_above_col].shift(1))
            # Sell when price crosses below MA
            sell_signal = (data[price_below_col] & ~data[price_below_col].shift(1))
            
            signals[buy_signal] = 1
            signals[sell_signal] = -1
            
        elif self.signal_type == 'position':
            # Position-based signals
            # Buy when price is above MA
            signals[data[price_above_col]] = 1
            # Sell when price is below MA
            signals[data[price_below_col]] = -1
            
        else:
            logger.error(f"Unknown signal type: {self.signal_type}")
            return pd.Series(0, index=data.index)
        
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