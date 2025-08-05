"""
Sample data generator for testing the Trading Strategy Discovery System
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging
from config.settings import DATA_RAW_DIR

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_sample_ohlcv_data(start_date: str = '2023-01-01', 
                              end_date: str = '2023-12-31',
                              base_price: float = 100.0,
                              volatility: float = 0.02) -> pd.DataFrame:
    """
    Generate sample 1-minute OHLCV data
    
    Args:
        start_date: Start date for data generation
        end_date: End date for data generation
        base_price: Base price for the asset
        volatility: Price volatility
        
    Returns:
        DataFrame with OHLCV data
    """
    logger.info("Generating sample OHLCV data...")
    
    # Create datetime range for 1-minute intervals
    date_range = pd.date_range(start=start_date, end=end_date, freq='1T')
    
    # Generate price data with random walk
    np.random.seed(42)  # For reproducible results
    
    # Generate log returns
    log_returns = np.random.normal(0, volatility, len(date_range))
    
    # Add some trend and mean reversion
    trend = np.linspace(0, 0.1, len(date_range))  # 10% upward trend
    mean_reversion = -0.0001 * np.arange(len(date_range))  # Slight mean reversion
    
    log_returns += trend + mean_reversion
    
    # Calculate prices
    prices = base_price * np.exp(np.cumsum(log_returns))
    
    # Generate OHLCV data
    data = []
    
    for i, (timestamp, close_price) in enumerate(zip(date_range, prices)):
        # Generate OHLC from close price with some randomness
        high_noise = np.random.uniform(0.001, 0.005)
        low_noise = np.random.uniform(0.001, 0.005)
        
        high = close_price * (1 + high_noise)
        low = close_price * (1 - low_noise)
        open_price = prices[i-1] if i > 0 else close_price
        
        # Generate volume (higher during price movements)
        price_change = abs(close_price - open_price) / open_price
        base_volume = np.random.uniform(1000, 5000)
        volume = base_volume * (1 + price_change * 10)
        
        data.append({
            'timestamp': timestamp,
            'open': open_price,
            'high': high,
            'low': low,
            'close': close_price,
            'volume': volume
        })
    
    df = pd.DataFrame(data)
    df = df.set_index('timestamp')
    
    logger.info(f"Generated {len(df)} rows of sample data")
    logger.info(f"Price range: ${df['low'].min():.2f} - ${df['high'].max():.2f}")
    logger.info(f"Date range: {df.index.min()} to {df.index.max()}")
    
    return df

def generate_multiple_samples():
    """Generate multiple sample datasets for testing"""
    
    # Ensure data directory exists
    DATA_RAW_DIR.mkdir(parents=True, exist_ok=True)
    
    # Generate different types of market data
    samples = [
        {
            'name': 'trending_market',
            'start_date': '2023-01-01',
            'end_date': '2023-12-31',
            'base_price': 100.0,
            'volatility': 0.015,
            'trend': 0.2  # 20% upward trend
        },
        {
            'name': 'volatile_market',
            'start_date': '2023-01-01',
            'end_date': '2023-12-31',
            'base_price': 50.0,
            'volatility': 0.03,
            'trend': 0.0  # No trend
        },
        {
            'name': 'sideways_market',
            'start_date': '2023-01-01',
            'end_date': '2023-12-31',
            'base_price': 75.0,
            'volatility': 0.01,
            'trend': 0.0  # No trend
        }
    ]
    
    for sample in samples:
        logger.info(f"Generating {sample['name']} sample data...")
        
        # Generate data with specific characteristics
        df = generate_sample_ohlcv_data(
            start_date=sample['start_date'],
            end_date=sample['end_date'],
            base_price=sample['base_price'],
            volatility=sample['volatility']
        )
        
        # Add trend if specified
        if sample['trend'] > 0:
            trend_factor = np.linspace(1, 1 + sample['trend'], len(df))
            df['close'] *= trend_factor
            df['high'] *= trend_factor
            df['low'] *= trend_factor
            df['open'] *= trend_factor
        
        # Save to CSV
        output_file = DATA_RAW_DIR / f"{sample['name']}.csv"
        df.reset_index().to_csv(output_file, index=False)
        
        logger.info(f"Saved {sample['name']} data to {output_file}")
    
    logger.info("Sample data generation completed!")
    logger.info(f"Sample files created in {DATA_RAW_DIR}:")
    for file in DATA_RAW_DIR.glob("*.csv"):
        logger.info(f"  - {file.name}")

def main():
    """Main function to generate sample data"""
    try:
        generate_multiple_samples()
        print("\nSample data generation completed successfully!")
        print("You can now run the main trading strategy discovery system:")
        print("python main.py")
        
    except Exception as e:
        logger.error(f"Error generating sample data: {e}")
        raise

if __name__ == "__main__":
    main()