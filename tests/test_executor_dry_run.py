import pytest
import json
from pathlib import Path
from datetime import datetime, timezone
from src.funding.executor import FundingExecutor
from src.funding.model import FundingOpportunity, Position


class TestExecutorDryRun:
    @pytest.fixture
    def config(self):
        return {
            'symbol': 'BTC/USDT',
            'notional_usdt': 100,
            'threshold_bps': 0.5,
            'fee_bps': 7.0,
            'slippage_bps': 2.0,
            'leverage': 1,
            'maker_only': True,
            'whitelist_symbols': ['BTC/USDT'],
            'max_notional_usdt': 10000,
            'min_notional_usdt': 10,
            'max_leverage': 3,
            'max_positions': 1,
            'log_level': 'INFO'
        }

    @pytest.fixture
    def executor(self, config):
        return FundingExecutor(config, dry_run=True)

    def test_executor_initialization(self, executor, config):
        assert executor.dry_run == True
        assert executor.symbol == config['symbol']
        assert executor.notional_usdt == config['notional_usdt']
        assert executor.threshold_bps == config['threshold_bps']
        assert executor.position is None

    def test_state_file_creation(self, executor):
        executor._save_state()
        assert executor.state_file.exists()

        with open(executor.state_file, 'r') as f:
            state = json.load(f)

        assert 'timestamp' in state
        assert state['dry_run'] == True
        assert state['position'] is None

    def test_check_funding_opportunity(self, executor):
        opportunity = executor.check_funding_opportunity()

        assert opportunity is not None
        assert isinstance(opportunity, FundingOpportunity)
        assert opportunity.symbol == executor.symbol
        assert opportunity.notional_usdt == executor.notional_usdt

    def test_open_position_dry_run(self, executor):
        opportunity = FundingOpportunity(
            symbol='BTC/USDT',
            funding_rate_bps=10.0,
            spot_price=50000.0,
            futures_price=50001.0,
            notional_usdt=100,
            edge_bps=1.0,
            fees_bps=7.0,
            slippage_bps=2.0,
            next_funding_time=datetime.now(timezone.utc),
            is_profitable=True
        )

        success = executor.open_position(opportunity)

        assert success == True
        assert executor.position is not None
        assert executor.position.symbol == 'BTC/USDT'
        assert executor.position.notional_usdt == 100

    def test_close_position_dry_run(self, executor):
        executor.position = Position(
            symbol='BTC/USDT',
            spot_amount=0.002,
            futures_amount=0.002,
            spot_entry_price=50000,
            futures_entry_price=50001,
            notional_usdt=100,
            entry_time=datetime.now(timezone.utc)
        )

        success = executor.close_position()

        assert success == True
        assert executor.position is None

    def test_risk_guard_integration(self, executor):
        opportunity = FundingOpportunity(
            symbol='ETH/USDT',
            funding_rate_bps=10.0,
            spot_price=3000.0,
            futures_price=3001.0,
            notional_usdt=100,
            edge_bps=1.0,
            fees_bps=7.0,
            slippage_bps=2.0,
            next_funding_time=datetime.now(timezone.utc),
            is_profitable=True
        )

        success = executor.open_position(opportunity)
        assert success == False

    def test_state_persistence(self, executor):
        executor.position = Position(
            symbol='BTC/USDT',
            spot_amount=0.002,
            futures_amount=0.002,
            spot_entry_price=50000,
            futures_entry_price=50001,
            notional_usdt=100,
            entry_time=datetime.now(timezone.utc),
            funding_collected=5.0,
            realized_pnl=10.0
        )

        executor._save_state()

        new_executor = FundingExecutor(executor.config, dry_run=True)

        assert new_executor.position is not None
        assert new_executor.position.symbol == 'BTC/USDT'
        assert new_executor.position.funding_collected == 5.0
        assert new_executor.position.realized_pnl == 10.0

    def teardown_method(self):
        state_file = Path("logs/state.json")
        if state_file.exists():
            state_file.unlink()