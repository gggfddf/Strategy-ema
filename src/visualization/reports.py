"""
Report generation and visualization module
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from typing import Dict, List
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class ReportGenerator:
    """Generate comprehensive reports and visualizations"""
    
    def __init__(self):
        """Initialize report generator"""
        # Set plotting style
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
    
    def generate_comprehensive_report(self, ranking_report: Dict, output_dir: str):
        """
        Generate comprehensive report with all visualizations
        
        Args:
            ranking_report: Ranking report dictionary
            output_dir: Output directory path
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        logger.info("Generating comprehensive report...")
        
        # Generate different types of reports
        self._generate_overview_charts(ranking_report, output_path)
        self._generate_category_analysis(ranking_report, output_path)
        self._generate_strategy_comparison(ranking_report, output_path)
        self._generate_performance_metrics(ranking_report, output_path)
        
        logger.info(f"Comprehensive report generated in {output_path}")
    
    def _generate_overview_charts(self, ranking_report: Dict, output_path: Path):
        """Generate overview charts"""
        
        # 1. Strategy Distribution by Category
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # Strategy count by category
        categories = list(ranking_report['top_strategies'].keys())
        strategy_counts = [len(strategies) for strategies in ranking_report['top_strategies'].values()]
        
        axes[0, 0].pie(strategy_counts, labels=categories, autopct='%1.1f%%', startangle=90)
        axes[0, 0].set_title('Strategy Distribution by Category')
        
        # Performance comparison
        category_analysis = ranking_report['category_analysis']
        if not category_analysis.empty:
            axes[0, 1].bar(category_analysis['category'], category_analysis['avg_sharpe_ratio'])
            axes[0, 1].set_title('Average Sharpe Ratio by Category')
            axes[0, 1].set_ylabel('Sharpe Ratio')
            axes[0, 1].tick_params(axis='x', rotation=45)
        
        # Win rate comparison
        if not category_analysis.empty:
            axes[1, 0].bar(category_analysis['category'], category_analysis['avg_win_rate'])
            axes[1, 0].set_title('Average Win Rate by Category')
            axes[1, 0].set_ylabel('Win Rate')
            axes[1, 0].tick_params(axis='x', rotation=45)
        
        # Max drawdown comparison
        if not category_analysis.empty:
            axes[1, 1].bar(category_analysis['category'], category_analysis['avg_max_drawdown'])
            axes[1, 1].set_title('Average Max Drawdown by Category')
            axes[1, 1].set_ylabel('Max Drawdown')
            axes[1, 1].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.savefig(output_path / 'overview_charts.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def _generate_category_analysis(self, ranking_report: Dict, output_path: Path):
        """Generate category-specific analysis"""
        
        for category, strategies in ranking_report['top_strategies'].items():
            if not strategies:
                continue
            
            fig, axes = plt.subplots(2, 2, figsize=(15, 12))
            
            # Extract metrics
            sharpe_ratios = [s.metrics['sharpe_ratio'] for s in strategies]
            total_returns = [s.metrics['total_return'] for s in strategies]
            win_rates = [s.metrics['win_rate'] for s in strategies]
            max_drawdowns = [s.metrics['max_drawdown'] for s in strategies]
            strategy_names = [s.strategy_name for s in strategies]
            
            # Top strategies by Sharpe ratio
            axes[0, 0].barh(range(len(strategy_names)), sharpe_ratios)
            axes[0, 0].set_yticks(range(len(strategy_names)))
            axes[0, 0].set_yticklabels(strategy_names, fontsize=8)
            axes[0, 0].set_title(f'{category.upper()} - Sharpe Ratios')
            axes[0, 0].set_xlabel('Sharpe Ratio')
            
            # Total returns
            axes[0, 1].barh(range(len(strategy_names)), total_returns)
            axes[0, 1].set_yticks(range(len(strategy_names)))
            axes[0, 1].set_yticklabels(strategy_names, fontsize=8)
            axes[0, 1].set_title(f'{category.upper()} - Total Returns')
            axes[0, 1].set_xlabel('Total Return')
            
            # Win rates
            axes[1, 0].barh(range(len(strategy_names)), win_rates)
            axes[1, 0].set_yticks(range(len(strategy_names)))
            axes[1, 0].set_yticklabels(strategy_names, fontsize=8)
            axes[1, 0].set_title(f'{category.upper()} - Win Rates')
            axes[1, 0].set_xlabel('Win Rate')
            
            # Max drawdowns
            axes[1, 1].barh(range(len(strategy_names)), max_drawdowns)
            axes[1, 1].set_yticks(range(len(strategy_names)))
            axes[1, 1].set_yticklabels(strategy_names, fontsize=8)
            axes[1, 1].set_title(f'{category.upper()} - Max Drawdowns')
            axes[1, 1].set_xlabel('Max Drawdown')
            
            plt.tight_layout()
            plt.savefig(output_path / f'{category}_analysis.png', dpi=300, bbox_inches='tight')
            plt.close()
    
    def _generate_strategy_comparison(self, ranking_report: Dict, output_path: Path):
        """Generate strategy comparison charts"""
        
        # Create comparison DataFrame
        comparison_data = []
        for category, strategies in ranking_report['top_strategies'].items():
            for strategy in strategies:
                comparison_data.append({
                    'category': category,
                    'strategy_name': strategy.strategy_name,
                    'sharpe_ratio': strategy.metrics['sharpe_ratio'],
                    'total_return': strategy.metrics['total_return'],
                    'win_rate': strategy.metrics['win_rate'],
                    'max_drawdown': strategy.metrics['max_drawdown'],
                    'profit_factor': strategy.metrics['profit_factor'],
                    'num_trades': strategy.metrics['num_trades']
                })
        
        if not comparison_data:
            return
        
        comparison_df = pd.DataFrame(comparison_data)
        
        # Create comparison plots
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        
        # Sharpe ratio by category
        sns.boxplot(data=comparison_df, x='category', y='sharpe_ratio', ax=axes[0, 0])
        axes[0, 0].set_title('Sharpe Ratio Distribution by Category')
        axes[0, 0].tick_params(axis='x', rotation=45)
        
        # Total return by category
        sns.boxplot(data=comparison_df, x='category', y='total_return', ax=axes[0, 1])
        axes[0, 1].set_title('Total Return Distribution by Category')
        axes[0, 1].tick_params(axis='x', rotation=45)
        
        # Win rate by category
        sns.boxplot(data=comparison_df, x='category', y='win_rate', ax=axes[0, 2])
        axes[0, 2].set_title('Win Rate Distribution by Category')
        axes[0, 2].tick_params(axis='x', rotation=45)
        
        # Max drawdown by category
        sns.boxplot(data=comparison_df, x='category', y='max_drawdown', ax=axes[1, 0])
        axes[1, 0].set_title('Max Drawdown Distribution by Category')
        axes[1, 0].tick_params(axis='x', rotation=45)
        
        # Profit factor by category
        sns.boxplot(data=comparison_df, x='category', y='profit_factor', ax=axes[1, 1])
        axes[1, 1].set_title('Profit Factor Distribution by Category')
        axes[1, 1].tick_params(axis='x', rotation=45)
        
        # Number of trades by category
        sns.boxplot(data=comparison_df, x='category', y='num_trades', ax=axes[1, 2])
        axes[1, 2].set_title('Number of Trades by Category')
        axes[1, 2].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.savefig(output_path / 'strategy_comparison.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def _generate_performance_metrics(self, ranking_report: Dict, output_path: Path):
        """Generate performance metrics visualizations"""
        
        # Create performance metrics DataFrame
        metrics_data = []
        for category, strategies in ranking_report['top_strategies'].items():
            for strategy in strategies:
                metrics_data.append({
                    'category': category,
                    'strategy_name': strategy.strategy_name,
                    'sharpe_ratio': strategy.metrics['sharpe_ratio'],
                    'total_return': strategy.metrics['total_return'],
                    'annual_return': strategy.metrics['annual_return'],
                    'win_rate': strategy.metrics['win_rate'],
                    'max_drawdown': strategy.metrics['max_drawdown'],
                    'profit_factor': strategy.metrics['profit_factor'],
                    'volatility': strategy.metrics['volatility'],
                    'num_trades': strategy.metrics['num_trades'],
                    'avg_trade_return': strategy.metrics['avg_trade_return'],
                    'max_consecutive_losses': strategy.metrics['max_consecutive_losses']
                })
        
        if not metrics_data:
            return
        
        metrics_df = pd.DataFrame(metrics_data)
        
        # Create correlation heatmap
        correlation_metrics = ['sharpe_ratio', 'total_return', 'win_rate', 'max_drawdown', 
                             'profit_factor', 'volatility', 'num_trades']
        
        correlation_matrix = metrics_df[correlation_metrics].corr()
        
        plt.figure(figsize=(10, 8))
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0, 
                   square=True, linewidths=0.5)
        plt.title('Performance Metrics Correlation Matrix')
        plt.tight_layout()
        plt.savefig(output_path / 'correlation_matrix.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # Create scatter plots
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # Sharpe vs Return
        axes[0, 0].scatter(metrics_df['total_return'], metrics_df['sharpe_ratio'], 
                           alpha=0.6, s=50)
        axes[0, 0].set_xlabel('Total Return')
        axes[0, 0].set_ylabel('Sharpe Ratio')
        axes[0, 0].set_title('Sharpe Ratio vs Total Return')
        
        # Win Rate vs Profit Factor
        axes[0, 1].scatter(metrics_df['win_rate'], metrics_df['profit_factor'], 
                           alpha=0.6, s=50)
        axes[0, 1].set_xlabel('Win Rate')
        axes[0, 1].set_ylabel('Profit Factor')
        axes[0, 1].set_title('Win Rate vs Profit Factor')
        
        # Max Drawdown vs Sharpe
        axes[1, 0].scatter(metrics_df['max_drawdown'], metrics_df['sharpe_ratio'], 
                           alpha=0.6, s=50)
        axes[1, 0].set_xlabel('Max Drawdown')
        axes[1, 0].set_ylabel('Sharpe Ratio')
        axes[1, 0].set_title('Max Drawdown vs Sharpe Ratio')
        
        # Number of Trades vs Win Rate
        axes[1, 1].scatter(metrics_df['num_trades'], metrics_df['win_rate'], 
                           alpha=0.6, s=50)
        axes[1, 1].set_xlabel('Number of Trades')
        axes[1, 1].set_ylabel('Win Rate')
        axes[1, 1].set_title('Number of Trades vs Win Rate')
        
        plt.tight_layout()
        plt.savefig(output_path / 'performance_scatter_plots.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def generate_interactive_report(self, ranking_report: Dict, output_path: Path):
        """Generate interactive Plotly report"""
        
        # Create interactive dashboard
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=('Strategy Performance by Category', 'Sharpe Ratio Distribution',
                          'Win Rate vs Profit Factor', 'Max Drawdown by Category',
                          'Top Strategies Overview', 'Performance Metrics Correlation'),
            specs=[[{"type": "bar"}, {"type": "box"}],
                   [{"type": "scatter"}, {"type": "bar"}],
                   [{"type": "table"}, {"type": "heatmap"}]]
        )
        
        # Add traces for each subplot
        categories = list(ranking_report['top_strategies'].keys())
        
        # Strategy count by category
        strategy_counts = [len(strategies) for strategies in ranking_report['top_strategies'].values()]
        fig.add_trace(
            go.Bar(x=categories, y=strategy_counts, name="Strategy Count"),
            row=1, col=1
        )
        
        # Sharpe ratio distribution
        sharpe_data = []
        for category, strategies in ranking_report['top_strategies'].items():
            sharpe_values = [s.metrics['sharpe_ratio'] for s in strategies]
            sharpe_data.extend(sharpe_values)
        
        fig.add_trace(
            go.Box(y=sharpe_data, name="Sharpe Ratio"),
            row=1, col=2
        )
        
        # Win rate vs profit factor scatter
        win_rates = []
        profit_factors = []
        for category, strategies in ranking_report['top_strategies'].items():
            for strategy in strategies:
                win_rates.append(strategy.metrics['win_rate'])
                profit_factors.append(strategy.metrics['profit_factor'])
        
        fig.add_trace(
            go.Scatter(x=win_rates, y=profit_factors, mode='markers', name="Win Rate vs Profit Factor"),
            row=2, col=1
        )
        
        # Max drawdown by category
        max_drawdowns = []
        for category, strategies in ranking_report['top_strategies'].items():
            drawdown_values = [s.metrics['max_drawdown'] for s in strategies]
            max_drawdowns.extend(drawdown_values)
        
        fig.add_trace(
            go.Bar(x=categories, y=max_drawdowns, name="Max Drawdown"),
            row=2, col=2
        )
        
        # Update layout
        fig.update_layout(height=1200, showlegend=False, title_text="Trading Strategy Discovery Results")
        
        # Save interactive report
        fig.write_html(output_path / 'interactive_report.html')
        
        logger.info(f"Interactive report generated: {output_path / 'interactive_report.html'}")
    
    def generate_strategy_details_report(self, ranking_report: Dict, output_path: Path):
        """Generate detailed strategy report"""
        
        # Create detailed strategy report
        report_lines = []
        report_lines.append("TRADING STRATEGY DISCOVERY SYSTEM - DETAILED REPORT")
        report_lines.append("=" * 80)
        report_lines.append("")
        
        # Overview
        overview = ranking_report['overview']
        report_lines.append("OVERVIEW")
        report_lines.append(f"Total strategies tested: {overview['total_strategies']}")
        report_lines.append(f"Strategies meeting criteria: {overview['filtered_strategies']}")
        report_lines.append(f"Top strategies selected: {overview['top_strategies_selected']}")
        report_lines.append(f"Categories analyzed: {overview['categories_analyzed']}")
        report_lines.append("")
        
        # Category analysis
        category_analysis = ranking_report['category_analysis']
        if not category_analysis.empty:
            report_lines.append("CATEGORY ANALYSIS")
            report_lines.append("-" * 40)
            for _, row in category_analysis.iterrows():
                report_lines.append(f"Category: {row['category']}")
                report_lines.append(f"  Number of strategies: {row['num_strategies']}")
                report_lines.append(f"  Average Sharpe ratio: {row['avg_sharpe_ratio']:.3f}")
                report_lines.append(f"  Average total return: {row['avg_total_return']:.3f}")
                report_lines.append(f"  Average win rate: {row['avg_win_rate']:.3f}")
                report_lines.append(f"  Best strategy: {row['best_strategy']}")
                report_lines.append("")
        
        # Top strategies by category
        report_lines.append("TOP STRATEGIES BY CATEGORY")
        report_lines.append("=" * 80)
        
        for category, strategies in ranking_report['top_strategies'].items():
            report_lines.append(f"\n{category.upper()}")
            report_lines.append("-" * 40)
            
            for i, strategy in enumerate(strategies):
                metrics = strategy.metrics
                report_lines.append(f"{i+1}. {strategy.strategy_name}")
                report_lines.append(f"   Description: {strategy.get_strategy_description()}")
                report_lines.append(f"   Sharpe Ratio: {metrics['sharpe_ratio']:.3f}")
                report_lines.append(f"   Total Return: {metrics['total_return']:.3f}")
                report_lines.append(f"   Annual Return: {metrics['annual_return']:.3f}")
                report_lines.append(f"   Win Rate: {metrics['win_rate']:.3f}")
                report_lines.append(f"   Max Drawdown: {metrics['max_drawdown']:.3f}")
                report_lines.append(f"   Profit Factor: {metrics['profit_factor']:.3f}")
                report_lines.append(f"   Number of Trades: {metrics['num_trades']}")
                report_lines.append("")
        
        # Write report to file
        with open(output_path / 'detailed_report.txt', 'w') as f:
            f.write('\n'.join(report_lines))
        
        logger.info(f"Detailed report generated: {output_path / 'detailed_report.txt'}")