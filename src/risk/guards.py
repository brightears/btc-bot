from typing import Dict, Any, List
from src.funding.model import FundingOpportunity
from src.utils.logger import get_logger

logger = get_logger()


class RiskGuard:
    def __init__(self, config: Dict[str, Any]):
        self.max_notional = config.get('max_notional_usdt', 10000)
        self.min_notional = config.get('min_notional_usdt', 10)
        self.whitelist_symbols = config.get('whitelist_symbols', ['BTC/USDT'])
        self.max_leverage = config.get('max_leverage', 3)
        self.min_edge_bps = config.get('min_edge_bps', 0)
        self.max_positions = config.get('max_positions', 1)

        self.current_positions = 0

    def can_open_position(self, opportunity: FundingOpportunity) -> bool:
        checks = [
            self._check_symbol_whitelist(opportunity),
            self._check_notional_limits(opportunity),
            self._check_edge_threshold(opportunity),
            self._check_position_limit(),
        ]

        passed = all(checks)

        if not passed:
            logger.warning("Risk check failed")

        return passed

    def _check_symbol_whitelist(self, opportunity: FundingOpportunity) -> bool:
        if opportunity.symbol not in self.whitelist_symbols:
            logger.warning(
                f"Symbol {opportunity.symbol} not in whitelist {self.whitelist_symbols}"
            )
            return False
        return True

    def _check_notional_limits(self, opportunity: FundingOpportunity) -> bool:
        if opportunity.notional_usdt > self.max_notional:
            logger.warning(
                f"Notional ${opportunity.notional_usdt} exceeds max ${self.max_notional}"
            )
            return False

        if opportunity.notional_usdt < self.min_notional:
            logger.warning(
                f"Notional ${opportunity.notional_usdt} below min ${self.min_notional}"
            )
            return False

        return True

    def _check_edge_threshold(self, opportunity: FundingOpportunity) -> bool:
        if opportunity.edge_bps < self.min_edge_bps:
            logger.warning(
                f"Edge {opportunity.edge_bps:.2f} bps below min {self.min_edge_bps} bps"
            )
            return False
        return True

    def _check_position_limit(self) -> bool:
        if self.current_positions >= self.max_positions:
            logger.warning(
                f"Already have {self.current_positions} positions (max: {self.max_positions})"
            )
            return False
        return True

    def on_position_opened(self):
        self.current_positions += 1
        logger.info(f"Position opened. Current positions: {self.current_positions}")

    def on_position_closed(self):
        self.current_positions = max(0, self.current_positions - 1)
        logger.info(f"Position closed. Current positions: {self.current_positions}")

    def validate_leverage(self, leverage: int) -> bool:
        if leverage > self.max_leverage:
            logger.warning(f"Leverage {leverage} exceeds max {self.max_leverage}")
            return False

        if leverage < 1:
            logger.warning(f"Leverage {leverage} must be at least 1")
            return False

        return True

    def get_risk_metrics(self) -> Dict[str, Any]:
        return {
            'current_positions': self.current_positions,
            'max_positions': self.max_positions,
            'max_notional': self.max_notional,
            'min_notional': self.min_notional,
            'whitelist_symbols': self.whitelist_symbols,
            'max_leverage': self.max_leverage,
            'min_edge_bps': self.min_edge_bps
        }