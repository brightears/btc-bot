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
        self.max_open_positions = 3  # Maximum concurrent positions to limit overtrading
        self.max_position_size = 100  # Base position size - actual size scaled by confidence

        # Performance tracking
        self.total_fees_paid = 0
        self.winning_trades = 0
        self.losing_trades = 0

        # State persistence
        self.state_file = Path("knowledge/paper_trading_state.json")
        self.load_state()

        # Repair any positions without stop-loss/take-profit
        self.repair_positions_without_stop_loss()

    def execute_trade(self, signal: Dict, market_data: Dict) -> Dict:
        """
        Execute a trade based on signal and REAL market data

        Args:
            signal: Trading signal with action, size, etc.
            market_data: Real-time market data

        Returns:
            Trade execution result
        """
        action = signal.get('action', 'hold')
        strategy_id = signal.get('strategy_id', 'unknown')
        size_usdt = signal.get('size', 0)

        self.logger.info(f"🎯 PAPER TRADING ENGINE - TRADE EXECUTION ATTEMPT:")
        self.logger.info(f"   Strategy ID: {strategy_id}")
        self.logger.info(f"   Action: {action.upper()}")
        self.logger.info(f"   Size: ${size_usdt:,.2f}")
        self.logger.info(f"   Current Balance: ${self.balance:,.2f}")
        self.logger.info(f"   Open Positions: {len(self.positions)}")
        self.logger.debug(f"Signal details: {signal}")
        self.logger.debug(f"Market data keys: {list(market_data.keys())}")

        # Validate we have real data
        is_real_data = market_data.get('is_real_data', False)
        self.logger.info(f"🔍 DATA VALIDATION CHECK:")
        self.logger.info(f"   Real data available: {is_real_data}")
        self.logger.info(f"   Data source: {market_data.get('source', 'unknown')}")

        if not is_real_data:
            self.logger.error("🚫 TRADE EXECUTION BLOCKED:")
            self.logger.error(f"   Strategy: {strategy_id}")
            self.logger.error(f"   Reason: No real market data available")
            self.logger.error(f"   Safety check: Data validation failed")
            return {
                'success': False,
                'error': 'No real market data available',
                'action': 'BLOCKED',
                'reason': 'Data safety check failed'
            }

        current_price = market_data.get('price', 0)
        self.logger.info(f"💰 MARKET PRICE VALIDATION:")
        self.logger.info(f"   Current BTC Price: ${current_price:,.2f}")
        self.logger.info(f"   Bid Price: ${market_data.get('bid', current_price):,.2f}")
        self.logger.info(f"   Ask Price: ${market_data.get('ask', current_price):,.2f}")

        if current_price <= 0:
            self.logger.error(f"🚫 TRADE EXECUTION BLOCKED:")
            self.logger.error(f"   Strategy: {strategy_id}")
            self.logger.error(f"   Reason: Invalid market price: {current_price}")
            return {'success': False, 'error': 'Invalid market price'}

        if action == 'buy':
            self.logger.info("📈 EXECUTING BUY ORDER:")
            return self._execute_buy(signal, current_price, market_data)
        elif action == 'sell':
            self.logger.info("📉 EXECUTING SELL ORDER:")
            return self._execute_sell(signal, current_price, market_data)
        elif action == 'close':
            self.logger.info("🔚 EXECUTING POSITION CLOSE:")
            return self._close_position(signal, current_price, market_data)
        else:
            self.logger.info(f"⏸️ HOLD ACTION - No trade executed")
            self.logger.info(f"   Strategy: {strategy_id} chose to wait")
            return {'success': True, 'action': 'hold'}

    def _execute_buy(self, signal: Dict, price: float, market_data: Dict) -> Dict:
        """Execute a buy order with real price and fees"""
        # CONFIDENCE-BASED POSITION SIZING
        # Scale position size based on confidence level to prevent overexposure
        confidence = signal.get('confidence', 50)  # Default 50% if not provided

        # Position sizing formula (aligned with 72% threshold):
        # - 72-80% confidence: 50% of base size (moderate conviction)
        # - 80-90% confidence: 75% of base size (high conviction)
        # - 90%+ confidence: 100% of base size (very high conviction)
        if confidence < 72:
            # Should not reach here due to strategy_manager threshold
            size_multiplier = 0.0
            self.logger.warning(f"⚠️ LOW CONFIDENCE DETECTED: {confidence}% < 72% minimum")
        elif confidence < 80:
            size_multiplier = 0.5  # 50% of base size
        elif confidence < 90:
            size_multiplier = 0.75  # 75% of base size
        else:
            size_multiplier = 1.0  # Full base size
        
        base_size = min(signal.get('size', self.max_position_size), self.max_position_size)
        size_usdt = base_size * size_multiplier
        
        self.logger.info(f"🎯 CONFIDENCE-BASED POSITION SIZING:")
        self.logger.info(f"   Signal Confidence: {confidence:.1f}%")
        self.logger.info(f"   Size Multiplier: {size_multiplier*100:.0f}%")
        self.logger.info(f"   Base Size: ${base_size:.2f}")
        self.logger.info(f"   Adjusted Size: ${size_usdt:.2f}")
        
        strategy_id = signal.get('strategy_id', 'unknown')

        # Check position limit
        if len(self.positions) >= self.max_open_positions:
            self.logger.warning(f"🚫 BUY ORDER REJECTED - Position limit reached:")
            self.logger.warning(f"   Current positions: {len(self.positions)}")
            self.logger.warning(f"   Max allowed: {self.max_open_positions}")
            return {'success': False, 'error': 'Maximum position limit reached'}

        self.logger.info(f"💵 BUY ORDER PREPARATION:")
        self.logger.info(f"   Strategy: {strategy_id}")
        self.logger.info(f"   Requested Size: ${size_usdt:,.2f}")
        self.logger.info(f"   Available Balance: ${self.balance:,.2f}")

        # Check balance
        if size_usdt > self.balance:
            self.logger.error(f"🚫 BUY ORDER REJECTED:")
            self.logger.error(f"   Strategy: {strategy_id}")
            self.logger.error(f"   Requested: ${size_usdt:,.2f}")
            self.logger.error(f"   Available: ${self.balance:,.2f}")
            self.logger.error(f"   Shortfall: ${size_usdt - self.balance:,.2f}")
            return {'success': False, 'error': 'Insufficient balance'}

        # Calculate actual execution price with slippage
        ask_price = market_data.get('ask', price)
        execution_price = ask_price * (1 + self.slippage)

        self.logger.info(f"💰 BUY ORDER PRICING:")
        self.logger.info(f"   Base Price: ${price:,.2f}")
        self.logger.info(f"   Ask Price: ${ask_price:,.2f}")
        self.logger.info(f"   Execution Price (with {self.slippage*100:.2f}% slippage): ${execution_price:,.2f}")

        # Calculate fees
        fee = size_usdt * self.taker_fee
        total_cost = size_usdt + fee

        self.logger.info(f"💳 BUY ORDER COSTS:")
        self.logger.info(f"   Order Size: ${size_usdt:,.2f}")
        self.logger.info(f"   Taker Fee ({self.taker_fee*100:.1f}%): ${fee:.2f}")
        self.logger.info(f"   Total Cost: ${total_cost:,.2f}")

        if total_cost > self.balance:
            # Adjust size for fees
            original_size = size_usdt
            size_usdt = self.balance / (1 + self.taker_fee) * 0.99  # Leave 1% buffer
            fee = size_usdt * self.taker_fee
            total_cost = size_usdt + fee

            self.logger.info(f"🔄 BUY ORDER SIZE ADJUSTMENT:")
            self.logger.info(f"   Original Size: ${original_size:,.2f}")
            self.logger.info(f"   Adjusted Size: ${size_usdt:,.2f}")
            self.logger.info(f"   New Fee: ${fee:.2f}")
            self.logger.info(f"   New Total Cost: ${total_cost:,.2f}")

        # Execute trade
        btc_amount = size_usdt / execution_price

        self.logger.info(f"🔄 EXECUTING BUY TRADE:")
        self.logger.info(f"   BTC Amount: {btc_amount:.8f} BTC")
        self.logger.info(f"   Execution Price: ${execution_price:,.2f}")
        self.logger.info(f"   Total USDT: ${size_usdt:,.2f}")

        # AUTOMATIC STOP-LOSS AND TAKE-PROFIT CALCULATION
        # If signal doesn't provide SL/TP, calculate them automatically
        stop_loss = signal.get('stop_loss')
        take_profit = signal.get('take_profit')

        if stop_loss is None:
            # Set stop-loss to 1% below entry price
            stop_loss = execution_price * 0.99
            self.logger.info(f"🛡️ AUTO STOP-LOSS SET:")
            self.logger.info(f"   Stop Loss: ${stop_loss:,.2f} (-1.0% from entry)")
        else:
            self.logger.info(f"📍 USING SIGNAL STOP-LOSS: ${stop_loss:,.2f}")

        if take_profit is None:
            # Set take-profit to 2% above entry price
            take_profit = execution_price * 1.02
            self.logger.info(f"🎯 AUTO TAKE-PROFIT SET:")
            self.logger.info(f"   Take Profit: ${take_profit:,.2f} (+2.0% from entry)")
        else:
            self.logger.info(f"📍 USING SIGNAL TAKE-PROFIT: ${take_profit:,.2f}")

        position = {
            'id': f"PT_{datetime.now(timezone.utc).isoformat()}",
            'type': 'long',
            'entry_price': execution_price,
            'size_btc': btc_amount,
            'size_usdt': size_usdt,
            'entry_fee': fee,
            'entry_time': datetime.now(timezone.utc).isoformat(),
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'strategy': signal.get('strategy_id', 'unknown')
        }

        # Update state
        self.positions.append(position)
        self.balance -= total_cost
        self.total_fees_paid += fee

        self.save_state()

        self.logger.info(f"✅ BUY ORDER EXECUTED SUCCESSFULLY:")
        self.logger.info(f"   Position ID: {position['id']}")
        self.logger.info(f"   Strategy: {strategy_id}")
        self.logger.info(f"   Amount: {btc_amount:.8f} BTC")
        self.logger.info(f"   Price: ${execution_price:.2f}")
        self.logger.info(f"   Stop Loss: ${stop_loss:,.2f} ({((stop_loss/execution_price - 1) * 100):.1f}%)")
        self.logger.info(f"   Take Profit: ${take_profit:,.2f} ({((take_profit/execution_price - 1) * 100):.1f}%)")
        self.logger.info(f"   Fee Paid: ${fee:.2f}")
        self.logger.info(f"   Remaining Balance: ${self.balance:,.2f}")
        self.logger.info(f"   Total Positions: {len(self.positions)}")

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
        strategy_id = signal.get('strategy_id', 'unknown')

        if not self.positions:
            self.logger.error(f"🚫 POSITION CLOSE REJECTED:")
            self.logger.error(f"   Strategy: {strategy_id}")
            self.logger.error(f"   Reason: No open positions available")
            return {'success': False, 'error': 'No open positions'}

        # Get position to close (oldest by default)
        position_id = signal.get('position_id')
        if position_id:
            position = next((p for p in self.positions if p['id'] == position_id), None)
            if not position:
                self.logger.error(f"🚫 POSITION CLOSE REJECTED:")
                self.logger.error(f"   Strategy: {strategy_id}")
                self.logger.error(f"   Reason: Position {position_id} not found")
                return {'success': False, 'error': 'Position not found'}
        else:
            position = self.positions[0]  # Close oldest

        self.logger.info(f"🔄 CLOSING POSITION:")
        self.logger.info(f"   Position ID: {position['id']}")
        self.logger.info(f"   Strategy: {strategy_id}")
        self.logger.info(f"   Entry Price: ${position['entry_price']:,.2f}")
        self.logger.info(f"   Size: {position['size_btc']:.8f} BTC (${position['size_usdt']:,.2f})")
        self.logger.info(f"   Current Price: ${price:,.2f}")

        # Calculate actual execution price with slippage
        bid_price = market_data.get('bid', price)
        execution_price = bid_price * (1 - self.slippage)

        self.logger.info(f"💰 POSITION CLOSE PRICING:")
        self.logger.info(f"   Current Price: ${price:,.2f}")
        self.logger.info(f"   Bid Price: ${bid_price:,.2f}")
        self.logger.info(f"   Execution Price (with {self.slippage*100:.2f}% slippage): ${execution_price:,.2f}")

        # Calculate proceeds and fees
        proceeds_usdt = position['size_btc'] * execution_price
        fee = proceeds_usdt * self.taker_fee
        net_proceeds = proceeds_usdt - fee

        # Calculate REAL P&L
        total_cost = position['size_usdt'] + position['entry_fee']
        pnl = net_proceeds - total_cost
        pnl_percent = (pnl / total_cost * 100) if total_cost > 0 else 0.0

        self.logger.info(f"📊 REAL P&L CALCULATION:")
        self.logger.info(f"   Gross Proceeds: ${proceeds_usdt:,.2f}")
        self.logger.info(f"   Exit Fee: ${fee:.2f}")
        self.logger.info(f"   Net Proceeds: ${net_proceeds:,.2f}")
        self.logger.info(f"   Total Cost (entry + fees): ${total_cost:,.2f}")
        self.logger.info(f"   REALIZED P&L: ${pnl:+.2f} ({pnl_percent:+.2f}%)")

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
            self.logger.info(f"🏆 WINNING TRADE RECORDED")
        else:
            self.losing_trades += 1
            self.logger.info(f"📉 LOSING TRADE RECORDED")

        # Update state
        self.positions.remove(position)
        self.closed_trades.append(closed_trade)
        self.balance += net_proceeds
        self.total_fees_paid += fee

        self.save_state()

        self.logger.info(f"✅ POSITION CLOSED SUCCESSFULLY:")
        self.logger.info(f"   Position ID: {position['id']}")
        self.logger.info(f"   Strategy: {strategy_id}")
        self.logger.info(f"   P&L: ${pnl:+.2f} ({pnl_percent:+.2f}%)")
        self.logger.info(f"   Exit Price: ${execution_price:.2f}")
        self.logger.info(f"   New Balance: ${self.balance:,.2f}")
        self.logger.info(f"   Open Positions: {len(self.positions)}")
        total_trades = self.winning_trades + self.losing_trades
        win_rate = (self.winning_trades / total_trades * 100) if total_trades > 0 else 0.0
        self.logger.info(f"   Win Rate: {win_rate:.1f}%")

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

        # Log monitoring activity if we have positions
        if self.positions:
            self.logger.debug(f"📊 MONITORING {len(self.positions)} POSITIONS FOR SL/TP:")
            self.logger.debug(f"   Current BTC Price: ${current_price:,.2f}")

        for position in self.positions[:]:  # Copy list since we modify it
            # Log position status for monitoring
            if position.get('stop_loss') and position.get('take_profit'):
                sl_distance = ((current_price - position['stop_loss']) / position['stop_loss']) * 100
                tp_distance = ((position['take_profit'] - current_price) / current_price) * 100
                self.logger.debug(f"   Position {position['id'][:20]}... Entry: ${position['entry_price']:.2f}, SL: ${position['stop_loss']:.2f} ({sl_distance:.2f}% away), TP: ${position['take_profit']:.2f} ({tp_distance:.2f}% away)")

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
                    self.logger.info(f"🚨 STOP LOSS TRIGGERED:")
                    self.logger.info(f"   Position: {position['id']}")
                    self.logger.info(f"   Trigger Price: ${position['stop_loss']:.2f}")
                    self.logger.info(f"   Current Price: ${current_price:.2f}")
                    self.logger.info(f"   P&L: ${result.get('pnl_usdt', 0):+.2f}")

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
                    self.logger.info(f"🏆 TAKE PROFIT TRIGGERED:")
                    self.logger.info(f"   Position: {position['id']}")
                    self.logger.info(f"   Trigger Price: ${position['take_profit']:.2f}")
                    self.logger.info(f"   Current Price: ${current_price:.2f}")
                    self.logger.info(f"   P&L: ${result.get('pnl_usdt', 0):+.2f}")

        return triggered_orders

    def get_performance_metrics(self, current_price: float = None) -> Dict:
        """Calculate performance metrics from REAL trades

        Args:
            current_price: Current BTC price for equity calculation
        """
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
                'open_positions': len(self.positions),
                'current_equity': self.get_current_equity(current_price)
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
            'current_equity': self.get_current_equity(current_price)
        }

    def get_current_equity(self, current_price: float = None) -> float:
        """Calculate current account equity including open positions

        Args:
            current_price: Current BTC price for calculating unrealized P&L

        Returns:
            Total account equity (cash balance + value of open positions)
        """
        equity = self.balance

        # Add value of open positions
        if self.positions:
            if current_price and current_price > 0:
                # Calculate unrealized P&L with current market price
                for position in self.positions:
                    position_value = position['size_btc'] * current_price
                    estimated_exit_fee = position_value * self.taker_fee
                    net_value = position_value - estimated_exit_fee
                    equity += net_value
            else:
                # No current price available - use original position cost
                for position in self.positions:
                    equity += position['size_usdt']

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

    def repair_positions_without_stop_loss(self):
        """Add stop-loss and take-profit to any positions that don't have them"""
        repaired_count = 0
        for position in self.positions:
            if position.get('stop_loss') is None or position.get('take_profit') is None:
                entry_price = position['entry_price']

                if position.get('stop_loss') is None:
                    position['stop_loss'] = entry_price * 0.99  # 1% below entry
                    self.logger.warning(f"🔧 REPAIRED POSITION {position['id'][:20]}...")
                    self.logger.warning(f"   Added missing stop-loss at ${position['stop_loss']:,.2f}")
                    repaired_count += 1

                if position.get('take_profit') is None:
                    position['take_profit'] = entry_price * 1.02  # 2% above entry
                    self.logger.warning(f"   Added missing take-profit at ${position['take_profit']:,.2f}")

        if repaired_count > 0:
            self.save_state()
            self.logger.info(f"✅ Repaired {repaired_count} positions with missing stop-loss/take-profit")

        return repaired_count

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