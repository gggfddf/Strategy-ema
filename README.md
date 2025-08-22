# Trading Strategy Discovery System

A machine learning system that discovers the top 20 most effective trading strategies across 4 defined categories using 1-minute OHLCV candle data.

## Project Overview

This system automatically:
- Loads and validates 1-minute OHLCV CSV data
- Generates all higher timeframes (M2, M3, M5, M10, M15, M30, H1, H2, H4, H6, H8, H12, D, W, M)
- Computes 600 moving averages (200 periods × 3 types: SMA, EMA, WMA) for each timeframe
- Discovers and ranks the top 20 strategies in each of 4 categories
- Provides comprehensive performance metrics and visualizations

## Strategy Categories

1. **Normal MA-Based Strategies** - Single MA logic (price crosses above/below MA)
2. **MA Crossover Strategies** - Fast MA crosses above/below Slow MA
3. **Multi-Timeframe Trend Alignment** - Entry logic with trend confirmation from different timeframes
4. **Mean Reversion Strategies** - Price overextension detection and reversion signals

## Project Structure

```
trading_strategy_discovery/
├── data/
│   ├── raw/                 # Input CSV files
│   └── processed/           # Generated timeframes
├── src/
│   ├── data/
│   │   ├── loader.py       # Data loading and validation
│   │   ├── timeframe_generator.py  # Multi-timeframe generation
│   │   └── feature_engineer.py    # MA calculations and features
│   ├── strategies/
│   │   ├── base.py         # Base strategy class
│   │   ├── ma_single.py    # Single MA strategies
│   │   ├── ma_crossover.py # MA crossover strategies
│   │   ├── multi_tf.py     # Multi-timeframe strategies
│   │   └── mean_reversion.py # Mean reversion strategies
│   ├── evaluation/
│   │   ├── backtester.py   # Strategy backtesting
│   │   ├── metrics.py      # Performance metrics
│   │   └── ranking.py      # Strategy ranking
│   ├── ml/
│   │   ├── model.py        # ML model for strategy optimization
│   │   └── trainer.py      # Model training logic
│   └── visualization/
│       ├── charts.py       # Performance charts
│       └── reports.py      # Strategy reports
├── config/
│   └── settings.py         # Configuration parameters
├── results/
│   ├── strategies/         # Discovered strategies
│   └── reports/           # Performance reports
├── requirements.txt        # Dependencies
├── main.py               # Main execution script
└── README.md            # This file
```

## Installation

```bash
pip install -r requirements.txt
```

## Usage

1. Place your 1-minute OHLCV CSV files in `data/raw/`
2. Run the main script:
   ```bash
   python main.py
   ```
3. View results in `results/` directory

## Output

For each of the 4 strategy categories, the system outputs:
- Top 20 strategies with exact parameters
- Performance metrics (Win rate, Sharpe ratio, Max drawdown, etc.)
- Visual charts and reports
- Human-readable strategy descriptions