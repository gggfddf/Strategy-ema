"""
Run Trading Strategy Discovery System with XAUUSD data
"""

import os
import sys
from pathlib import Path
import subprocess

def main():
    """Run the system with XAUUSD data"""
    
    print("="*80)
    print("TRADING STRATEGY DISCOVERY SYSTEM - XAUUSD ANALYSIS")
    print("="*80)
    
    # Step 1: Check if data file exists
    data_file = None
    possible_files = [
        "xauusd data.csv",
        "xauusd_data.csv", 
        "xauusddata.csv",
        "data.csv",
        "XAUUSD.csv",
        "gold.csv"
    ]
    
    for file in possible_files:
        if os.path.exists(file):
            data_file = file
            break
    
    if not data_file:
        print("❌ No XAUUSD data file found!")
        print("\nPlease ensure your data file is in the current directory.")
        print("Expected file names:")
        for file in possible_files:
            print(f"  - {file}")
        print("\nOr run: python upload_data.py")
        return False
    
    print(f"✅ Found data file: {data_file}")
    
    # Step 2: Prepare data
    print("\n📁 Preparing data file...")
    try:
        result = subprocess.run([sys.executable, "upload_data.py"], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ Data preparation failed!")
            print(result.stderr)
            return False
        print("✅ Data preparation completed!")
    except Exception as e:
        print(f"❌ Error preparing data: {e}")
        return False
    
    # Step 3: Install dependencies if needed
    print("\n📦 Checking dependencies...")
    try:
        import pandas
        import numpy
        import matplotlib
        import seaborn
        import plotly
        import openpyxl
        print("✅ All dependencies are installed!")
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Installing dependencies...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed!")
    
    # Step 4: Run the main system
    print("\n🚀 Starting Trading Strategy Discovery System...")
    print("This will:")
    print("1. Load your XAUUSD data")
    print("2. Generate all timeframes (M2, M3, M5, M10, M15, M30, H1, H2, H4, H6, H8, H12, D, W, M)")
    print("3. Compute 600 moving averages for each timeframe")
    print("4. Discover top 20 strategies in each category")
    print("5. Save all results in Excel format")
    print("\nProcessing... (this may take several minutes)")
    
    try:
        result = subprocess.run([sys.executable, "main.py"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("\n" + "="*80)
            print("✅ TRADING STRATEGY DISCOVERY COMPLETED!")
            print("="*80)
            print("\n📊 RESULTS SAVED TO EXCEL:")
            print("  - results/trading_strategy_results.xlsx (Complete results)")
            print("  - results/top_20_strategies.xlsx (Top 20 strategies)")
            print("  - results/ (Charts and reports)")
            print("\n🎯 TOP 20 STRATEGIES FOUND:")
            print("  - 5 Normal MA-Based Strategies")
            print("  - 5 MA Crossover Strategies") 
            print("  - 5 Multi-Timeframe Trend Alignment Strategies")
            print("  - 5 Mean Reversion Strategies")
            print("\n📈 Each strategy includes:")
            print("  - Sharpe Ratio")
            print("  - Total Return")
            print("  - Win Rate")
            print("  - Max Drawdown")
            print("  - Profit Factor")
            print("  - Number of Trades")
            print("\nCheck the Excel files for detailed results!")
            
        else:
            print("❌ System execution failed!")
            print("Error output:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error running system: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ System failed to complete. Please check the error messages above.")
        sys.exit(1)
    else:
        print("\n🎉 System completed successfully!")