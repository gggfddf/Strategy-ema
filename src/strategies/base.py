"""
Base strategy class for all trading strategies
"""

import pandas as pd
import numpy as np
from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Optional
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class StrategyResult:
    """Container for strategy backtest results"""
    strategy_name: str
    parameters: Dict
    signals: pd.Series
    returns: pd.Series
    positions: pd.Series
    equity_curve: pd.Series
    trades: pd.DataFrame
    metrics: Dict

class BaseStrategy(ABC):
    """Base class for all trading strategies"""
    
    def __init__(self, name: str, category: str):
        self.name = name
        self.category = category
        self.parameters = {}
        self.signals = None
        self.returns = None
        self.positions = None
        self.equity_curve = None
        self.trades = None
        self.metrics = {}
    
    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """
        Generate trading signals
        
        Args:
            data: OHLCV DataFrame with features
            
        Returns:
            Series with signals (1 for buy, -1 for sell, 0 for hold)
        """
        pass
    
    @abstractmethod
    def get_strategy_description(self) -> str:
        """
        Get human-readable description of the strategy
        
        Returns:
            Strategy description string
        """
        pass
    
    def backtest(self, data: pd.DataFrame, initial_capital: float = 100000,
                 commission_rate: float = 0.001, slippage: float = 0.0001) -> StrategyResult:
        """
        Backtest the strategy
        
        Args:
            data: OHLCV DataFrame with features
            initial_capital: Initial capital
            commission_rate: Commission rate per trade
            slippage: Slippage per trade
            
        Returns:
            StrategyResult object
        """
        # Generate signals
        signals = self.generate_signals(data)
        
        # Calculate positions
        positions = self._calculate_positions(signals)
        
        # Calculate returns
        returns = self._calculate_returns(data, positions, commission_rate, slippage)
        
        # Calculate equity curve
        equity_curve = self._calculate_equity_curve(returns, initial_capital)
        
        # Generate trades
        trades = self._generate_trades(data, positions, signals)
        
        # Calculate metrics
        metrics = self._calculate_metrics(returns, equity_curve, trades)
        
        # Create result object
        result = StrategyResult(
            strategy_name=self.name,
            parameters=self.parameters,
            signals=signals,
            returns=returns,
            positions=positions,
            equity_curve=equity_curve,
            trades=trades,
            metrics=metrics
        )
        
        return result
    
    def _calculate_positions(self, signals: pd.Series) -> pd.Series:
        """
        Calculate position sizes from signals
        
        Args:
            signals: Trading signals
            
        Returns:
            Position sizes
        """
        positions = signals.copy()
        positions = positions.fillna(0)
        
        # Ensure positions are -1, 0, or 1
        positions = positions.clip(-1, 1)
        
        return positions
    
    def _calculate_returns(self, data: pd.DataFrame, positions: pd.Series,
                          commission_rate: float, slippage: float) -> pd.Series:
        """
        Calculate strategy returns
        
        Args:
            data: OHLCV DataFrame
            positions: Position sizes
            commission_rate: Commission rate
            slippage: Slippage rate
            
        Returns:
            Strategy returns
        """
        # Calculate price returns
        price_returns = data['close'].pct_change()
        
        # Calculate strategy returns
        strategy_returns = positions.shift(1) * price_returns
        
        # Calculate transaction costs
        position_changes = positions.diff().abs()
        transaction_costs = position_changes * (commission_rate + slippage)
        
        # Net returns
        net_returns = strategy_returns - transaction_costs
        
        return net_returns
    
    def _calculate_equity_curve(self, returns: pd.Series, initial_capital: float) -> pd.Series:
        """
        Calculate equity curve
        
        Args:
            returns: Strategy returns
            initial_capital: Initial capital
            
        Returns:
            Equity curve
        """
        cumulative_returns = (1 + returns).cumprod()
        equity_curve = initial_capital * cumulative_returns
        return equity_curve
    
    def _generate_trades(self, data: pd.DataFrame, positions: pd.Series, signals: pd.Series) -> pd.DataFrame:
        """
        Generate trade DataFrame
        
        Args:
            data: OHLCV DataFrame
            positions: Position sizes
            signals: Trading signals
            
        Returns:
            DataFrame with trade information
        """
        # Find entry and exit points
        position_changes = positions.diff()
        
        # Entry points (position changes from 0 to 1 or -1)
        entries = position_changes != 0
        
        # Exit points (position changes from 1 or -1 to 0)
        exits = (positions.shift(1) != 0) & (positions == 0)
        
        # Combine entry and exit points
        trade_points = entries | exits
        
        if not trade_points.any():
            return pd.DataFrame()
        
        # Create trades DataFrame
        trades = pd.DataFrame({
            'timestamp': data.index[trade_points],
            'price': data.loc[trade_points, 'close'],
            'position': positions[trade_points],
            'signal': signals[trade_points],
            'volume': data.loc[trade_points, 'volume']
        })
        
        # Add trade direction
        trades['direction'] = trades['position'].map({1: 'BUY', -1: 'SELL', 0: 'CLOSE'})
        
        return trades
    
    def _calculate_metrics(self, returns: pd.Series, equity_curve: pd.Series, trades: pd.DataFrame) -> Dict:
        """
        Calculate performance metrics
        
        Args:
            returns: Strategy returns
            equity_curve: Equity curve
            trades: Trades DataFrame
            
        Returns:
            Dictionary of performance metrics
        """
        metrics = {}
        
        # Basic return metrics
        total_return = (equity_curve.iloc[-1] / equity_curve.iloc[0]) - 1
        annual_return = total_return * (252 / len(returns))
        
        metrics['total_return'] = total_return
        metrics['annual_return'] = annual_return
        metrics['avg_return'] = returns.mean()
        metrics['return_std'] = returns.std()
        
        # Risk metrics
        metrics['sharpe_ratio'] = self._calculate_sharpe_ratio(returns)
        metrics['max_drawdown'] = self._calculate_max_drawdown(equity_curve)
        metrics['volatility'] = returns.std() * np.sqrt(252)
        
        # Trade metrics
        if not trades.empty:
            metrics['num_trades'] = len(trades[trades['position'] != 0])
            metrics['win_rate'] = self._calculate_win_rate(trades)
            metrics['profit_factor'] = self._calculate_profit_factor(trades)
            metrics['avg_trade_return'] = self._calculate_avg_trade_return(trades)
            metrics['max_consecutive_losses'] = self._calculate_max_consecutive_losses(trades)
        else:
            metrics['num_trades'] = 0
            metrics['win_rate'] = 0
            metrics['profit_factor'] = 0
            metrics['avg_trade_return'] = 0
            metrics['max_consecutive_losses'] = 0
        
        return metrics
    
    def _calculate_sharpe_ratio(self, returns: pd.Series, risk_free_rate: float = 0.02) -> float:
        """Calculate Sharpe ratio"""
        excess_returns = returns - risk_free_rate / 252
        if returns.std() == 0:
            return 0
        return excess_returns.mean() / returns.std() * np.sqrt(252)
    
    def _calculate_max_drawdown(self, equity_curve: pd.Series) -> float:
        """Calculate maximum drawdown"""
        rolling_max = equity_curve.expanding().max()
        drawdown = (equity_curve - rolling_max) / rolling_max
        return drawdown.min()
    
    def _calculate_win_rate(self, trades: pd.DataFrame) -> float:
        """Calculate win rate"""
        if len(trades) == 0:
            return 0
        
        # Calculate trade returns
        trade_returns = trades['price'].pct_change()
        winning_trades = trade_returns > 0
        
        return winning_trades.mean()
    
    def _calculate_profit_factor(self, trades: pd.DataFrame) -> float:
        """Calculate profit factor"""
        if len(trades) == 0:
            return 0
        
        # Calculate trade returns
        trade_returns = trades['price'].pct_change()
        
        gross_profit = trade_returns[trade_returns > 0].sum()
        gross_loss = abs(trade_returns[trade_returns < 0].sum())
        
        if gross_loss == 0:
            return float('inf') if gross_profit > 0 else 0
        
        return gross_profit / gross_loss
    
    def _calculate_avg_trade_return(self, trades: pd.DataFrame) -> float:
        """Calculate average trade return"""
        if len(trades) == 0:
            return 0
        
        trade_returns = trades['price'].pct_change()
        return trade_returns.mean()
    
    def _calculate_max_consecutive_losses(self, trades: pd.DataFrame) -> int:
        """Calculate maximum consecutive losses"""
        if len(trades) == 0:
            return 0
        
        trade_returns = trades['price'].pct_change()
        losing_trades = trade_returns < 0
        
        max_consecutive = 0
        current_consecutive = 0
        
        for is_loss in losing_trades:
            if is_loss:
                current_consecutive += 1
                max_consecutive = max(max_consecutive, current_consecutive)
            else:
                current_consecutive = 0
        
        return max_consecutive