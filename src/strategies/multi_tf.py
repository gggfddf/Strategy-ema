"""
Multi-Timeframe Strategy Implementation
Multi-Timeframe Trend Alignment Strategies
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from .base import BaseStrategy
import logging

logger = logging.getLogger(__name__)

class MultiTimeframeStrategy(BaseStrategy):
    """Multi-Timeframe Trend Alignment Strategy"""
    
    def __init__(self, entry_tf: str, entry_ma_type: str, entry_ma_period: int,
                 trend_tf: str, trend_ma_type: str, trend_ma_period: int,
                 alignment_type: str = 'slope'):
        """
        Initialize Multi-Timeframe Strategy
        
        Args:
            entry_tf: Entry timeframe
            entry_ma_type: Entry MA type
            entry_ma_period: Entry MA period
            trend_tf: Trend confirmation timeframe
            trend_ma_type: Trend MA type
            trend_ma_period: Trend MA period
            alignment_type: Type of alignment ('slope', 'position', 'both')
        """
        name = f"MultiTF_{entry_tf}_{entry_ma_type}{entry_ma_period}_{trend_tf}_{trend_ma_type}{trend_ma_period}_{alignment_type}"
        super().__init__(name, 'multi_timeframe')
        
        self.entry_tf = entry_tf
        self.entry_ma_type = entry_ma_type
        self.entry_ma_period = entry_ma_period
        self.trend_tf = trend_tf
        self.trend_ma_type = trend_ma_type
        self.trend_ma_period = trend_ma_period
        self.alignment_type = alignment_type
        
        self.parameters = {
            'entry_tf': entry_tf,
            'entry_ma_type': entry_ma_type,
            'entry_ma_period': entry_ma_period,
            'trend_tf': trend_tf,
            'trend_ma_type': trend_ma_type,
            'trend_ma_period': trend_ma_period,
            'alignment_type': alignment_type
        }
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """
        Generate trading signals based on multi-timeframe alignment
        
        Args:
            data: OHLCV DataFrame with multi-timeframe features
            
        Returns:
            Series with signals (1 for buy, -1 for sell, 0 for hold)
        """
        signals = pd.Series(0, index=data.index)
        
        # Entry signal features
        entry_ma_col = f"{self.entry_ma_type.lower()}_{self.entry_ma_period}"
        entry_price_above = f"price_above_{entry_ma_col}"
        entry_price_below = f"price_below_{entry_ma_col}"
        
        # Trend confirmation features
        trend_slope_bullish = f"trend_aligned_{self.trend_tf}_{self.trend_ma_type.lower()}_{self.trend_ma_period}_bullish"
        trend_slope_bearish = f"trend_aligned_{self.trend_tf}_{self.trend_ma_type.lower()}_{self.trend_ma_period}_bearish"
        trend_price_above = f"price_aligned_{self.trend_tf}_{self.trend_ma_type.lower()}_{self.trend_ma_period}_above"
        trend_price_below = f"price_aligned_{self.trend_tf}_{self.trend_ma_type.lower()}_{self.trend_ma_period}_below"
        
        # Check if required features exist
        required_features = [entry_price_above, entry_price_below]
        
        if self.alignment_type in ['slope', 'both']:
            required_features.extend([trend_slope_bullish, trend_slope_bearish])
        
        if self.alignment_type in ['position', 'both']:
            required_features.extend([trend_price_above, trend_price_below])
        
        missing_features = [f for f in required_features if f not in data.columns]
        if missing_features:
            logger.error(f"Missing features: {missing_features}")
            return signals
        
        # Generate signals based on alignment type
        if self.alignment_type == 'slope':
            # Buy: price above entry MA AND trend MA slope is bullish
            buy_signal = data[entry_price_above] & data[trend_slope_bullish]
            # Sell: price below entry MA AND trend MA slope is bearish
            sell_signal = data[entry_price_below] & data[trend_slope_bearish]
            
        elif self.alignment_type == 'position':
            # Buy: price above entry MA AND trend price above trend MA
            buy_signal = data[entry_price_above] & data[trend_price_above]
            # Sell: price below entry MA AND trend price below trend MA
            sell_signal = data[entry_price_below] & data[trend_price_below]
            
        elif self.alignment_type == 'both':
            # Buy: price above entry MA AND trend slope bullish AND trend price above trend MA
            buy_signal = (data[entry_price_above] & 
                         data[trend_slope_bullish] & 
                         data[trend_price_above])
            # Sell: price below entry MA AND trend slope bearish AND trend price below trend MA
            sell_signal = (data[entry_price_below] & 
                          data[trend_slope_bearish] & 
                          data[trend_price_below])
        
        else:
            logger.error(f"Unknown alignment type: {self.alignment_type}")
            return signals
        
        # Apply signals
        signals[buy_signal] = 1
        signals[sell_signal] = -1
        
        return signals
    
    def get_strategy_description(self) -> str:
        """Get human-readable strategy description"""
        if self.alignment_type == 'slope':
            return f"Buy when price > {self.entry_ma_type}{self.entry_ma_period} on {self.entry_tf} AND {self.trend_ma_type}{self.trend_ma_period} sloping up on {self.trend_tf}"
        elif self.alignment_type == 'position':
            return f"Buy when price > {self.entry_ma_type}{self.entry_ma_period} on {self.entry_tf} AND price > {self.trend_ma_type}{self.trend_ma_period} on {self.trend_tf}"
        else:
            return f"Buy when price > {self.entry_ma_type}{self.entry_ma_period} on {self.entry_tf} AND {self.trend_ma_type}{self.trend_ma_period} bullish on {self.trend_tf}"

class CrossTimeframeStrategy(BaseStrategy):
    """Cross-Timeframe Strategy with mixed directional alignment"""
    
    def __init__(self, short_tf: str, short_ma_type: str, short_ma_period: int,
                 long_tf: str, long_ma_type: str, long_ma_period: int,
                 strategy_type: str = 'mixed'):
        """
        Initialize Cross-Timeframe Strategy
        
        Args:
            short_tf: Short timeframe
            short_ma_type: Short timeframe MA type
            short_ma_period: Short timeframe MA period
            long_tf: Long timeframe
            long_ma_type: Long timeframe MA type
            long_ma_period: Long timeframe MA period
            strategy_type: Strategy type ('mixed', 'aligned', 'divergence')
        """
        name = f"CrossTF_{short_tf}_{short_ma_type}{short_ma_period}_{long_tf}_{long_ma_type}{long_ma_period}_{strategy_type}"
        super().__init__(name, 'multi_timeframe')
        
        self.short_tf = short_tf
        self.short_ma_type = short_ma_type
        self.short_ma_period = short_ma_period
        self.long_tf = long_tf
        self.long_ma_type = long_ma_type
        self.long_ma_period = long_ma_period
        self.strategy_type = strategy_type
        
        self.parameters = {
            'short_tf': short_tf,
            'short_ma_type': short_ma_type,
            'short_ma_period': short_ma_period,
            'long_tf': long_tf,
            'long_ma_type': long_ma_type,
            'long_ma_period': long_ma_period,
            'strategy_type': strategy_type
        }
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """
        Generate trading signals based on cross-timeframe analysis
        
        Args:
            data: OHLCV DataFrame with multi-timeframe features
            
        Returns:
            Series with signals (1 for buy, -1 for sell, 0 for hold)
        """
        signals = pd.Series(0, index=data.index)
        
        # Short timeframe features
        short_ma_col = f"{self.short_ma_type.lower()}_{self.short_ma_period}"
        short_price_above = f"price_above_{short_ma_col}"
        short_slope_bullish = f"trend_aligned_{self.short_tf}_{self.short_ma_type.lower()}_{self.short_ma_period}_bullish"
        
        # Long timeframe features
        long_ma_col = f"{self.long_ma_type.lower()}_{self.long_ma_period}"
        long_price_above = f"price_above_{long_ma_col}"
        long_slope_bullish = f"trend_aligned_{self.long_tf}_{self.long_ma_type.lower()}_{self.long_ma_period}_bullish"
        
        # Check if required features exist
        required_features = [short_price_above, short_slope_bullish, long_price_above, long_slope_bullish]
        missing_features = [f for f in required_features if f not in data.columns]
        
        if missing_features:
            logger.error(f"Missing features: {missing_features}")
            return signals
        
        if self.strategy_type == 'mixed':
            # Mixed strategy: short timeframe bullish + long timeframe confirmation
            buy_signal = data[short_slope_bullish] & data[long_price_above]
            sell_signal = ~data[short_slope_bullish] & ~data[long_price_above]
            
        elif self.strategy_type == 'aligned':
            # Aligned strategy: both timeframes bullish
            buy_signal = data[short_slope_bullish] & data[long_slope_bullish]
            sell_signal = ~data[short_slope_bullish] & ~data[long_slope_bullish]
            
        elif self.strategy_type == 'divergence':
            # Divergence strategy: short bullish, long bearish (or vice versa)
            buy_signal = data[short_slope_bullish] & ~data[long_slope_bullish]
            sell_signal = ~data[short_slope_bullish] & data[long_slope_bullish]
            
        else:
            logger.error(f"Unknown strategy type: {self.strategy_type}")
            return signals
        
        # Apply signals
        signals[buy_signal] = 1
        signals[sell_signal] = -1
        
        return signals
    
    def get_strategy_description(self) -> str:
        """Get human-readable strategy description"""
        if self.strategy_type == 'mixed':
            return f"Buy when {self.short_ma_type}{self.short_ma_period} bullish on {self.short_tf} and price > {self.long_ma_type}{self.long_ma_period} on {self.long_tf}"
        elif self.strategy_type == 'aligned':
            return f"Buy when {self.short_ma_type}{self.short_ma_period} and {self.long_ma_type}{self.long_ma_period} both bullish on {self.short_tf} and {self.long_tf}"
        else:
            return f"Buy when {self.short_ma_type}{self.short_ma_period} bullish on {self.short_tf} but {self.long_ma_type}{self.long_ma_period} bearish on {self.long_tf}"

class MultiTimeframeStrategyGenerator:
    """Generator for Multi-Timeframe Strategies"""
    
    def __init__(self, ma_types: List[str] = None, ma_periods: List[int] = None, 
                 timeframes: List[str] = None, alignment_types: List[str] = None):
        """
        Initialize strategy generator
        
        Args:
            ma_types: List of MA types to test
            ma_periods: List of MA periods to test
            timeframes: List of timeframes to test
            alignment_types: List of alignment types to test
        """
        from config.settings import MA_TYPES, MA_PERIODS, TIMEFRAMES
        
        self.ma_types = ma_types or MA_TYPES
        self.ma_periods = ma_periods or MA_PERIODS
        self.timeframes = timeframes or list(TIMEFRAMES.keys())
        self.alignment_types = alignment_types or ['slope', 'position', 'both']
    
    def generate_strategies(self) -> List[MultiTimeframeStrategy]:
        """
        Generate all possible multi-timeframe strategies
        
        Returns:
            List of MultiTimeframeStrategy objects
        """
        strategies = []
        
        for entry_tf in self.timeframes:
            for entry_ma_type in self.ma_types:
                for entry_ma_period in self.ma_periods:
                    for trend_tf in self.timeframes:
                        if entry_tf != trend_tf:  # Different timeframes
                            for trend_ma_type in self.ma_types:
                                for trend_ma_period in self.ma_periods:
                                    for alignment_type in self.alignment_types:
                                        strategy = MultiTimeframeStrategy(
                                            entry_tf=entry_tf,
                                            entry_ma_type=entry_ma_type,
                                            entry_ma_period=entry_ma_period,
                                            trend_tf=trend_tf,
                                            trend_ma_type=trend_ma_type,
                                            trend_ma_period=trend_ma_period,
                                            alignment_type=alignment_type
                                        )
                                        strategies.append(strategy)
        
        logger.info(f"Generated {len(strategies)} multi-timeframe strategies")
        return strategies
    
    def generate_filtered_strategies(self, max_periods: int = 100) -> List[MultiTimeframeStrategy]:
        """
        Generate filtered multi-timeframe strategies with reasonable parameters
        
        Args:
            max_periods: Maximum MA period to test
            
        Returns:
            List of filtered MultiTimeframeStrategy objects
        """
        strategies = []
        
        # Common timeframe combinations
        tf_combinations = [
            ('M5', 'H1'),
            ('M15', 'H1'),
            ('M30', 'H1'),
            ('H1', 'H4'),
            ('H1', 'D'),
            ('H4', 'D'),
            ('M5', 'H4'),
            ('M15', 'D'),
        ]
        
        # Common MA combinations
        ma_combinations = [
            ('SMA', 10, 'SMA', 50),
            ('EMA', 20, 'SMA', 100),
            ('EMA', 12, 'EMA', 26),
            ('WMA', 10, 'SMA', 50),
            ('SMA', 20, 'SMA', 200),
        ]
        
        for entry_tf, trend_tf in tf_combinations:
            for entry_ma_type, entry_period, trend_ma_type, trend_period in ma_combinations:
                if entry_period <= max_periods and trend_period <= max_periods:
                    for alignment_type in self.alignment_types:
                        strategy = MultiTimeframeStrategy(
                            entry_tf=entry_tf,
                            entry_ma_type=entry_ma_type,
                            entry_ma_period=entry_period,
                            trend_tf=trend_tf,
                            trend_ma_type=trend_ma_type,
                            trend_ma_period=trend_period,
                            alignment_type=alignment_type
                        )
                        strategies.append(strategy)
        
        logger.info(f"Generated {len(strategies)} filtered multi-timeframe strategies")
        return strategies
    
    def generate_cross_timeframe_strategies(self, max_periods: int = 100) -> List[CrossTimeframeStrategy]:
        """
        Generate cross-timeframe strategies
        
        Args:
            max_periods: Maximum MA period to test
            
        Returns:
            List of CrossTimeframeStrategy objects
        """
        strategies = []
        
        # Short-long timeframe combinations
        tf_combinations = [
            ('M5', 'H1'),
            ('M15', 'H1'),
            ('H1', 'H4'),
            ('H1', 'D'),
        ]
        
        # MA combinations
        ma_combinations = [
            ('SMA', 5, 'SMA', 33),
            ('EMA', 10, 'EMA', 50),
            ('SMA', 20, 'SMA', 100),
        ]
        
        strategy_types = ['mixed', 'aligned', 'divergence']
        
        for short_tf, long_tf in tf_combinations:
            for short_ma_type, short_period, long_ma_type, long_period in ma_combinations:
                if short_period <= max_periods and long_period <= max_periods:
                    for strategy_type in strategy_types:
                        strategy = CrossTimeframeStrategy(
                            short_tf=short_tf,
                            short_ma_type=short_ma_type,
                            short_ma_period=short_period,
                            long_tf=long_tf,
                            long_ma_type=long_ma_type,
                            long_ma_period=long_period,
                            strategy_type=strategy_type
                        )
                        strategies.append(strategy)
        
        logger.info(f"Generated {len(strategies)} cross-timeframe strategies")
        return strategies