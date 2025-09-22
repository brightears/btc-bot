"""
Data Integrity Validator
Ensures ALL data used for trading decisions is REAL
Prevents any AI hallucination or fake data usage
"""

import logging
from datetime import datetime, timezone
from typing import Dict, List, Tuple, Optional


class DataIntegrityValidator:
    """Validates all data to ensure it's real and not simulated"""

    def __init__(self):
        """Initialize data validator"""
        self.logger = logging.getLogger(__name__)

        # Validation rules
        self.btc_price_min = 10000  # BTC should be above $10k
        self.btc_price_max = 500000  # BTC shouldn't exceed $500k
        self.max_price_change_per_minute = 0.1  # 10% max change
        self.min_volume = 1000  # Minimum volume in USDT (more reasonable)
        self.max_funding_rate = 0.01  # 1% max funding rate

        # Track last known good values
        self.last_valid_price = None
        self.last_valid_time = None
        self.validation_failures = 0

    def validate_market_data(self, data: Dict) -> Tuple[bool, List[str]]:
        """
        Validate market data for integrity

        Args:
            data: Market data to validate

        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []

        # Critical: Check if data is marked as real
        if not data.get('is_real_data', False):
            issues.append("CRITICAL: Data is not marked as real")
            self.logger.critical("Attempting to use non-real data!")
            return False, issues

        # Check timestamp freshness
        timestamp = data.get('timestamp')
        if timestamp:
            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            age = (datetime.now(timezone.utc) - timestamp).total_seconds()
            if age > 300:  # Data older than 5 minutes
                issues.append(f"Stale data: {age:.0f} seconds old")

        # Validate price
        price = data.get('price', 0)
        if price <= 0:
            issues.append("Invalid price: zero or negative")
        elif price < self.btc_price_min:
            issues.append(f"Price too low: ${price:.2f}")
        elif price > self.btc_price_max:
            issues.append(f"Price too high: ${price:.2f}")

        # Check for sudden price spikes
        if self.last_valid_price and self.last_valid_time:
            time_diff = (datetime.now(timezone.utc) - self.last_valid_time).total_seconds()
            if time_diff > 0 and time_diff < 60:  # Within last minute
                price_change = abs(price - self.last_valid_price) / self.last_valid_price
                if price_change > self.max_price_change_per_minute:
                    issues.append(f"Suspicious price spike: {price_change:.2%} in {time_diff:.0f}s")

        # Validate volume
        volume = data.get('volume', 0)
        if volume <= 0:
            issues.append("Invalid volume: zero or negative")
        elif volume < self.min_volume:
            issues.append(f"Volume too low: {volume:.0f}")

        # Validate funding rate
        funding_rate = data.get('funding_rate', 0)
        if abs(funding_rate) > self.max_funding_rate:
            issues.append(f"Extreme funding rate: {funding_rate:.4%}")

        # Check data quality score
        quality = data.get('data_quality', {})
        if quality.get('score', 100) < 50:
            issues.append(f"Low data quality score: {quality.get('score', 0)}")

        # Check for error flags
        if data.get('error'):
            issues.append(f"Data error: {data['error']}")

        # Update last known good values if valid
        if not issues and price > 0:
            self.last_valid_price = price
            self.last_valid_time = datetime.now(timezone.utc)
            self.validation_failures = 0
        else:
            self.validation_failures += 1

        # Too many consecutive failures is critical
        if self.validation_failures > 5:
            issues.append(f"Too many validation failures: {self.validation_failures}")

        is_valid = len(issues) == 0
        return is_valid, issues

    def validate_trading_signal(self, signal: Dict, market_data: Dict) -> Tuple[bool, List[str]]:
        """
        Validate a trading signal before execution

        Args:
            signal: Trading signal to validate
            market_data: Current market data

        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []

        # First validate the market data
        data_valid, data_issues = self.validate_market_data(market_data)
        if not data_valid:
            issues.extend([f"Market data: {issue}" for issue in data_issues])
            return False, issues

        # Check signal has required fields
        if not signal.get('action'):
            issues.append("Missing action in signal")

        if signal.get('action') in ['buy', 'sell'] and not signal.get('size'):
            issues.append("Missing size for trade signal")

        # Validate position size
        size = signal.get('size', 0)
        if size <= 0:
            issues.append(f"Invalid position size: {size}")
        elif size < 10:
            issues.append(f"Position size too small: ${size}")
        elif size > 10000:
            issues.append(f"Position size too large: ${size}")

        # Validate stop loss and take profit
        if signal.get('stop_loss'):
            sl = signal['stop_loss']
            price = market_data.get('price', 0)
            if signal.get('action') == 'buy' and sl >= price:
                issues.append(f"Stop loss ${sl:.2f} above entry price ${price:.2f}")
            elif signal.get('action') == 'sell' and sl <= price:
                issues.append(f"Stop loss ${sl:.2f} below entry price ${price:.2f}")

        if signal.get('take_profit'):
            tp = signal['take_profit']
            price = market_data.get('price', 0)
            if signal.get('action') == 'buy' and tp <= price:
                issues.append(f"Take profit ${tp:.2f} below entry price ${price:.2f}")
            elif signal.get('action') == 'sell' and tp >= price:
                issues.append(f"Take profit ${tp:.2f} above entry price ${price:.2f}")

        is_valid = len(issues) == 0
        return is_valid, issues

    def validate_hypothesis_parameters(self, hypothesis: Dict) -> Tuple[bool, List[str]]:
        """
        Validate hypothesis parameters are realistic

        Args:
            hypothesis: Hypothesis to validate

        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []

        # Check exit conditions
        exit_conditions = hypothesis.get('exit_conditions', [])
        for condition in exit_conditions:
            if condition.get('type') == 'take_profit':
                tp_value = condition.get('value', 0)
                if tp_value <= 0 or tp_value > 10:  # Max 10% TP
                    issues.append(f"Unrealistic take profit: {tp_value}%")

            elif condition.get('type') == 'stop_loss':
                sl_value = condition.get('value', 0)
                if sl_value <= 0 or sl_value > 5:  # Max 5% SL
                    issues.append(f"Unrealistic stop loss: {sl_value}%")

        # Check risk parameters
        risk_params = hypothesis.get('risk_parameters', {})
        max_pos = risk_params.get('max_position_size', 0)
        if max_pos <= 0 or max_pos > 10000:
            issues.append(f"Unrealistic position size: ${max_pos}")

        max_trades = risk_params.get('max_daily_trades', 0)
        if max_trades <= 0 or max_trades > 50:
            issues.append(f"Unrealistic daily trades: {max_trades}")

        is_valid = len(issues) == 0
        return is_valid, issues

    def get_validation_status(self) -> Dict:
        """Get current validation status"""
        return {
            'last_valid_price': self.last_valid_price,
            'last_valid_time': self.last_valid_time.isoformat() if self.last_valid_time else None,
            'consecutive_failures': self.validation_failures,
            'is_healthy': self.validation_failures < 3
        }

    def reset(self):
        """Reset validator state"""
        self.last_valid_price = None
        self.last_valid_time = None
        self.validation_failures = 0
        self.logger.info("Data validator reset")