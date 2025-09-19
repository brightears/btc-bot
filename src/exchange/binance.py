import os
import ccxt
from typing import Dict, Any, Optional, List, Tuple
from tenacity import retry, stop_after_attempt, wait_exponential
from src.utils.logger import get_logger
from src.utils.filters import apply_exchange_filters

logger = get_logger()


class BinanceClient:
    def __init__(self, testnet: bool = False, dry_run: bool = True):
        self.dry_run = dry_run
        self.testnet = testnet

        api_key = os.getenv('BINANCE_API_KEY', '')
        api_secret = os.getenv('BINANCE_API_SECRET', '')

        if not dry_run and (not api_key or not api_secret):
            logger.warning("Missing Binance API credentials, continuing in dry-run mode")
            self.dry_run = True

        self.spot = self._init_spot_client(api_key, api_secret)
        self.futures = self._init_futures_client(api_key, api_secret)

        self.markets_spot = {}
        self.markets_futures = {}

    def _init_spot_client(self, api_key: str, api_secret: str) -> ccxt.binance:
        config = {
            'apiKey': api_key if not self.dry_run else '',
            'secret': api_secret if not self.dry_run else '',
            'enableRateLimit': True,
            'options': {
                'defaultType': 'spot',
                'adjustForTimeDifference': True,
            }
        }

        if self.testnet:
            config['hostname'] = 'testnet.binance.vision'

        return ccxt.binance(config)

    def _init_futures_client(self, api_key: str, api_secret: str) -> ccxt.binanceusdm:
        config = {
            'apiKey': api_key if not self.dry_run else '',
            'secret': api_secret if not self.dry_run else '',
            'enableRateLimit': True,
            'options': {
                'defaultType': 'future',
                'adjustForTimeDifference': True,
            }
        }

        if self.testnet:
            config['hostname'] = 'testnet.binancefuture.com'

        return ccxt.binanceusdm(config)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def load_markets(self) -> None:
        try:
            self.markets_spot = self.spot.load_markets()
            self.markets_futures = self.futures.load_markets()
            logger.info(f"Loaded {len(self.markets_spot)} spot and {len(self.markets_futures)} futures markets")
        except Exception as e:
            logger.error(f"Failed to load markets: {e}")
            if not self.dry_run:
                raise

    def get_market_info(self, symbol: str, market_type: str = "spot") -> Dict[str, Any]:
        markets = self.markets_spot if market_type == "spot" else self.markets_futures
        return markets.get(symbol, {})

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def get_ticker(self, symbol: str, market_type: str = "spot") -> Dict[str, Any]:
        try:
            exchange = self.spot if market_type == "spot" else self.futures
            ticker = exchange.fetch_ticker(symbol)
            return ticker
        except Exception as e:
            logger.error(f"Failed to fetch ticker for {symbol}: {e}")
            if self.dry_run:
                return {
                    'symbol': symbol,
                    'bid': 50000.0,
                    'ask': 50001.0,
                    'last': 50000.5,
                    'baseVolume': 1000.0,
                    'quoteVolume': 50000000.0,
                }
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def get_funding_rate(self, symbol: str) -> Tuple[float, int]:
        try:
            funding = self.futures.fetch_funding_rate(symbol)
            rate = funding.get('fundingRate', 0.0)
            timestamp = funding.get('timestamp', 0)
            return rate, timestamp
        except Exception as e:
            logger.error(f"Failed to fetch funding rate for {symbol}: {e}")
            if self.dry_run:
                return 0.0001, 0
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def get_funding_history(self, symbol: str, limit: int = 10) -> List[Dict[str, Any]]:
        try:
            history = self.futures.fetch_funding_rate_history(symbol, limit=limit)
            return history
        except Exception as e:
            logger.error(f"Failed to fetch funding history for {symbol}: {e}")
            if self.dry_run:
                return []
            raise

    def place_spot_order(
        self,
        symbol: str,
        side: str,
        amount: float,
        price: Optional[float] = None,
        order_type: str = 'limit',
        post_only: bool = True
    ) -> Dict[str, Any]:
        if self.dry_run:
            order_id = f"DRY_SPOT_{side.upper()}_{symbol.replace('/', '')}_{amount}"
            logger.info(f"[DRY-RUN] Spot {side} order: {amount} {symbol} @ {price}")
            return {
                'id': order_id,
                'symbol': symbol,
                'side': side,
                'amount': amount,
                'price': price,
                'type': order_type,
                'status': 'closed',
                'filled': amount,
                'remaining': 0,
                'cost': amount * (price or 50000),
                'dry_run': True
            }

        try:
            market = self.get_market_info(symbol, 'spot')
            filtered_price, filtered_amount = apply_exchange_filters(
                symbol, price, amount, market, side
            )

            params = {}
            if post_only and order_type == 'limit':
                params['timeInForce'] = 'GTX'

            order = self.spot.create_order(
                symbol=symbol,
                type=order_type,
                side=side,
                amount=filtered_amount,
                price=filtered_price if order_type == 'limit' else None,
                params=params
            )

            logger.info(f"Placed spot {side} order: {order['id']}")
            return order

        except Exception as e:
            logger.error(f"Failed to place spot order: {e}")
            raise

    def place_futures_order(
        self,
        symbol: str,
        side: str,
        amount: float,
        price: Optional[float] = None,
        order_type: str = 'limit',
        reduce_only: bool = False,
        post_only: bool = True
    ) -> Dict[str, Any]:
        if self.dry_run:
            order_id = f"DRY_FUT_{side.upper()}_{symbol.replace('/', '')}_{amount}"
            logger.info(f"[DRY-RUN] Futures {side} order: {amount} {symbol} @ {price}")
            return {
                'id': order_id,
                'symbol': symbol,
                'side': side,
                'amount': amount,
                'price': price,
                'type': order_type,
                'status': 'closed',
                'filled': amount,
                'remaining': 0,
                'cost': amount * (price or 50000),
                'reduceOnly': reduce_only,
                'dry_run': True
            }

        try:
            market = self.get_market_info(symbol, 'futures')
            filtered_price, filtered_amount = apply_exchange_filters(
                symbol, price, amount, market, side
            )

            params = {'reduceOnly': reduce_only}
            if post_only and order_type == 'limit':
                params['timeInForce'] = 'GTX'

            order = self.futures.create_order(
                symbol=symbol,
                type=order_type,
                side=side,
                amount=filtered_amount,
                price=filtered_price if order_type == 'limit' else None,
                params=params
            )

            logger.info(f"Placed futures {side} order: {order['id']}")
            return order

        except Exception as e:
            logger.error(f"Failed to place futures order: {e}")
            raise

    def get_positions(self) -> List[Dict[str, Any]]:
        if self.dry_run:
            return []

        try:
            positions = self.futures.fetch_positions()
            return [p for p in positions if p['contracts'] != 0]
        except Exception as e:
            logger.error(f"Failed to fetch positions: {e}")
            return []

    def get_balances(self) -> Dict[str, Any]:
        if self.dry_run:
            return {
                'USDT': {'free': 10000, 'used': 0, 'total': 10000},
                'BTC': {'free': 0, 'used': 0, 'total': 0}
            }

        try:
            spot_balance = self.spot.fetch_balance()
            futures_balance = self.futures.fetch_balance()
            return {
                'spot': spot_balance,
                'futures': futures_balance
            }
        except Exception as e:
            logger.error(f"Failed to fetch balances: {e}")
            return {}

    def set_leverage(self, symbol: str, leverage: int = 1) -> bool:
        if self.dry_run:
            logger.info(f"[DRY-RUN] Set leverage for {symbol} to {leverage}x")
            return True

        try:
            self.futures.set_leverage(leverage, symbol)
            logger.info(f"Set leverage for {symbol} to {leverage}x")
            return True
        except Exception as e:
            logger.error(f"Failed to set leverage: {e}")
            return False