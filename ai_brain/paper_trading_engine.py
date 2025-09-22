"""
Real Paper Trading Engine
Uses ACTUAL market prices for realistic simulation
NO RANDOM NUMBERS - Everything based on real data
"""

import json
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import logging


class PaperTradingEngine:
    """Realistic paper trading using actual market data"""

    def __init__(self, initial_balance: float = 10000.0):
        """
        Initialize paper trading engine

        Args:
            initial_balance: Starting balance in USDT
        """
        self.logger = logging.getLogger(__name__)

        # Account state
        self.balance = initial_balance
        self.initial_balance = initial_balance
        self.positions = []  # Open positions
        self.closed_trades = []  # Trade history
        self.pending_orders = []  # Limit orders

        # Trading parameters (realistic)
        self.maker_fee = 0.001  # 0.1% maker fee (Binance)
        self.taker_fee = 0.001  # 0.1% taker fee (Binance)
        self.slippage = 0.0005  # 0.05% slippage on market orders
        self.min_order_size = 10  # $10 minimum order

        # Performance tracking
        self.total_fees_paid = 0
        self.winning_trades = 0
        self.losing_trades = 0

        # State persistence
        self.state_file = Path("knowledge/paper_trading_state.json")
        self.load_state()

    def execute_trade(self, signal: Dict, market_data: Dict) -> Dict:
        """
        Execute a trade based on signal and REAL market data

        Args:
            signal: Trading signal with action, size, etc.
            market_data: Real-time market data

        Returns:
            Trade execution result
        """
        # Validate we have real data
        if not market_data.get('is_real_data', False):
            self.logger.error("REFUSING TO TRADE - No real market data!")
            return {
                'success': False,
                'error': 'No real market data available',
                'action': 'BLOCKED'
            }

        current_price = market_data.get('price', 0)
        if current_price <= 0:
            self.logger.error(f"Invalid price: {current_price}")
            return {'success': False, 'error': 'Invalid market price'}

        action = signal.get('action', 'hold')

        if action == 'buy':
            return self._execute_buy(signal, current_price, market_data)
        elif action == 'sell':
            return self._execute_sell(signal, current_price, market_data)
        elif action == 'close':
            return self._close_position(signal, current_price, market_data)
        else:
            return {'success': True, 'action': 'hold'}

    def _execute_buy(self, signal: Dict, price: float, market_data: Dict) -> Dict:
        """Execute a buy order with real price and fees"""
        size_usdt = signal.get('size', 100)

        # Check balance
        if size_usdt > self.balance:
            return {'success': False, 'error': 'Insufficient balance'}

        # Calculate actual execution price with slippage
        ask_price = market_data.get('ask', price)
        execution_price = ask_price * (1 + self.slippage)

        # Calculate fees
        fee = size_usdt * self.taker_fee
        total_cost = size_usdt + fee

        if total_cost > self.balance:
            # Adjust size for fees
            size_usdt = self.balance / (1 + self.taker_fee) * 0.99  # Leave 1% buffer
            fee = size_usdt * self.taker_fee
            total_cost = size_usdt + fee

        # Execute trade
        btc_amount = size_usdt / execution_price

        position = {
            'id': f"PT_{datetime.now(timezone.utc).isoformat()}",
            'type': 'long',
            'entry_price': execution_price,
            'size_btc': btc_amount,
            'size_usdt': size_usdt,
            'entry_fee': fee,
            'entry_time': datetime.now(timezone.utc).isoformat(),
            'stop_loss': signal.get('stop_loss'),
            'take_profit': signal.get('take_profit'),
            'strategy': signal.get('strategy_id', 'unknown')
        }

        # Update state
        self.positions.append(position)
        self.balance -= total_cost
        self.total_fees_paid += fee

        self.save_state()

        self.logger.info(f"BUY executed: {btc_amount:.8f} BTC @ ${execution_price:.2f}")

        return {
            'success': True,
            'action': 'buy',
            'position': position,
            'execution_price': execution_price,
            'fee_paid': fee
        }

    def _execute_sell(self, signal: Dict, price: float, market_data: Dict) -> Dict:
        """Execute a sell/short order with real price"""
        # For now, we'll only close longs, not open shorts
        # This keeps it simpler and safer for initial implementation
        return self._close_position(signal, price, market_data)

    def _close_position(self, signal: Dict, price: float, market_data: Dict) -> Dict:
        """Close a position with real P&L calculation"""
        if not self.positions:
            return {'success': False, 'error': 'No open positions'}

        # Get position to close (oldest by default)
        position_id = signal.get('position_id')
        if position_id:
            position = next((p for p in self.positions if p['id'] == position_id), None)
            if not position:
                return {'success': False, 'error': 'Position not found'}
        else:
            position = self.positions[0]  # Close oldest

        # Calculate actual execution price with slippage
        bid_price = market_data.get('bid', price)
        execution_price = bid_price * (1 - self.slippage)

        # Calculate proceeds and fees
        proceeds_usdt = position['size_btc'] * execution_price
        fee = proceeds_usdt * self.taker_fee
        net_proceeds = proceeds_usdt - fee

        # Calculate REAL P&L
        total_cost = position['size_usdt'] + position['entry_fee']
        pnl = net_proceeds - total_cost
        pnl_percent = (pnl / total_cost) * 100

        # Record closed trade
        closed_trade = {
            **position,
            'exit_price': execution_price,
            'exit_time': datetime.now(timezone.utc).isoformat(),
            'exit_fee': fee,
            'pnl_usdt': pnl,
            'pnl_percent': pnl_percent,
            'duration_hours': self._calculate_duration(position['entry_time'])
        }

        # Update statistics
        if pnl > 0:
            self.winning_trades += 1
        else:
            self.losing_trades += 1

        # Update state
        self.positions.remove(position)
        self.closed_trades.append(closed_trade)
        self.balance += net_proceeds
        self.total_fees_paid += fee

        self.save_state()

        self.logger.info(
            f"Position CLOSED: {pnl:+.2f} USDT ({pnl_percent:+.2f}%) "
            f"@ ${execution_price:.2f}"
        )

        return {
            'success': True,
            'action': 'close',
            'closed_position': closed_trade,
            'pnl_usdt': pnl,
            'pnl_percent': pnl_percent
        }

    def check_stop_loss_take_profit(self, market_data: Dict) -> List[Dict]:
        """Check if any positions hit SL/TP based on REAL prices"""
        if not market_data.get('is_real_data', False):
            return []

        current_price = market_data.get('price', 0)
        triggered_orders = []

        for position in self.positions[:]:  # Copy list since we modify it
            # Check stop loss
            if position.get('stop_loss') and current_price <= position['stop_loss']:
                result = self._close_position(
                    {'position_id': position['id'], 'reason': 'stop_loss'},
                    current_price,
                    market_data
                )
                if result['success']:
                    triggered_orders.append({
                        'type': 'stop_loss',
                        'position_id': position['id'],
                        'trigger_price': position['stop_loss'],
                        'result': result
                    })
                    self.logger.info(f"STOP LOSS triggered at ${current_price:.2f}")

            # Check take profit
            elif position.get('take_profit') and current_price >= position['take_profit']:
                result = self._close_position(
                    {'position_id': position['id'], 'reason': 'take_profit'},
                    current_price,
                    market_data
                )
                if result['success']:
                    triggered_orders.append({
                        'type': 'take_profit',
                        'position_id': position['id'],
                        'trigger_price': position['take_profit'],
                        'result': result
                    })
                    self.logger.info(f"TAKE PROFIT triggered at ${current_price:.2f}")

        return triggered_orders

    def get_performance_metrics(self) -> Dict:
        """Calculate performance metrics from REAL trades"""
        if not self.closed_trades:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0,
                'total_pnl': 0,
                'roi': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'profit_factor': 0,
                'sharpe_ratio': 0,
                'max_drawdown': 0,
                'total_fees_paid': self.total_fees_paid,
                'current_balance': self.balance,
                'open_positions': len(self.positions)
            }

        # Calculate metrics from actual closed trades
        total_pnl = sum(t['pnl_usdt'] for t in self.closed_trades)
        wins = [t for t in self.closed_trades if t['pnl_usdt'] > 0]
        losses = [t for t in self.closed_trades if t['pnl_usdt'] <= 0]

        avg_win = sum(t['pnl_usdt'] for t in wins) / len(wins) if wins else 0
        avg_loss = sum(t['pnl_usdt'] for t in losses) / len(losses) if losses else 0

        # Calculate profit factor
        total_wins = sum(t['pnl_usdt'] for t in wins) if wins else 0
        total_losses = abs(sum(t['pnl_usdt'] for t in losses)) if losses else 1
        profit_factor = total_wins / total_losses if total_losses > 0 else 0

        # Calculate max drawdown
        equity_curve = []
        running_balance = self.initial_balance
        for trade in self.closed_trades:
            running_balance += trade['pnl_usdt']
            equity_curve.append(running_balance)

        max_drawdown = 0
        if equity_curve:
            peak = equity_curve[0]
            for value in equity_curve:
                if value > peak:
                    peak = value
                drawdown = (peak - value) / peak if peak > 0 else 0
                max_drawdown = max(max_drawdown, drawdown)

        return {
            'total_trades': len(self.closed_trades),
            'winning_trades': len(wins),
            'losing_trades': len(losses),
            'win_rate': (len(wins) / len(self.closed_trades) * 100) if self.closed_trades else 0,
            'total_pnl': total_pnl,
            'roi': (total_pnl / self.initial_balance * 100),
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'max_drawdown': max_drawdown * 100,
            'total_fees_paid': self.total_fees_paid,
            'current_balance': self.balance,
            'open_positions': len(self.positions),
            'current_equity': self.get_current_equity()
        }

    def get_current_equity(self) -> float:
        """Calculate current account equity including open positions"""
        equity = self.balance

        # Add unrealized P&L from open positions
        # Note: This requires current market price
        # We'll implement this when called with market data

        return equity

    def _calculate_duration(self, entry_time_str: str) -> float:
        """Calculate position duration in hours"""
        entry_time = datetime.fromisoformat(entry_time_str.replace('Z', '+00:00'))
        duration = datetime.now(timezone.utc) - entry_time
        return duration.total_seconds() / 3600

    def save_state(self):
        """Persist paper trading state to disk"""
        state = {
            'balance': self.balance,
            'initial_balance': self.initial_balance,
            'positions': self.positions,
            'closed_trades': self.closed_trades[-100:],  # Keep last 100 trades
            'total_fees_paid': self.total_fees_paid,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'last_updated': datetime.now(timezone.utc).isoformat()
        }

        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2, default=str)

    def load_state(self):
        """Load paper trading state from disk"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    state = json.load(f)

                self.balance = state.get('balance', self.initial_balance)
                self.positions = state.get('positions', [])
                self.closed_trades = state.get('closed_trades', [])
                self.total_fees_paid = state.get('total_fees_paid', 0)
                self.winning_trades = state.get('winning_trades', 0)
                self.losing_trades = state.get('losing_trades', 0)

                self.logger.info(f"Loaded paper trading state: Balance ${self.balance:.2f}")
            except Exception as e:
                self.logger.error(f"Error loading state: {e}")
                self.reset()

    def reset(self):
        """Reset paper trading account to initial state"""
        self.balance = self.initial_balance
        self.positions = []
        self.closed_trades = []
        self.pending_orders = []
        self.total_fees_paid = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.save_state()
        self.logger.info("Paper trading account reset")