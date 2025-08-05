# Quick Start Guide - Trading Strategy Discovery System

## Prerequisites

- Python 3.8 or higher
- 8GB+ RAM recommended
- Sufficient disk space for data and results

## Installation

1. **Clone or download the project files**

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Getting Started

### Option 1: Use Sample Data (Recommended for Testing)

1. **Generate sample data:**
   ```bash
   python generate_sample_data.py
   ```
   This creates three sample datasets in `data/raw/`:
   - `trending_market.csv` - Upward trending market
   - `volatile_market.csv` - High volatility market
   - `sideways_market.csv` - Sideways market

2. **Run the system:**
   ```bash
   python main.py
   ```

### Option 2: Use Your Own Data

1. **Prepare your data:**
   - Format: 1-minute OHLCV CSV files
   - Required columns: `timestamp`, `open`, `high`, `low`, `close`, `volume`
   - Place files in `data/raw/` directory

2. **Run the system:**
   ```bash
   python main.py
   ```

## Expected Output

The system will:

1. **Load and validate your data**
2. **Generate all timeframes** (M2, M3, M5, M10, M15, M30, H1, H2, H4, H6, H8, H12, D, W, M)
3. **Compute 600 moving averages** for each timeframe
4. **Generate and test strategies** across 4 categories:
   - Normal MA-Based Strategies
   - MA Crossover Strategies
   - Multi-Timeframe Trend Alignment
   - Mean Reversion Strategies
5. **Rank and select top 20 strategies** per category
6. **Generate comprehensive reports** and visualizations

## Results

Check the `results/` directory for:

- **`top_strategies.csv`** - Summary of all top strategies
- **`category_analysis.csv`** - Performance analysis by category
- **`detailed_report.txt`** - Comprehensive text report
- **`results/reports/`** - Charts and visualizations
- **Category-specific files** - Detailed results for each category

## Sample Output

```
TRADING STRATEGY DISCOVERY SYSTEM - RESULTS SUMMARY
================================================================================

Overview:
  Total strategies tested: 1,200
  Strategies meeting criteria: 156
  Top strategies selected: 80
  Categories analyzed: 4

Top Strategies by Category:

  NORMAL_MA:
    1. Single_EMA_20_M5_crossover
       Description: Buy when price crosses above EMA20 on M5, Sell when price crosses below EMA20 on M5
       Sharpe Ratio: 1.245
       Total Return: 0.156
       Win Rate: 0.623
       Max Drawdown: -0.089

  MA_CROSSOVER:
    1. Crossover_EMA_12_SMA_26_M15
       Description: Buy: EMA12 crosses above SMA26 on M15, Sell: EMA12 crosses below SMA26 on M15
       Sharpe Ratio: 1.187
       Total Return: 0.134
       Win Rate: 0.598
       Max Drawdown: -0.092

Results exported to: results/
================================================================================
```

## Configuration

Edit `config/settings.py` to customize:

- **MA periods**: Currently 1-200 (can be reduced for faster processing)
- **Timeframes**: All 16 timeframes included
- **Performance thresholds**: Minimum win rate, Sharpe ratio, etc.
- **Backtesting parameters**: Initial capital, commission rates

## Troubleshooting

### Common Issues

1. **"No CSV files found"**
   - Ensure your CSV files are in `data/raw/` directory
   - Check file format (timestamp, open, high, low, close, volume)

2. **Memory errors**
   - Reduce MA periods in `config/settings.py`
   - Use smaller datasets for testing

3. **Processing time too long**
   - Reduce MA periods range
   - Use fewer timeframes
   - Reduce strategy generation parameters

### Performance Tips

- **For testing**: Use sample data with reduced MA periods
- **For production**: Use full MA range (1-200) with complete datasets
- **For large datasets**: Ensure sufficient RAM (16GB+ recommended)

## Next Steps

1. **Review results** in `results/` directory
2. **Analyze top strategies** for your specific needs
3. **Customize parameters** in `config/settings.py`
4. **Extend functionality** by adding new strategy types

## Support

- Check logs in `trading_strategy_discovery.log`
- Review `PROJECT_PLAN.md` for detailed implementation
- Examine source code in `src/` directory for customization

## System Capabilities

✅ **Data Handling**: Load, validate, and process 1-minute OHLCV data
✅ **Timeframe Generation**: Create all higher timeframes from M1 base
✅ **Feature Engineering**: Compute 600 MAs and advanced features
✅ **Strategy Discovery**: 4 categories with parameter optimization
✅ **Backtesting**: Realistic testing with transaction costs
✅ **Performance Analysis**: Comprehensive metrics and ranking
✅ **Reporting**: Visualizations and detailed reports

The system is production-ready and designed for extensibility!