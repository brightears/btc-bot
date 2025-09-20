#!/usr/bin/env python3
"""
Real-time monitoring dashboard for BTC Funding Bot
Shows current status, metrics, and market conditions
"""

import json
import os
import time
import ccxt
from datetime import datetime, timezone
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich.text import Text
from dotenv import load_dotenv

load_dotenv()


class FundingMonitor:
    def __init__(self):
        self.console = Console()
        self.state_file = Path("logs/state.json")
        self.metrics_file = Path("logs/metrics.json")
        self.log_file = Path("logs/funding_exec.log")

        # Initialize exchange for real-time data
        self.exchange = ccxt.binanceusdm({
            'enableRateLimit': True,
            'options': {'defaultType': 'future'}
        })

    def load_state(self):
        """Load current bot state"""
        if self.state_file.exists():
            with open(self.state_file, 'r') as f:
                return json.load(f)
        return {}

    def load_metrics(self):
        """Load performance metrics"""
        if self.metrics_file.exists():
            with open(self.metrics_file, 'r') as f:
                return json.load(f)
        return {
            'total_trades': 0,
            'winning_trades': 0,
            'total_pnl': 0.0,
            'total_funding': 0.0,
            'win_rate': 0.0
        }

    def get_latest_logs(self, n=5):
        """Get latest log entries"""
        if not self.log_file.exists():
            return []

        with open(self.log_file, 'r') as f:
            lines = f.readlines()
            return lines[-n:] if len(lines) >= n else lines

    def get_current_funding_rate(self):
        """Get current BTC funding rate"""
        try:
            funding = self.exchange.fetch_funding_rate('BTC/USDT')
            rate = funding.get('fundingRate', 0) * 10000  # Convert to bps
            next_time = funding.get('fundingTimestamp', 0)
            return rate, next_time
        except:
            return 0.0, 0

    def get_market_price(self):
        """Get current BTC price"""
        try:
            ticker = self.exchange.fetch_ticker('BTC/USDT')
            return ticker['last']
        except:
            return 0.0

    def create_status_panel(self, state):
        """Create status panel"""
        mode = "🔴 LIVE" if not state.get('dry_run', True) else "🟢 DRY-RUN"

        if state.get('position'):
            pos = state['position']
            status_text = Text()
            status_text.append("Status: ", style="bold")
            status_text.append("POSITION ACTIVE\n", style="bold green")
            status_text.append(f"Symbol: {pos.get('symbol', 'N/A')}\n")
            status_text.append(f"Notional: ${pos.get('notional_usdt', 0):.2f}\n")
            status_text.append(f"Entry: ${pos.get('spot_entry_price', 0):.2f}\n")
            status_text.append(f"Funding: ${pos.get('funding_collected', 0):.4f}\n")
        else:
            status_text = Text()
            status_text.append("Status: ", style="bold")
            status_text.append("MONITORING\n", style="bold yellow")
            status_text.append("No active position\n")
            status_text.append("Waiting for opportunity...\n")

        return Panel(
            status_text,
            title=f"Bot Status [{mode}]",
            border_style="green" if state.get('dry_run') else "red"
        )

    def create_market_panel(self):
        """Create market conditions panel"""
        funding_rate, _ = self.get_current_funding_rate()
        btc_price = self.get_market_price()

        # Calculate edge
        fee_bps = 7.0
        slippage_bps = 2.0
        edge_bps = funding_rate - fee_bps - slippage_bps

        market_text = Text()
        market_text.append(f"BTC Price: ${btc_price:,.2f}\n")
        market_text.append(f"Funding Rate: {funding_rate:.2f} bps\n")
        market_text.append(f"Edge: {edge_bps:.2f} bps ")

        if edge_bps > 0.5:
            market_text.append("✅ PROFITABLE", style="bold green")
        else:
            market_text.append("❌ NOT PROFITABLE", style="bold red")

        return Panel(
            market_text,
            title="Market Conditions",
            border_style="cyan"
        )

    def create_metrics_table(self, metrics):
        """Create metrics table"""
        table = Table(title="Performance Metrics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", justify="right")

        table.add_row("Total Trades", str(metrics.get('total_trades', 0)))
        table.add_row("Winning Trades", str(metrics.get('winning_trades', 0)))
        table.add_row("Win Rate", f"{metrics.get('win_rate', 0):.1f}%")
        table.add_row("Total P&L", f"${metrics.get('total_pnl', 0):.4f}")
        table.add_row("Total Funding", f"${metrics.get('total_funding', 0):.4f}")
        table.add_row("Best Trade", f"${metrics.get('best_trade', 0):.4f}")
        table.add_row("Worst Trade", f"${metrics.get('worst_trade', 0):.4f}")

        return table

    def create_logs_panel(self):
        """Create recent logs panel"""
        logs = self.get_latest_logs(5)
        log_text = Text()

        for log in logs:
            if "ERROR" in log:
                log_text.append(log.strip() + "\n", style="red")
            elif "WARNING" in log:
                log_text.append(log.strip() + "\n", style="yellow")
            elif "profitable" in log.lower():
                log_text.append(log.strip() + "\n", style="green")
            else:
                log_text.append(log.strip() + "\n")

        return Panel(
            log_text,
            title="Recent Activity",
            border_style="blue"
        )

    def create_dashboard(self):
        """Create full dashboard layout"""
        state = self.load_state()
        metrics = self.load_metrics()

        layout = Layout()
        layout.split_column(
            Layout(name="header", size=1),
            Layout(name="main"),
            Layout(name="footer", size=8)
        )

        layout["main"].split_row(
            Layout(name="left"),
            Layout(name="right")
        )

        # Header
        header = Text("🤖 BTC Funding Bot Monitor", style="bold magenta", justify="center")
        layout["header"].update(header)

        # Left side - Status and Market
        layout["left"].split_column(
            Layout(self.create_status_panel(state)),
            Layout(self.create_market_panel())
        )

        # Right side - Metrics
        layout["right"].update(self.create_metrics_table(metrics))

        # Footer - Logs
        layout["footer"].update(self.create_logs_panel())

        return layout

    def run(self):
        """Run the monitoring dashboard"""
        self.console.print("[bold cyan]Starting BTC Funding Bot Monitor...[/bold cyan]")
        self.console.print("Press Ctrl+C to exit\n")

        try:
            with Live(self.create_dashboard(), refresh_per_second=1, screen=True) as live:
                while True:
                    time.sleep(1)
                    live.update(self.create_dashboard())
        except KeyboardInterrupt:
            self.console.print("\n[bold red]Monitor stopped[/bold red]")


if __name__ == "__main__":
    monitor = FundingMonitor()
    monitor.run()