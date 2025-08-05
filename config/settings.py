"""
Configuration settings for the Trading Strategy Discovery System
"""

import os
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_RAW_DIR = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
RESULTS_DIR = PROJECT_ROOT / "results"

# Data settings
TIMEFRAMES = {
    'M1': '1T',
    'M2': '2T', 
    'M3': '3T',
    'M5': '5T',
    'M10': '10T',
    'M15': '15T',
    'M30': '30T',
    'H1': '1H',
    'H2': '2H',
    'H4': '4H',
    'H6': '6H',
    'H8': '8H',
    'H12': '12H',
    'D': '1D',
    'W': '1W',
    'M': '1M'
}

# Moving Average settings
MA_PERIODS = list(range(1, 201))  # 1 to 200
MA_TYPES = ['SMA', 'EMA', 'WMA']

# Strategy parameters
STRATEGY_CATEGORIES = [
    'normal_ma',      # Single MA strategies
    'ma_crossover',   # MA crossover strategies
    'multi_timeframe', # Multi-timeframe strategies
    'mean_reversion'  # Mean reversion strategies
]

# Backtesting settings
INITIAL_CAPITAL = 100000
COMMISSION_RATE = 0.001  # 0.1%
SLIPPAGE = 0.0001  # 0.01%

# Performance thresholds
MIN_WIN_RATE = 0.4  # 40% win rate (reduced from 0.5)
MIN_PROFIT_FACTOR = 1.0  # Break-even (reduced from 1.2)
MAX_DRAWDOWN = 0.3  # 30% max drawdown (increased from 0.2)
MIN_SHARPE_RATIO = 0.0  # Any positive Sharpe ratio (reduced from 0.5)

# Mean reversion settings
DISTANCE_THRESHOLDS = [0.01, 0.02, 0.03, 0.05, 0.08, 0.10, 0.15, 0.20]  # 1% to 20%

# Multi-timeframe settings
TREND_CONFIRMATION_PERIODS = [5, 10, 20, 50, 100, 200]

# ML settings
RANDOM_STATE = 42
TEST_SIZE = 0.2
CV_FOLDS = 5

# Output settings
TOP_STRATEGIES_PER_CATEGORY = 20
SAVE_INTERMEDIATE_RESULTS = True