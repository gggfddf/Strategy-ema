#!/usr/bin/env python3
"""
Test script to verify all fixes work correctly
"""

import sys
import os
import logging
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from data.loader import DataLoader
from data.timeframe_generator import TimeframeGenerator
from data.feature_engineer import FeatureEngineer
from config.settings import DATA_RAW_DIR

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_data_loading():
    """Test data loading functionality"""
    print("="*60)
    print("TESTING DATA LOADING")
    print("="*60)
    
    try:
        loader = DataLoader()
        data = loader.get_combined_data()
        print(f"✅ Data loaded successfully: {data.shape}")
        print(f"   Date range: {data.index.min()} to {data.index.max()}")
        print(f"   Columns: {list(data.columns)}")
        return data
    except Exception as e:
        print(f"❌ Data loading failed: {e}")
        return None

def test_timeframe_generation(data):
    """Test timeframe generation"""
    print("\n" + "="*60)
    print("TESTING TIMEFRAME GENERATION")
    print("="*60)
    
    try:
        generator = TimeframeGenerator()
        timeframe_data = generator.generate_all_timeframes(data)
        
        print(f"✅ Timeframes generated successfully")
        for tf_name, df in timeframe_data.items():
            print(f"   {tf_name}: {df.shape}")
        
        return timeframe_data
    except Exception as e:
        print(f"❌ Timeframe generation failed: {e}")
        return None

def test_feature_engineering(timeframe_data):
    """Test feature engineering"""
    print("\n" + "="*60)
    print("TESTING FEATURE ENGINEERING")
    print("="*60)
    
    try:
        engineer = FeatureEngineer()
        
        # Test MA computation
        enhanced_data = engineer.compute_all_moving_averages(timeframe_data)
        print(f"✅ MA computation completed")
        
        # Test crossover features
        for tf_name, df in enhanced_data.items():
            enhanced_data[tf_name] = engineer.generate_crossover_features(df)
        print(f"✅ Crossover features generated")
        
        # Test mean reversion features
        for tf_name, df in enhanced_data.items():
            enhanced_data[tf_name] = engineer.generate_mean_reversion_features(df)
        print(f"✅ Mean reversion features generated")
        
        # Test multi-timeframe features
        enhanced_data = engineer.generate_multi_timeframe_features(enhanced_data)
        print(f"✅ Multi-timeframe features generated")
        
        # Get feature summary
        summary = engineer.get_feature_summary(enhanced_data)
        print(f"✅ Feature summary generated:")
        print(summary.to_string())
        
        return enhanced_data
    except Exception as e:
        print(f"❌ Feature engineering failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Run all tests"""
    print("TRADING STRATEGY SYSTEM - FIX VERIFICATION")
    print("="*60)
    
    # Test 1: Data Loading
    data = test_data_loading()
    if data is None:
        print("❌ Cannot proceed without data")
        return False
    
    # Test 2: Timeframe Generation
    timeframe_data = test_timeframe_generation(data)
    if timeframe_data is None:
        print("❌ Cannot proceed without timeframes")
        return False
    
    # Test 3: Feature Engineering
    enhanced_data = test_feature_engineering(timeframe_data)
    if enhanced_data is None:
        print("❌ Feature engineering failed")
        return False
    
    print("\n" + "="*60)
    print("✅ ALL TESTS PASSED!")
    print("="*60)
    print("The system is now ready for strategy generation and backtesting.")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)