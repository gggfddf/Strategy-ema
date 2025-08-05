"""
Data loading and validation module for 1-minute OHLCV CSV data
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional
import logging
from config.settings import DATA_RAW_DIR

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataLoader:
    """Handles loading and validation of 1-minute OHLCV CSV data"""
    
    def __init__(self, data_dir: Path = DATA_RAW_DIR):
        self.data_dir = data_dir
        self.required_columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        
    def load_csv_files(self, pattern: str = "*.csv") -> Dict[str, pd.DataFrame]:
        """
        Load all CSV files from the raw data directory
        
        Args:
            pattern: File pattern to match
            
        Returns:
            Dictionary mapping filename to DataFrame
        """
        csv_files = list(self.data_dir.glob(pattern))
        
        if not csv_files:
            raise FileNotFoundError(f"No CSV files found in {self.data_dir}")
            
        data_dict = {}
        
        for file_path in csv_files:
            try:
                df = self._load_single_file(file_path)
                if df is not None:
                    data_dict[file_path.stem] = df
                    logger.info(f"Loaded {file_path.name} with {len(df)} rows")
            except Exception as e:
                logger.error(f"Error loading {file_path}: {e}")
                
        return data_dict
    
    def _load_single_file(self, file_path: Path) -> Optional[pd.DataFrame]:
        """
        Load a single CSV file
        
        Args:
            file_path: Path to CSV file
            
        Returns:
            DataFrame or None if loading fails
        """
        try:
            logger.info(f"Loading {file_path}")
            
            # Try different delimiters
            for delimiter in [',', '\t', ';']:
                try:
                    df = pd.read_csv(file_path, delimiter=delimiter)
                    if len(df.columns) >= 5:  # At least OHLCV
                        logger.info(f"Successfully loaded with delimiter '{delimiter}'")
                        break
                except:
                    continue
            else:
                logger.error(f"Could not parse {file_path} with any delimiter")
                return None
            
            # Standardize column names
            df = self._standardize_columns(df)
            
            # Validate data
            if not self._validate_data(df):
                logger.error(f"Data validation failed for {file_path}")
                return None
            
            # Preprocess data
            df = self._preprocess_data(df)
            
            logger.info(f"Successfully loaded {file_path} with shape {df.shape}")
            return df
            
        except Exception as e:
            logger.error(f"Error loading {file_path}: {e}")
            return None
    
    def _standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Standardize column names to expected format
        
        Args:
            df: Input DataFrame
            
        Returns:
            DataFrame with standardized column names
        """
        # Common column name variations
        column_mapping = {
            'date': 'timestamp',
            'time': 'timestamp',
            'datetime': 'timestamp',
            'o': 'open',
            'h': 'high',
            'l': 'low',
            'c': 'close',
            'v': 'volume',
            'vol': 'volume'
        }
        
        # Rename columns if they exist
        for old_name, new_name in column_mapping.items():
            if old_name in df.columns:
                df = df.rename(columns={old_name: new_name})
        
        return df
    
    def _validate_data(self, df: pd.DataFrame) -> bool:
        """
        Validate the loaded data
        
        Args:
            df: DataFrame to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Check required columns
        missing_cols = set(self.required_columns) - set(df.columns)
        if missing_cols:
            logger.error(f"Missing required columns: {missing_cols}")
            logger.info(f"Available columns: {list(df.columns)}")
            return False
        
        # Check for null values
        null_counts = df[self.required_columns].isnull().sum()
        if null_counts.sum() > 0:
            logger.warning(f"Found null values: {null_counts}")
        
        # Check data types and convert to numeric
        numeric_cols = ['open', 'high', 'low', 'close', 'volume']
        for col in numeric_cols:
            if col in df.columns:
                try:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                    # Fill NaN values with reasonable defaults
                    if col == 'volume':
                        df[col] = df[col].fillna(1000)  # Default volume
                    else:
                        # For price columns, forward fill then backward fill
                        df[col] = df[col].ffill().bfill()
                except:
                    logger.error(f"Column {col} cannot be converted to numeric")
                    return False
        
        # Validate OHLC relationships
        if not self._validate_ohlc(df):
            return False
        
        # Check for reasonable values
        if not self._validate_value_ranges(df):
            return False
            
        return True
    
    def _validate_ohlc(self, df: pd.DataFrame) -> bool:
        """
        Validate OHLC relationships
        
        Args:
            df: DataFrame with OHLC data
            
        Returns:
            True if OHLC relationships are valid
        """
        ohlc_cols = ['open', 'high', 'low', 'close']
        
        # Check if all OHLC columns exist
        if not all(col in df.columns for col in ohlc_cols):
            return False
        
        # Validate relationships
        invalid_rows = (
            (df['high'] < df['low']) |
            (df['high'] < df['open']) |
            (df['high'] < df['close']) |
            (df['low'] > df['open']) |
            (df['low'] > df['close'])
        )
        
        if invalid_rows.sum() > 0:
            logger.warning(f"Found {invalid_rows.sum()} rows with invalid OHLC relationships")
            # Remove invalid rows
            df.drop(df[invalid_rows].index, inplace=True)
        
        return True
    
    def _validate_value_ranges(self, df: pd.DataFrame) -> bool:
        """
        Validate that values are within reasonable ranges
        
        Args:
            df: DataFrame to validate
            
        Returns:
            True if values are reasonable
        """
        # Check for negative prices
        price_cols = ['open', 'high', 'low', 'close']
        negative_prices = (df[price_cols] < 0).any(axis=1)
        
        if negative_prices.sum() > 0:
            logger.warning(f"Found {negative_prices.sum()} rows with negative prices")
            df.drop(df[negative_prices].index, inplace=True)
        
        # Check for zero or negative volume
        if 'volume' in df.columns:
            invalid_volume = df['volume'] <= 0
            if invalid_volume.sum() > 0:
                logger.warning(f"Found {invalid_volume.sum()} rows with invalid volume, setting to default")
                df.loc[invalid_volume, 'volume'] = 1000  # Set default volume instead of removing
        
        return True
    
    def _preprocess_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocess the data for analysis
        
        Args:
            df: Raw DataFrame
            
        Returns:
            Preprocessed DataFrame
        """
        # Convert timestamp to datetime
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp')
            df = df.set_index('timestamp')
        
        # Remove duplicates
        df = df.drop_duplicates()
        
        # Ensure data is sorted by timestamp
        df = df.sort_index()
        
        # Add basic features
        df['returns'] = df['close'].pct_change()
        df['log_returns'] = np.log(df['close'] / df['close'].shift(1))
        
        return df
    
    def get_combined_data(self, pattern: str = "*.csv") -> pd.DataFrame:
        """
        Load and combine all CSV files into a single DataFrame
        
        Args:
            pattern: File pattern to match
            
        Returns:
            Combined DataFrame
        """
        data_dict = self.load_csv_files(pattern)
        
        if not data_dict:
            raise ValueError("No valid CSV files found")
        
        # Combine all dataframes
        combined_df = pd.concat(data_dict.values(), ignore_index=False)
        
        # Sort by timestamp and remove duplicates
        combined_df = combined_df.sort_index()
        combined_df = combined_df.drop_duplicates()
        
        logger.info(f"Combined data shape: {combined_df.shape}")
        
        return combined_df