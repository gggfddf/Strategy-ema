"""
Mean Reversion Strategy Implementation
Mean Reversion Strategies (Price overextension detection)
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from .base import BaseStrategy
import logging

logger = logging.getLogger(__name__)

class MeanReversionStrategy(BaseStrategy):
    """Mean Reversion Strategy"""
    
    def __init__(self, ma_type: str, ma_period: int, timeframe: str,
                 distance_threshold: float, signal_type: str = 'overextension'):
        """
        Initialize Mean Reversion Strategy
        
        Args:
            ma_type: Type of MA (SMA, EMA, WMA)
            ma_period: MA period
            timeframe: Timeframe for the strategy
            distance_threshold: Distance threshold for overextension (e.g., 0.05 for 5%)
            signal_type: Signal type ('overextension', 'zscore', 'divergence')
        """
        name = f"MeanRev_{ma_type}{ma_period}_{timeframe}_{int(distance_threshold*100)}pct_{signal_type}"
        super().__init__(name, 'mean_reversion')
        
        self.ma_type = ma_type
        self.ma_period = ma_period
        self.timeframe = timeframe
        self.distance_threshold = distance_threshold
        self.signal_type = signal_type
        
        self.parameters = {
            'ma_type': ma_type,
            'ma_period': ma_period,
            'timeframe': timeframe,
            'distance_threshold': distance_threshold,
            'signal_type': signal_type
        }
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """
        Generate trading signals based on mean reversion
        
        Args:
            data: OHLCV DataFrame with MA features
            
        Returns:
            Series with signals (1 for buy, -1 for sell, 0 for hold)
        """
        signals = pd.Series(0, index=data.index)
        
        # Get MA column name
        ma_col = f"{self.ma_type.lower()}_{self.ma_period}"
        
        if ma_col not in data.columns:
            logger.error(f"MA column {ma_col} not found in data")
            return signals
        
        # Get distance from MA
        distance_col = f"distance_from_{ma_col}"
        
        if distance_col not in data.columns:
            logger.error(f"Distance column {distance_col} not found in data")
            return signals
        
        if self.signal_type == 'overextension':
            # Simple overextension strategy
            # Buy when price is significantly below MA
            buy_signal = data[distance_col] < -self.distance_threshold
            # Sell when price is significantly above MA
            sell_signal = data[distance_col] > self.distance_threshold
            
        elif self.signal_type == 'zscore':
            # Z-score based strategy
            zscore_col = f"{ma_col}_zscore"
            
            if zscore_col not in data.columns:
                logger.error(f"Z-score column {zscore_col} not found in data")
                return signals
            
            # Buy when z-score is below -2 (oversold)
            buy_signal = data[zscore_col] < -2
            # Sell when z-score is above 2 (overbought)
            sell_signal = data[zscore_col] > 2
            
        elif self.signal_type == 'divergence':
            # Divergence strategy: price moving away from MA with momentum
            # Get MA slope
            slope_col = f"{ma_col}_slope"
            
            if slope_col not in data.columns:
                logger.error(f"Slope column {slope_col} not found in data")
                return signals
            
            # Buy when price is below MA but MA slope is positive (converging)
            buy_signal = (data[distance_col] < -self.distance_threshold) & (data[slope_col] > 0)
            # Sell when price is above MA but MA slope is negative (converging)
            sell_signal = (data[distance_col] > self.distance_threshold) & (data[slope_col] < 0)
            
        else:
            logger.error(f"Unknown signal type: {self.signal_type}")
            return signals
        
        # Apply signals
        signals[buy_signal] = 1
        signals[sell_signal] = -1
        
        return signals
    
    def get_strategy_description(self) -> str:
        """Get human-readable strategy description"""
        threshold_pct = int(self.distance_threshold * 100)
        
        if self.signal_type == 'overextension':
            return f"Buy when price is {threshold_pct}% below {self.ma_type}{self.ma_period} on {self.timeframe}, Sell when price is {threshold_pct}% above {self.ma_type}{self.ma_period} on {self.timeframe}"
        elif self.signal_type == 'zscore':
            return f"Buy when price z-score < -2 from {self.ma_type}{self.ma_period} on {self.timeframe}, Sell when z-score > 2"
        else:
            return f"Buy when price {threshold_pct}% below {self.ma_type}{self.ma_period} with positive slope on {self.timeframe}, Sell when price {threshold_pct}% above {self.ma_type}{self.ma_period} with negative slope on {self.timeframe}"

class VolumeMeanReversionStrategy(BaseStrategy):
    """Mean Reversion Strategy with Volume Confirmation"""
    
    def __init__(self, ma_type: str, ma_period: int, timeframe: str,
                 distance_threshold: float, volume_threshold: float = 1.5):
        """
        Initialize Volume Mean Reversion Strategy
        
        Args:
            ma_type: Type of MA (SMA, EMA, WMA)
            ma_period: MA period
            timeframe: Timeframe for the strategy
            distance_threshold: Distance threshold for overextension
            volume_threshold: Volume threshold multiplier
        """
        name = f"VolMeanRev_{ma_type}{ma_period}_{timeframe}_{int(distance_threshold*100)}pct_vol{volume_threshold}"
        super().__init__(name, 'mean_reversion')
        
        self.ma_type = ma_type
        self.ma_period = ma_period
        self.timeframe = timeframe
        self.distance_threshold = distance_threshold
        self.volume_threshold = volume_threshold
        
        self.parameters = {
            'ma_type': ma_type,
            'ma_period': ma_period,
            'timeframe': timeframe,
            'distance_threshold': distance_threshold,
            'volume_threshold': volume_threshold
        }
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """
        Generate trading signals based on mean reversion with volume confirmation
        
        Args:
            data: OHLCV DataFrame with MA features
            
        Returns:
            Series with signals (1 for buy, -1 for sell, 0 for hold)
        """
        signals = pd.Series(0, index=data.index)
        
        # Get MA column name
        ma_col = f"{self.ma_type.lower()}_{self.ma_period}"
        
        if ma_col not in data.columns:
            logger.error(f"MA column {ma_col} not found in data")
            return signals
        
        # Get distance from MA
        distance_col = f"distance_from_{ma_col}"
        
        if distance_col not in data.columns:
            logger.error(f"Distance column {distance_col} not found in data")
            return signals
        
        # Calculate volume confirmation
        avg_volume = data['volume'].rolling(window=20).mean()
        high_volume = data['volume'] > (avg_volume * self.volume_threshold)
        
        # Buy when price is below MA with high volume
        buy_signal = (data[distance_col] < -self.distance_threshold) & high_volume
        
        # Sell when price is above MA with high volume
        sell_signal = (data[distance_col] > self.distance_threshold) & high_volume
        
        # Apply signals
        signals[buy_signal] = 1
        signals[sell_signal] = -1
        
        return signals
    
    def get_strategy_description(self) -> str:
        """Get human-readable strategy description"""
        threshold_pct = int(self.distance_threshold * 100)
        return f"Buy when price is {threshold_pct}% below {self.ma_type}{self.ma_period} with {self.volume_threshold}x volume on {self.timeframe}, Sell when price is {threshold_pct}% above {self.ma_type}{self.ma_period} with {self.volume_threshold}x volume on {self.timeframe}"

class MomentumMeanReversionStrategy(BaseStrategy):
    """Mean Reversion Strategy with Momentum Confirmation"""
    
    def __init__(self, ma_type: str, ma_period: int, timeframe: str,
                 distance_threshold: float, momentum_period: int = 14):
        """
        Initialize Momentum Mean Reversion Strategy
        
        Args:
            ma_type: Type of MA (SMA, EMA, WMA)
            ma_period: MA period
            timeframe: Timeframe for the strategy
            distance_threshold: Distance threshold for overextension
            momentum_period: Period for momentum calculation
        """
        name = f"MomMeanRev_{ma_type}{ma_period}_{timeframe}_{int(distance_threshold*100)}pct_mom{momentum_period}"
        super().__init__(name, 'mean_reversion')
        
        self.ma_type = ma_type
        self.ma_period = ma_period
        self.timeframe = timeframe
        self.distance_threshold = distance_threshold
        self.momentum_period = momentum_period
        
        self.parameters = {
            'ma_type': ma_type,
            'ma_period': ma_period,
            'timeframe': timeframe,
            'distance_threshold': distance_threshold,
            'momentum_period': momentum_period
        }
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """
        Generate trading signals based on mean reversion with momentum confirmation
        
        Args:
            data: OHLCV DataFrame with MA features
            
        Returns:
            Series with signals (1 for buy, -1 for sell, 0 for hold)
        """
        signals = pd.Series(0, index=data.index)
        
        # Get MA column name
        ma_col = f"{self.ma_type.lower()}_{self.ma_period}"
        
        if ma_col not in data.columns:
            logger.error(f"MA column {ma_col} not found in data")
            return signals
        
        # Get distance from MA
        distance_col = f"distance_from_{ma_col}"
        
        if distance_col not in data.columns:
            logger.error(f"Distance column {distance_col} not found in data")
            return signals
        
        # Calculate momentum (rate of change)
        momentum = data['close'].pct_change(self.momentum_period)
        
        # Buy when price is below MA and momentum is turning positive
        buy_signal = (data[distance_col] < -self.distance_threshold) & (momentum > 0)
        
        # Sell when price is above MA and momentum is turning negative
        sell_signal = (data[distance_col] > self.distance_threshold) & (momentum < 0)
        
        # Apply signals
        signals[buy_signal] = 1
        signals[sell_signal] = -1
        
        return signals
    
    def get_strategy_description(self) -> str:
        """Get human-readable strategy description"""
        threshold_pct = int(self.distance_threshold * 100)
        return f"Buy when price is {threshold_pct}% below {self.ma_type}{self.ma_period} with positive {self.momentum_period}-period momentum on {self.timeframe}, Sell when price is {threshold_pct}% above {self.ma_type}{self.ma_period} with negative {self.momentum_period}-period momentum on {self.timeframe}"

class MeanReversionStrategyGenerator:
    """Generator for Mean Reversion Strategies"""
    
    def __init__(self, ma_types: List[str] = None, ma_periods: List[int] = None, 
                 timeframes: List[str] = None, distance_thresholds: List[float] = None,
                 signal_types: List[str] = None):
        """
        Initialize strategy generator
        
        Args:
            ma_types: List of MA types to test
            ma_periods: List of MA periods to test
            timeframes: List of timeframes to test
            distance_thresholds: List of distance thresholds to test
            signal_types: List of signal types to test
        """
        from config.settings import MA_TYPES, MA_PERIODS, TIMEFRAMES, DISTANCE_THRESHOLDS
        
        self.ma_types = ma_types or MA_TYPES
        self.ma_periods = ma_periods or MA_PERIODS
        self.timeframes = timeframes or list(TIMEFRAMES.keys())
        self.distance_thresholds = distance_thresholds or DISTANCE_THRESHOLDS
        self.signal_types = signal_types or ['overextension', 'zscore', 'divergence']
    
    def generate_strategies(self) -> List[MeanReversionStrategy]:
        """
        Generate all possible mean reversion strategies
        
        Returns:
            List of MeanReversionStrategy objects
        """
        strategies = []
        
        for ma_type in self.ma_types:
            for ma_period in self.ma_periods:
                for timeframe in self.timeframes:
                    for distance_threshold in self.distance_thresholds:
                        for signal_type in self.signal_types:
                            strategy = MeanReversionStrategy(
                                ma_type=ma_type,
                                ma_period=ma_period,
                                timeframe=timeframe,
                                distance_threshold=distance_threshold,
                                signal_type=signal_type
                            )
                            strategies.append(strategy)
        
        logger.info(f"Generated {len(strategies)} mean reversion strategies")
        return strategies
    
    def generate_filtered_strategies(self, max_periods: int = 100) -> List[MeanReversionStrategy]:
        """
        Generate filtered mean reversion strategies with reasonable parameters
        
        Args:
            max_periods: Maximum MA period to test
            
        Returns:
            List of filtered MeanReversionStrategy objects
        """
        strategies = []
        
        # Common MA periods for mean reversion
        common_periods = [20, 50, 100, 200]
        common_periods = [p for p in common_periods if p <= max_periods]
        
        # Common distance thresholds
        common_thresholds = [0.02, 0.03, 0.05, 0.08, 0.10]  # 2%, 3%, 5%, 8%, 10%
        
        for ma_type in self.ma_types:
            for ma_period in common_periods:
                for timeframe in self.timeframes:
                    for distance_threshold in common_thresholds:
                        for signal_type in self.signal_types:
                            strategy = MeanReversionStrategy(
                                ma_type=ma_type,
                                ma_period=ma_period,
                                timeframe=timeframe,
                                distance_threshold=distance_threshold,
                                signal_type=signal_type
                            )
                            strategies.append(strategy)
        
        logger.info(f"Generated {len(strategies)} filtered mean reversion strategies")
        return strategies
    
    def generate_volume_strategies(self, max_periods: int = 100) -> List[VolumeMeanReversionStrategy]:
        """
        Generate volume-based mean reversion strategies
        
        Args:
            max_periods: Maximum MA period to test
            
        Returns:
            List of VolumeMeanReversionStrategy objects
        """
        strategies = []
        
        # Common parameters for volume strategies
        common_periods = [20, 50, 100]
        common_periods = [p for p in common_periods if p <= max_periods]
        common_thresholds = [0.03, 0.05, 0.08]
        volume_thresholds = [1.5, 2.0, 2.5]
        
        for ma_type in self.ma_types:
            for ma_period in common_periods:
                for timeframe in self.timeframes:
                    for distance_threshold in common_thresholds:
                        for volume_threshold in volume_thresholds:
                            strategy = VolumeMeanReversionStrategy(
                                ma_type=ma_type,
                                ma_period=ma_period,
                                timeframe=timeframe,
                                distance_threshold=distance_threshold,
                                volume_threshold=volume_threshold
                            )
                            strategies.append(strategy)
        
        logger.info(f"Generated {len(strategies)} volume-based mean reversion strategies")
        return strategies
    
    def generate_momentum_strategies(self, max_periods: int = 100) -> List[MomentumMeanReversionStrategy]:
        """
        Generate momentum-based mean reversion strategies
        
        Args:
            max_periods: Maximum MA period to test
            
        Returns:
            List of MomentumMeanReversionStrategy objects
        """
        strategies = []
        
        # Common parameters for momentum strategies
        common_periods = [20, 50, 100]
        common_periods = [p for p in common_periods if p <= max_periods]
        common_thresholds = [0.03, 0.05, 0.08]
        momentum_periods = [10, 14, 20]
        
        for ma_type in self.ma_types:
            for ma_period in common_periods:
                for timeframe in self.timeframes:
                    for distance_threshold in common_thresholds:
                        for momentum_period in momentum_periods:
                            strategy = MomentumMeanReversionStrategy(
                                ma_type=ma_type,
                                ma_period=ma_period,
                                timeframe=timeframe,
                                distance_threshold=distance_threshold,
                                momentum_period=momentum_period
                            )
                            strategies.append(strategy)
        
        logger.info(f"Generated {len(strategies)} momentum-based mean reversion strategies")
        return strategies