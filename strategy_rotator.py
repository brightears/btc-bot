#!/usr/bin/env python3
"""
Intelligent Strategy Rotation System for Freqtrade
Automatically selects and rotates strategies based on recent performance
"""

import json
import subprocess
import os
from datetime import datetime, timedelta
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StrategyRotator:
    """
    Intelligently rotates Freqtrade strategies based on backtest performance
    """

    def __init__(self, config_file='config.json'):
        self.config_file = config_file
        self.strategies = [
            {'name': 'NostalgiaForInfinityX5', 'timeframe': '5m'},
            {'name': 'SimpleRSI', 'timeframe': '5m'},
            {'name': 'MomentumStrategy', 'timeframe': '15m'},
            {'name': 'BollingerMeanReversion', 'timeframe': '15m'}
        ]
        self.rotation_file = 'user_data/strategy_rotation_log.json'

    def run_backtest(self, strategy_name, timeframe, days=7):
        """Run backtest for a strategy"""
        logger.info(f"📊 Backtesting {strategy_name} on {timeframe}...")

        cmd = [
            'freqtrade', 'backtesting',
            '--strategy', strategy_name,
            '--timeframe', timeframe,
            '--timerange', f'{(datetime.now() - timedelta(days=days)).strftime("%Y%m%d")}-',
            '--export', 'none'
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )

            # Parse results from output
            output = result.stdout
            metrics = self._parse_backtest_output(output)
            metrics['strategy'] = strategy_name
            metrics['timeframe'] = timeframe

            return metrics

        except Exception as e:
            logger.error(f"❌ Backtest failed for {strategy_name}: {e}")
            return None

    def _parse_backtest_output(self, output):
        """Parse backtest output to extract metrics"""
        metrics = {
            'total_trades': 0,
            'win_rate': 0,
            'profit_pct': 0,
            'sharpe_ratio': 0,
            'max_drawdown': 0,
            'score': 0
        }

        try:
            # Extract metrics from Freqtrade output
            for line in output.split('\n'):
                if '│ Total/Daily Avg Trades' in line:
                    parts = line.split('│')
                    if len(parts) > 2:
                        metrics['total_trades'] = int(parts[2].strip().split()[0])

                elif '│ Win  Draw  Loss  Win%' in line:
                    parts = line.split('│')
                    if len(parts) > 2:
                        win_pct = parts[2].strip().split()[-1].replace('%', '')
                        metrics['win_rate'] = float(win_pct) if win_pct else 0

                elif '│ Absolute profit' in line:
                    parts = line.split('│')
                    if len(parts) > 2:
                        profit_str = parts[2].strip().split()[0]
                        metrics['profit_pct'] = float(profit_str) if profit_str else 0

                elif '│ Sharpe Ratio' in line:
                    parts = line.split('│')
                    if len(parts) > 2:
                        sharpe = parts[2].strip()
                        metrics['sharpe_ratio'] = float(sharpe) if sharpe and sharpe != '-' else 0

                elif '│ Max Drawdown' in line:
                    parts = line.split('│')
                    if len(parts) > 2:
                        dd_str = parts[2].strip().split()[0].replace('%', '')
                        metrics['max_drawdown'] = float(dd_str) if dd_str else 0

        except Exception as e:
            logger.warning(f"⚠️ Error parsing metrics: {e}")

        # Calculate composite score
        metrics['score'] = self._calculate_score(metrics)

        return metrics

    def _calculate_score(self, metrics):
        """Calculate composite score for strategy ranking"""
        # Weighted scoring system
        score = 0

        # Win rate (30%)
        if metrics['win_rate'] > 0:
            score += (metrics['win_rate'] / 100) * 30

        # Profit (40%)
        if metrics['profit_pct'] > 0:
            score += min(metrics['profit_pct'] * 10, 40)  # Cap at 40 points

        # Sharpe ratio (20%)
        if metrics['sharpe_ratio'] > 0:
            score += min(metrics['sharpe_ratio'] * 5, 20)  # Cap at 20 points

        # Drawdown penalty (10%)
        if metrics['max_drawdown'] > 0:
            score -= min(metrics['max_drawdown'] / 10, 10)

        # Trade count bonus
        if metrics['total_trades'] >= 20:
            score += 5
        elif metrics['total_trades'] >= 10:
            score += 2

        return max(score, 0)  # Don't go negative

    def select_best_strategy(self, min_trades=10):
        """Backtest all strategies and select the best one"""
        logger.info("🔄 Running strategy rotation analysis...")

        results = []
        for strategy in self.strategies:
            metrics = self.run_backtest(strategy['name'], strategy['timeframe'])
            if metrics and metrics['total_trades'] >= min_trades:
                results.append(metrics)
                logger.info(f"  {strategy['name']}: Score={metrics['score']:.2f}, Win Rate={metrics['win_rate']}%, Profit={metrics['profit_pct']}%")

        if not results:
            logger.warning("⚠️ No strategies met minimum trade count. Using default.")
            return self.strategies[0]  # Default to NFI

        # Sort by score
        results.sort(key=lambda x: x['score'], reverse=True)
        best = results[0]

        # Log rotation decision
        self._log_rotation(best, results)

        logger.info(f"✅ Selected strategy: {best['strategy']} (Score: {best['score']:.2f})")

        return {'name': best['strategy'], 'timeframe': best['timeframe']}

    def _log_rotation(self, selected, all_results):
        """Log strategy rotation decision"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'selected_strategy': selected['strategy'],
            'score': selected['score'],
            'all_results': all_results
        }

        # Load existing log
        log_data = []
        if os.path.exists(self.rotation_file):
            with open(self.rotation_file, 'r') as f:
                log_data = json.load(f)

        log_data.append(log_entry)

        # Keep only last 30 rotations
        log_data = log_data[-30:]

        # Save log
        os.makedirs(os.path.dirname(self.rotation_file), exist_ok=True)
        with open(self.rotation_file, 'w') as f:
            json.dump(log_data, f, indent=2)

    def update_config(self, strategy):
        """Update config.json with selected strategy"""
        with open(self.config_file, 'r') as f:
            config = json.load(f)

        # Update strategy in config
        config['strategy'] = strategy['name']
        config['timeframe'] = strategy['timeframe']

        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=4)

        logger.info(f"📝 Updated config.json with {strategy['name']}")


if __name__ == '__main__':
    rotator = StrategyRotator()
    best_strategy = rotator.select_best_strategy()
    rotator.update_config(best_strategy)

    print(f"\n✨ Strategy rotation complete!")
    print(f"   Active strategy: {best_strategy['name']}")
    print(f"   Timeframe: {best_strategy['timeframe']}")
    print(f"\n🚀 Ready to start Freqtrade with optimized strategy")
