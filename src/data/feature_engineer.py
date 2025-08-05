"""
Feature engineering module for computing moving averages and generating strategy features
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import logging
from config.settings import MA_PERIODS, MA_TYPES, TIMEFRAMES

logger = logging.getLogger(__name__)

class FeatureEngineer:
    """Computes moving averages and generates features for strategy discovery"""
    
    def __init__(self):
        self.ma_periods = MA_PERIODS
        self.ma_types = MA_TYPES
        self.timeframes = list(TIMEFRAMES.keys())
        
    def compute_all_moving_averages(self, timeframe_data: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """
        Compute all moving averages for all timeframes
        
        Args:
            timeframe_data: Dictionary of timeframe DataFrames
            
        Returns:
            Dictionary with enhanced DataFrames
        """
        enhanced_data = {}
        
        for tf_name, df in timeframe_data.items():
            try:
                logger.info(f"Computing MAs for {tf_name} timeframe...")
                
                # Skip if no data
                if df.empty:
                    logger.warning(f"No data for {tf_name} timeframe, skipping")
                    enhanced_data[tf_name] = df
                    continue
                
                enhanced_df = self._compute_timeframe_mas(df, tf_name)
                enhanced_data[tf_name] = enhanced_df
                logger.info(f"Completed MAs for {tf_name}: {enhanced_df.shape}")
            except Exception as e:
                logger.error(f"Error computing MAs for {tf_name}: {e}")
                enhanced_data[tf_name] = df  # Return original data if error
        
        return enhanced_data
    
    def _compute_timeframe_mas(self, df: pd.DataFrame, tf_name: str) -> pd.DataFrame:
        """
        Compute all MAs for a single timeframe
        
        Args:
            df: DataFrame with OHLCV data
            tf_name: Timeframe name
            
        Returns:
            DataFrame with all MAs added
        """
        enhanced_df = df.copy()
        
        # Collect all new features to avoid DataFrame fragmentation
        new_features = {}
        
        # Compute each MA type and period
        for ma_type in self.ma_types:
            for period in self.ma_periods:
                ma_values = self._compute_ma(df['close'], period, ma_type)
                col_name = f"{ma_type.lower()}_{period}"
                new_features[col_name] = ma_values
                
                # Add price vs MA features
                new_features[f"price_above_{col_name}"] = df['close'] > ma_values
                new_features[f"price_below_{col_name}"] = df['close'] < ma_values
                
                # Add MA slope features
                new_features[f"{col_name}_slope"] = self._compute_ma_slope(ma_values)
                
                # Add distance from MA
                new_features[f"distance_from_{col_name}"] = (df['close'] - ma_values) / ma_values
                
                # Add z-score
                new_features[f"{col_name}_zscore"] = self._compute_zscore(df['close'], ma_values)
        
        # Add all features at once to avoid fragmentation
        new_features_df = pd.DataFrame(new_features, index=df.index)
        enhanced_df = pd.concat([enhanced_df, new_features_df], axis=1)
        
        return enhanced_df
    
    def _compute_ma(self, prices: pd.Series, period: int, ma_type: str) -> pd.Series:
        """
        Compute moving average
        
        Args:
            prices: Price series
            period: MA period
            ma_type: Type of MA (SMA, EMA, WMA)
            
        Returns:
            Moving average series
        """
        if ma_type == 'SMA':
            return prices.rolling(window=period).mean()
        elif ma_type == 'EMA':
            return prices.ewm(span=period).mean()
        elif ma_type == 'WMA':
            weights = np.arange(1, period + 1)
            return prices.rolling(window=period).apply(
                lambda x: np.dot(x, weights) / weights.sum(), raw=True
            )
        else:
            raise ValueError(f"Unknown MA type: {ma_type}")
    
    def _compute_ma_slope(self, ma_values: pd.Series, periods: int = 5) -> pd.Series:
        """
        Compute MA slope (trend direction)
        
        Args:
            ma_values: Moving average values
            periods: Number of periods for slope calculation
            
        Returns:
            Slope series (positive = uptrend, negative = downtrend)
        """
        return ma_values.diff(periods) / periods
    
    def _compute_zscore(self, prices: pd.Series, ma_values: pd.Series, window: int = 20) -> pd.Series:
        """
        Compute z-score of price deviation from MA
        
        Args:
            prices: Price series
            ma_values: Moving average values
            window: Window for rolling statistics
            
        Returns:
            Z-score series
        """
        deviation = prices - ma_values
        rolling_std = deviation.rolling(window=window).std()
        return deviation / rolling_std
    
    def generate_crossover_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate MA crossover features
        
        Args:
            df: DataFrame with MA columns
            
        Returns:
            DataFrame with crossover features
        """
        enhanced_df = df.copy()
        
        # Get all MA columns
        ma_columns = [col for col in df.columns if any(ma_type in col for ma_type in self.ma_types)]
        
        # Generate 2-MA crossovers
        for i, ma1 in enumerate(ma_columns):
            for ma2 in ma_columns[i+1:]:
                # Extract period and type from column names
                ma1_info = self._parse_ma_column(ma1)
                ma2_info = self._parse_ma_column(ma2)
                
                if ma1_info and ma2_info:
                    # Only create crossovers where periods are different
                    if ma1_info['period'] != ma2_info['period']:
                        # Determine fast and slow MA
                        if ma1_info['period'] < ma2_info['period']:
                            fast_ma, slow_ma = ma1, ma2
                            fast_info, slow_info = ma1_info, ma2_info
                        else:
                            fast_ma, slow_ma = ma2, ma1
                            fast_info, slow_info = ma2_info, ma1_info
                        
                        # Create crossover features
                        crossover_name = f"crossover_{fast_info['type']}_{fast_info['period']}_above_{slow_info['type']}_{slow_info['period']}"
                        enhanced_df[crossover_name] = (df[fast_ma] > df[slow_ma]) & (df[fast_ma].shift(1) <= df[slow_ma].shift(1))
                        
                        crossover_name_down = f"crossover_{fast_info['type']}_{fast_info['period']}_below_{slow_info['type']}_{slow_info['period']}"
                        enhanced_df[crossover_name_down] = (df[fast_ma] < df[slow_ma]) & (df[fast_ma].shift(1) >= df[slow_ma].shift(1))
        
        return enhanced_df
    
    def _parse_ma_column(self, column_name: str) -> Dict:
        """
        Parse MA column name to extract type and period
        
        Args:
            column_name: MA column name (e.g., 'sma_20', 'ema_50')
            
        Returns:
            Dictionary with MA type and period
        """
        for ma_type in self.ma_types:
            if ma_type.lower() in column_name:
                # Extract period number
                parts = column_name.split('_')
                for part in parts:
                    if part.isdigit():
                        return {
                            'type': ma_type,
                            'period': int(part)
                        }
        return None
    
    def generate_mean_reversion_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate mean reversion features
        
        Args:
            df: DataFrame with MA columns
            
        Returns:
            DataFrame with mean reversion features
        """
        enhanced_df = df.copy()
        
        # Get all MA columns
        ma_columns = [col for col in df.columns if any(ma_type in col for ma_type in self.ma_types)]
        
        for ma_col in ma_columns:
            ma_info = self._parse_ma_column(ma_col)
            if ma_info:
                # Distance from MA
                distance_col = f"distance_from_{ma_col}"
                if distance_col in df.columns:
                    # Overextension features
                    for threshold in [0.01, 0.02, 0.03, 0.05, 0.08, 0.10, 0.15, 0.20]:
                        enhanced_df[f"overextended_above_{ma_info['type']}_{ma_info['period']}_{int(threshold*100)}pct"] = (
                            df[distance_col] > threshold
                        )
                        enhanced_df[f"overextended_below_{ma_info['type']}_{ma_info['period']}_{int(threshold*100)}pct"] = (
                            df[distance_col] < -threshold
                        )
        
        return enhanced_df
    
    def generate_multi_timeframe_features(self, timeframe_data: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """
        Generate multi-timeframe features
        
        Args:
            timeframe_data: Dictionary of timeframe DataFrames
            
        Returns:
            Dictionary with enhanced DataFrames
        """
        enhanced_data = {}
        
        for target_tf, target_df in timeframe_data.items():
            try:
                logger.info(f"Generating multi-timeframe features for {target_tf}...")
                
                if target_df.empty:
                    logger.warning(f"No data for {target_tf}, skipping multi-timeframe features")
                    enhanced_data[target_tf] = target_df
                    continue
                
                enhanced_df = target_df.copy()
                
                # Generate features from other timeframes
                for source_tf, source_df in timeframe_data.items():
                    if source_tf != target_tf and not source_df.empty:
                        enhanced_df = self._add_trend_alignment_features(enhanced_df, source_df, source_tf)
                        enhanced_df = self._add_price_alignment_features(enhanced_df, source_df, source_tf)
                
                enhanced_data[target_tf] = enhanced_df
                logger.info(f"Completed multi-timeframe features for {target_tf}: {enhanced_df.shape}")
                
            except Exception as e:
                logger.error(f"Error generating multi-timeframe features for {target_tf}: {e}")
                enhanced_data[target_tf] = target_df
        
        return enhanced_data
    
    def _align_timeframes(self, target_df: pd.DataFrame, source_df: pd.DataFrame) -> pd.DataFrame:
        """
        Align source timeframe data to target timeframe
        
        Args:
            target_df: Target timeframe DataFrame
            source_df: Source timeframe DataFrame
            
        Returns:
            Aligned DataFrame
        """
        # Forward fill the source data to match target timeframe
        aligned = source_df.reindex(target_df.index, method='ffill')
        return aligned
    
    def _add_trend_alignment_features(self, target_df: pd.DataFrame, source_df: pd.DataFrame, source_tf: str) -> pd.DataFrame:
        """
        Add trend alignment features from source timeframe
        
        Args:
            target_df: Target timeframe DataFrame
            source_df: Source timeframe DataFrame
            source_tf: Source timeframe name
            
        Returns:
            DataFrame with trend alignment features
        """
        enhanced_df = target_df.copy()
        
        # Get MA columns from source timeframe
        source_ma_cols = [col for col in source_df.columns if any(ma_type in col for ma_type in self.ma_types)]
        
        for ma_col in source_ma_cols:
            ma_info = self._parse_ma_column(ma_col)
            if ma_info:
                ma_type, period = ma_info
                
                # Create trend alignment features
                bullish_col = f"trend_aligned_{source_tf}_{ma_type}_{period}_bullish"
                bearish_col = f"trend_aligned_{source_tf}_{ma_type}_{period}_bearish"
                
                # Calculate trend direction (slope)
                ma_values = source_df[ma_col]
                ma_slope = ma_values.diff(periods=1)
                
                # Create boolean features
                enhanced_df[bullish_col] = ma_slope > 0
                enhanced_df[bearish_col] = ma_slope < 0
                
                # Fill NaN values with False
                enhanced_df[bullish_col] = enhanced_df[bullish_col].fillna(False)
                enhanced_df[bearish_col] = enhanced_df[bearish_col].fillna(False)
        
        return enhanced_df
    
    def _add_price_alignment_features(self, target_df: pd.DataFrame, source_df: pd.DataFrame, source_tf: str) -> pd.DataFrame:
        """
        Add price alignment features from source timeframe
        
        Args:
            target_df: Target timeframe DataFrame
            source_df: Source timeframe DataFrame
            source_tf: Source timeframe name
            
        Returns:
            DataFrame with price alignment features
        """
        enhanced_df = target_df.copy()
        
        # Get MA columns from source timeframe
        source_ma_cols = [col for col in source_df.columns if any(ma_type in col for ma_type in self.ma_types)]
        
        for ma_col in source_ma_cols:
            ma_info = self._parse_ma_column(ma_col)
            if ma_info:
                ma_type, period = ma_info
                
                # Create price alignment features
                above_col = f"price_aligned_{source_tf}_{ma_type}_{period}_above"
                below_col = f"price_aligned_{source_tf}_{ma_type}_{period}_below"
                
                # Get close price and MA values
                close_col = 'close' if 'close' in source_df.columns else source_df.columns[0]
                close_values = source_df[close_col]
                ma_values = source_df[ma_col]
                
                # Create boolean features
                enhanced_df[above_col] = close_values > ma_values
                enhanced_df[below_col] = close_values < ma_values
                
                # Fill NaN values with False
                enhanced_df[above_col] = enhanced_df[above_col].fillna(False)
                enhanced_df[below_col] = enhanced_df[below_col].fillna(False)
        
        return enhanced_df
    
    def get_feature_summary(self, enhanced_data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """
        Generate summary of all features
        
        Args:
            enhanced_data: Dictionary of enhanced DataFrames
            
        Returns:
            DataFrame with feature summary
        """
        summary = []
        
        for tf_name, df in enhanced_data.items():
            # Count different types of features
            ma_features = len([col for col in df.columns if any(ma_type in col for ma_type in self.ma_types)])
            crossover_features = len([col for col in df.columns if 'crossover' in col])
            mean_reversion_features = len([col for col in df.columns if 'overextended' in col])
            trend_alignment_features = len([col for col in df.columns if 'trend_aligned' in col])
            
            summary.append({
                'timeframe': tf_name,
                'total_features': len(df.columns),
                'ma_features': ma_features,
                'crossover_features': crossover_features,
                'mean_reversion_features': mean_reversion_features,
                'trend_alignment_features': trend_alignment_features,
                'rows': len(df)
            })
        
        return pd.DataFrame(summary)