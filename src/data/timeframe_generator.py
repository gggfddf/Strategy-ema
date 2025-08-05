"""
Timeframe generator module for creating higher timeframes from 1-minute OHLCV data
"""

import pandas as pd
import numpy as np
from typing import Dict, List
import logging
from config.settings import TIMEFRAMES, DATA_PROCESSED_DIR

logger = logging.getLogger(__name__)

class TimeframeGenerator:
    """Generates higher timeframes from 1-minute OHLCV data"""
    
    def __init__(self):
        self.timeframes = TIMEFRAMES
        self.processed_dir = DATA_PROCESSED_DIR
        self.processed_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_all_timeframes(self, m1_data: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """
        Generate all timeframes from M1 data
        
        Args:
            m1_data: 1-minute OHLCV DataFrame with datetime index
            
        Returns:
            Dictionary mapping timeframe name to DataFrame
        """
        logger.info("Generating all timeframes from M1 data...")
        
        timeframe_data = {}
        
        # Start with M1 data
        timeframe_data['M1'] = m1_data.copy()
        
        # Generate higher timeframes
        for tf_name, tf_period in self.timeframes.items():
            if tf_name == 'M1':
                continue
                
            try:
                tf_data = self._resample_timeframe(m1_data, tf_period, tf_name)
                timeframe_data[tf_name] = tf_data
                logger.info(f"Generated {tf_name} timeframe with {len(tf_data)} bars")
            except Exception as e:
                logger.error(f"Error generating {tf_name}: {e}")
        
        # Save processed data
        self._save_timeframe_data(timeframe_data)
        
        return timeframe_data
    
    def _resample_timeframe(self, m1_data: pd.DataFrame, period: str, tf_name: str) -> pd.DataFrame:
        """
        Resample M1 data to a specific timeframe
        
        Args:
            m1_data: 1-minute OHLCV data
            period: Pandas time period string (e.g., '5T', '1H', '1D')
            tf_name: Timeframe name for logging
            
        Returns:
            Resampled DataFrame
        """
        # Ensure index is datetime
        if not isinstance(m1_data.index, pd.DatetimeIndex):
            raise ValueError("DataFrame index must be DatetimeIndex")
        
        # Define OHLCV aggregation rules
        agg_rules = {
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum'
        }
        
        # Add additional columns if they exist
        additional_cols = ['returns', 'log_returns']
        for col in additional_cols:
            if col in m1_data.columns:
                agg_rules[col] = 'sum'
        
        # Resample the data
        resampled = m1_data.resample(period).agg(agg_rules)
        
        # Remove rows with all NaN values (incomplete periods)
        resampled = resampled.dropna()
        
        # Recalculate returns for the new timeframe
        if 'close' in resampled.columns:
            resampled['returns'] = resampled['close'].pct_change()
            resampled['log_returns'] = np.log(resampled['close'] / resampled['close'].shift(1))
        
        return resampled
    
    def _save_timeframe_data(self, timeframe_data: Dict[str, pd.DataFrame]):
        """
        Save generated timeframe data to disk
        
        Args:
            timeframe_data: Dictionary of timeframe DataFrames
        """
        for tf_name, df in timeframe_data.items():
            file_path = self.processed_dir / f"{tf_name.lower()}_data.parquet"
            try:
                df.to_parquet(file_path)
                logger.info(f"Saved {tf_name} data to {file_path}")
            except Exception as e:
                logger.error(f"Error saving {tf_name} data: {e}")
    
    def load_timeframe_data(self, tf_name: str) -> pd.DataFrame:
        """
        Load specific timeframe data from disk
        
        Args:
            tf_name: Timeframe name (e.g., 'M5', 'H1', 'D')
            
        Returns:
            DataFrame for the specified timeframe
        """
        file_path = self.processed_dir / f"{tf_name.lower()}_data.parquet"
        
        if not file_path.exists():
            raise FileNotFoundError(f"Timeframe data not found: {file_path}")
        
        return pd.read_parquet(file_path)
    
    def get_timeframe_info(self, timeframe_data: Dict[str, pd.DataFrame]) -> Dict[str, Dict]:
        """
        Get information about all generated timeframes
        
        Args:
            timeframe_data: Dictionary of timeframe DataFrames
            
        Returns:
            Dictionary with timeframe information
        """
        info = {}
        
        for tf_name, df in timeframe_data.items():
            info[tf_name] = {
                'rows': len(df),
                'start_date': df.index.min(),
                'end_date': df.index.max(),
                'duration': df.index.max() - df.index.min(),
                'avg_volume': df['volume'].mean() if 'volume' in df.columns else None,
                'avg_price': df['close'].mean(),
                'volatility': df['returns'].std() if 'returns' in df.columns else None
            }
        
        return info
    
    def validate_timeframe_data(self, timeframe_data: Dict[str, pd.DataFrame]) -> bool:
        """
        Validate generated timeframe data
        
        Args:
            timeframe_data: Dictionary of timeframe DataFrames
            
        Returns:
            True if all timeframes are valid
        """
        for tf_name, df in timeframe_data.items():
            # Check required columns
            required_cols = ['open', 'high', 'low', 'close', 'volume']
            missing_cols = [col for col in required_cols if col not in df.columns]
            
            if missing_cols:
                logger.error(f"Missing columns in {tf_name}: {missing_cols}")
                return False
            
            # Check for null values
            null_counts = df[required_cols].isnull().sum()
            if null_counts.sum() > 0:
                logger.warning(f"Found null values in {tf_name}: {null_counts}")
            
            # Check OHLC relationships
            invalid_ohlc = (
                (df['high'] < df['low']) |
                (df['high'] < df['open']) |
                (df['high'] < df['close']) |
                (df['low'] > df['open']) |
                (df['low'] > df['close'])
            )
            
            if invalid_ohlc.sum() > 0:
                logger.error(f"Found {invalid_ohlc.sum()} invalid OHLC rows in {tf_name}")
                return False
        
        return True
    
    def get_timeframe_statistics(self, timeframe_data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """
        Generate statistics for all timeframes
        
        Args:
            timeframe_data: Dictionary of timeframe DataFrames
            
        Returns:
            DataFrame with timeframe statistics
        """
        stats = []
        
        for tf_name, df in timeframe_data.items():
            stat = {
                'timeframe': tf_name,
                'rows': len(df),
                'start_date': df.index.min(),
                'end_date': df.index.max(),
                'avg_price': df['close'].mean(),
                'price_std': df['close'].std(),
                'avg_volume': df['volume'].mean(),
                'volume_std': df['volume'].std(),
                'avg_return': df['returns'].mean() if 'returns' in df.columns else None,
                'return_std': df['returns'].std() if 'returns' in df.columns else None,
                'min_price': df['close'].min(),
                'max_price': df['close'].max(),
                'total_volume': df['volume'].sum()
            }
            stats.append(stat)
        
        return pd.DataFrame(stats)