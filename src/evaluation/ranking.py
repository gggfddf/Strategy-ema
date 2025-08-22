"""
Strategy ranking and selection module
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from ..strategies.base import StrategyResult
from config.settings import TOP_STRATEGIES_PER_CATEGORY, MIN_WIN_RATE, MIN_PROFIT_FACTOR, MAX_DRAWDOWN, MIN_SHARPE_RATIO
import logging

logger = logging.getLogger(__name__)

class StrategyRanker:
    """Strategy ranking and selection engine"""
    
    def __init__(self, top_n: int = TOP_STRATEGIES_PER_CATEGORY,
                 min_win_rate: float = MIN_WIN_RATE,
                 min_profit_factor: float = MIN_PROFIT_FACTOR,
                 max_drawdown: float = MAX_DRAWDOWN,
                 min_sharpe_ratio: float = MIN_SHARPE_RATIO):
        """
        Initialize strategy ranker
        
        Args:
            top_n: Number of top strategies to select per category
            min_win_rate: Minimum win rate threshold
            min_profit_factor: Minimum profit factor threshold
            max_drawdown: Maximum drawdown threshold
            min_sharpe_ratio: Minimum Sharpe ratio threshold
        """
        self.top_n = top_n
        self.min_win_rate = min_win_rate
        self.min_profit_factor = min_profit_factor
        self.max_drawdown = max_drawdown
        self.min_sharpe_ratio = min_sharpe_ratio
    
    def filter_strategies(self, results: List[StrategyResult]) -> List[StrategyResult]:
        """Filter strategies based on performance criteria - NO FILTERING - Show ALL"""
        # NO FILTERING AT ALL - Return all results
        print(f"✅ NO FILTERING: Returning all {len(results)} results")
        return results
    
    def rank_strategies_by_category(self, results: List[StrategyResult]) -> Dict[str, List[StrategyResult]]:
        """
        Rank strategies by category
        
        Args:
            results: List of StrategyResult objects
            
        Returns:
            Dictionary mapping category to ranked strategies
        """
        # Group results by category
        categories = {}
        for result in results:
            category = result.parameters.get('category', 'unknown')
            if category not in categories:
                categories[category] = []
            categories[category].append(result)
        
        # Rank strategies within each category
        ranked_categories = {}
        
        for category, category_results in categories.items():
            # Sort by composite score
            ranked_strategies = self._rank_by_composite_score(category_results)
            ranked_categories[category] = ranked_strategies
        
        return ranked_categories
    
    def _rank_by_composite_score(self, results: List[StrategyResult]) -> List[StrategyResult]:
        """
        Rank strategies by composite score
        
        Args:
            results: List of StrategyResult objects
            
        Returns:
            List of ranked StrategyResult objects
        """
        # Calculate composite scores
        for result in results:
            metrics = result.metrics
            
            # Get metrics with safe defaults
            sharpe_ratio = metrics.get('sharpe_ratio', 0)
            total_return = metrics.get('total_return', 0)
            win_rate = metrics.get('win_rate', 0)
            max_drawdown = metrics.get('max_drawdown', 0)
            
            # Handle NaN values
            if pd.isna(sharpe_ratio): sharpe_ratio = 0
            if pd.isna(total_return): total_return = 0
            if pd.isna(win_rate): win_rate = 0
            if pd.isna(max_drawdown): max_drawdown = 0
            
            # Composite score calculation
            composite_score = (
                sharpe_ratio * 0.4 +
                total_return * 0.3 +
                win_rate * 0.2 +
                (1 - abs(max_drawdown)) * 0.1
            )
            
            # Store composite score in result
            result.metrics['composite_score'] = composite_score
        
        # Sort by composite score
        ranked_results = sorted(results, key=lambda x: x.metrics.get('composite_score', 0), reverse=True)
        
        return ranked_results
    
    def select_top_strategies(self, results: List[StrategyResult]) -> Dict[str, List[StrategyResult]]:
        """
        Select top strategies for each category
        
        Args:
            results: List of StrategyResult objects
            
        Returns:
            Dictionary mapping category to top strategies
        """
        # Filter strategies
        filtered_results = self.filter_strategies(results)
        
        # Rank by category
        ranked_categories = self.rank_strategies_by_category(filtered_results)
        
        # Select top N strategies per category
        top_strategies = {}
        
        for category, ranked_strategies in ranked_categories.items():
            top_strategies[category] = ranked_strategies[:self.top_n]
            logger.info(f"Selected {len(top_strategies[category])} top strategies for category: {category}")
        
        return top_strategies
    
    def get_strategy_summary(self, top_strategies: Dict[str, List[StrategyResult]]) -> pd.DataFrame:
        """
        Generate summary of top strategies
        
        Args:
            top_strategies: Dictionary mapping category to top strategies
            
        Returns:
            DataFrame with strategy summary
        """
        summary_data = []
        
        for category, strategies in top_strategies.items():
            for i, strategy in enumerate(strategies):
                summary_data.append({
                    'rank': i + 1,
                    'category': category,
                    'strategy_name': strategy.strategy_name,
                    'description': strategy.get_strategy_description(),
                    'total_return': strategy.metrics.get('total_return', 0),
                    'annual_return': strategy.metrics.get('annual_return', 0),
                    'sharpe_ratio': strategy.metrics.get('sharpe_ratio', 0),
                    'max_drawdown': strategy.metrics.get('max_drawdown', 0),
                    'win_rate': strategy.metrics.get('win_rate', 0),
                    'profit_factor': strategy.metrics.get('profit_factor', 0),
                    'num_trades': strategy.metrics.get('num_trades', 0),
                    'composite_score': strategy.metrics.get('composite_score', 0),
                    'parameters': strategy.parameters
                })
        
        return pd.DataFrame(summary_data)
    
    def analyze_category_performance(self, results: List[StrategyResult]) -> pd.DataFrame:
        """
        Analyze performance by strategy category
        
        Args:
            results: List of StrategyResult objects
            
        Returns:
            DataFrame with category performance analysis
        """
        # Group by category
        categories = {}
        for result in results:
            category = result.parameters.get('category', 'unknown')
            if category not in categories:
                categories[category] = []
            categories[category].append(result)
        
        # Calculate category statistics
        category_stats = []
        
        for category, category_results in categories.items():
            if not category_results:
                continue
            
            # Calculate statistics
            total_returns = [r.metrics['total_return'] for r in category_results]
            sharpe_ratios = [r.metrics['sharpe_ratio'] for r in category_results]
            win_rates = [r.metrics['win_rate'] for r in category_results]
            max_drawdowns = [r.metrics['max_drawdown'] for r in category_results]
            
            stats = {
                'category': category,
                'num_strategies': len(category_results),
                'avg_total_return': np.mean(total_returns),
                'std_total_return': np.std(total_returns),
                'avg_sharpe_ratio': np.mean(sharpe_ratios),
                'std_sharpe_ratio': np.std(sharpe_ratios),
                'avg_win_rate': np.mean(win_rates),
                'std_win_rate': np.std(win_rates),
                'avg_max_drawdown': np.mean(max_drawdowns),
                'std_max_drawdown': np.std(max_drawdowns),
                'best_strategy': max(category_results, key=lambda x: x.metrics['composite_score']).strategy_name,
                'best_composite_score': max(r.metrics.get('composite_score', 0) for r in category_results)
            }
            
            category_stats.append(stats)
        
        return pd.DataFrame(category_stats)
    
    def generate_ranking_report(self, results: List[StrategyResult]) -> Dict:
        """
        Generate comprehensive ranking report
        
        Args:
            results: List of StrategyResult objects
            
        Returns:
            Dictionary with ranking report
        """
        # Select top strategies
        top_strategies = self.select_top_strategies(results)
        
        # Generate summaries
        strategy_summary = self.get_strategy_summary(top_strategies)
        # Generate category analysis
        category_analysis = []
        for category, category_results in top_strategies.items():
            if category_results:
                best_strategy = max(category_results, key=lambda x: x.metrics.get('composite_score', 0))
                category_analysis.append({
                    'category': category,
                    'num_strategies': len(category_results),
                    'best_strategy': best_strategy.strategy_name,
                    'best_composite_score': best_strategy.metrics.get('composite_score', 0),
                    'avg_sharpe': np.mean([r.metrics.get('sharpe_ratio', 0) for r in category_results]),
                    'avg_return': np.mean([r.metrics.get('total_return', 0) for r in category_results]),
                    'avg_win_rate': np.mean([r.metrics.get('win_rate', 0) for r in category_results])
                })
        
        category_analysis_df = pd.DataFrame(category_analysis)
        
        # Calculate overall statistics
        total_strategies = len(results)
        filtered_strategies = len([r for r in results if self._meets_thresholds(r)])
        total_top_strategies = sum(len(strategies) for strategies in top_strategies.values())
        
        report = {
            'overview': {
                'total_strategies': total_strategies,
                'filtered_strategies': filtered_strategies,
                'top_strategies_selected': total_top_strategies,
                'categories_analyzed': len(top_strategies)
            },
            'top_strategies': top_strategies,
            'strategy_summary': strategy_summary,
            'category_analysis': category_analysis_df,
            'filtering_criteria': {
                'min_win_rate': self.min_win_rate,
                'min_profit_factor': self.min_profit_factor,
                'max_drawdown': self.max_drawdown,
                'min_sharpe_ratio': self.min_sharpe_ratio,
                'top_n_per_category': self.top_n
            }
        }
        
        return report
    
    def _meets_thresholds(self, result: StrategyResult) -> bool:
        """Check if strategy meets all thresholds"""
        metrics = result.metrics
        
        return (metrics['win_rate'] >= self.min_win_rate and
                metrics['profit_factor'] >= self.min_profit_factor and
                abs(metrics['max_drawdown']) <= self.max_drawdown and
                metrics['sharpe_ratio'] >= self.min_sharpe_ratio)
    
    def export_ranking_results(self, report: Dict, output_dir: str):
        """
        Export ranking results to Excel files
        
        Args:
            report: Ranking report dictionary
            output_dir: Output directory path
        """
        import os
        from pathlib import Path
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Create Excel writer
        excel_file = output_path / 'trading_strategy_results.xlsx'
        
        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            # Export strategy summary
            strategy_summary = report['strategy_summary']
            strategy_summary.to_excel(writer, sheet_name='Top_Strategies', index=False)
            
            # Export category analysis
            category_analysis = report['category_analysis']
            category_analysis.to_excel(writer, sheet_name='Category_Analysis', index=False)
            
            # Export detailed results by category
            for category, strategies in report['top_strategies'].items():
                category_data = []
                for strategy in strategies:
                    # Flatten metrics for Excel
                    metrics_flat = {}
                    for key, value in strategy.metrics.items():
                        if isinstance(value, (int, float, str)):
                            metrics_flat[f'metric_{key}'] = value
                        else:
                            metrics_flat[f'metric_{key}'] = str(value)
                    
                    category_data.append({
                        'strategy_name': strategy.strategy_name,
                        'description': strategy.get_strategy_description(),
                        'category': category,
                        **metrics_flat,
                        'parameters': str(strategy.parameters)
                    })
                
                category_df = pd.DataFrame(category_data)
                sheet_name = f'{category}_Strategies'[:31]  # Excel sheet name limit
                category_df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            # Create overview sheet
            overview_data = []
            for category, strategies in report['top_strategies'].items():
                for i, strategy in enumerate(strategies):
                    overview_data.append({
                        'rank': i + 1,
                        'category': category,
                        'strategy_name': strategy.strategy_name,
                        'description': strategy.get_strategy_description(),
                        'sharpe_ratio': strategy.metrics['sharpe_ratio'],
                        'total_return': strategy.metrics['total_return'],
                        'annual_return': strategy.metrics['annual_return'],
                        'win_rate': strategy.metrics['win_rate'],
                        'max_drawdown': strategy.metrics['max_drawdown'],
                        'profit_factor': strategy.metrics['profit_factor'],
                        'num_trades': strategy.metrics['num_trades'],
                        'volatility': strategy.metrics['volatility']
                    })
            
            overview_df = pd.DataFrame(overview_data)
            overview_df.to_excel(writer, sheet_name='Overview', index=False)
        
        # Also save CSV versions for compatibility
        strategy_summary.to_csv(output_path / 'top_strategies.csv', index=False)
        category_analysis.to_csv(output_path / 'category_analysis.csv', index=False)
        
        logger.info(f"Exported ranking results to Excel file: {excel_file}")
        logger.info(f"Also saved CSV versions for compatibility")
    
    def get_strategy_recommendations(self, report: Dict) -> Dict[str, List[str]]:
        """
        Generate strategy recommendations by category
        
        Args:
            report: Ranking report dictionary
            
        Returns:
            Dictionary with strategy recommendations
        """
        recommendations = {}
        
        for category, strategies in report['top_strategies'].items():
            category_recs = []
            
            for i, strategy in enumerate(strategies[:5]):  # Top 5 per category
                rec = {
                    'rank': i + 1,
                    'name': strategy.strategy_name,
                    'description': strategy.get_strategy_description(),
                    'key_metrics': {
                        'sharpe_ratio': strategy.metrics['sharpe_ratio'],
                        'total_return': strategy.metrics['total_return'],
                        'win_rate': strategy.metrics['win_rate'],
                        'max_drawdown': strategy.metrics['max_drawdown']
                    }
                }
                category_recs.append(rec)
            
            recommendations[category] = category_recs
        
        return recommendations