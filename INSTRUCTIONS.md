# Instructions for Running Trading Strategy Discovery System

## Step 1: Prepare Your Data File

Make sure your XAUUSD data file is in the current directory. The system will look for files named:
- `xauusd data.csv`
- `xauusd_data.csv`
- `xauusddata.csv`
- `data.csv`
- `XAUUSD.csv`
- `gold.csv`

## Step 2: Run the System

### Option A: Automatic Setup and Run
```bash
python run_with_xauusd.py
```

This will:
1. Find your data file
2. Prepare it for processing
3. Install dependencies if needed
4. Run the complete trading strategy discovery system
5. Save all results in Excel format

### Option B: Manual Steps
```bash
# 1. Prepare data
python upload_data.py

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the system
python main.py
```

## Step 3: View Results

After the system completes, you'll find:

### Excel Files:
- **`results/trading_strategy_results.xlsx`** - Complete results with multiple sheets
- **`results/top_20_strategies.xlsx`** - Top 20 strategies summary

### Excel File Contents:
1. **Overview Sheet** - Summary of all top strategies
2. **Top_Strategies Sheet** - Detailed strategy information
3. **Category_Analysis Sheet** - Performance by category
4. **Category-specific Sheets** - Detailed results for each category

### Strategy Information in Excel:
- Strategy name and description
- Sharpe Ratio
- Total Return and Annual Return
- Win Rate
- Max Drawdown
- Profit Factor
- Number of Trades
- Volatility
- Average Trade Return
- Max Consecutive Losses

## Expected Output

The system will discover the **TOP 20 STRATEGIES** across 4 categories:

1. **Normal MA-Based Strategies** (5 strategies)
   - Buy when price crosses above MA, Sell when price crosses below MA

2. **MA Crossover Strategies** (5 strategies)
   - Buy when fast MA crosses above slow MA, Sell when fast MA crosses below slow MA

3. **Multi-Timeframe Trend Alignment** (5 strategies)
   - Entry logic on one timeframe with trend confirmation from another timeframe

4. **Mean Reversion Strategies** (5 strategies)
   - Buy when price is overextended below MA, Sell when price is overextended above MA

## Processing Time

- **Small dataset** (< 1 year): 5-15 minutes
- **Medium dataset** (1-2 years): 15-30 minutes
- **Large dataset** (> 2 years): 30-60 minutes

## Troubleshooting

### If you get "No data file found":
1. Make sure your CSV file is in the current directory
2. Check the file name matches one of the expected names
3. Ensure the file has OHLCV data (timestamp, open, high, low, close, volume)

### If you get memory errors:
1. The system will automatically reduce parameters for smaller datasets
2. For very large datasets, consider using a subset of your data

### If you get dependency errors:
1. Run: `pip install -r requirements.txt`
2. Make sure you have Python 3.8 or higher

## Data Format Requirements

Your CSV file should have these columns:
- `timestamp` (or `date`, `time`, `datetime`)
- `open`
- `high`
- `low`
- `close`
- `volume` (or `vol`, `v`)

The system will automatically standardize column names if needed.

## Results Summary

After completion, you'll see:
- Total strategies tested
- Number of strategies meeting criteria
- Top 20 strategies with performance metrics
- Excel files with detailed results
- Charts and visualizations

All results will be saved in Excel format for easy analysis!