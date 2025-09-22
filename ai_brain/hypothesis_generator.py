"""
Hypothesis Generator
Generates creative trading strategy ideas from various sources
Enhanced with LLM capabilities for smarter hypothesis generation
"""

import random
import json
from datetime import datetime, timezone
from typing import Dict, List, Optional
from pathlib import Path
import hashlib
import asyncio


class HypothesisGenerator:
    """Generates creative trading hypotheses and strategy ideas"""

    def __init__(self, llm_analyzer=None):
        self.hypotheses_db = Path("knowledge/hypotheses.json")
        self.hypotheses_db.parent.mkdir(parents=True, exist_ok=True)
        self.hypotheses = self.load_hypotheses()
        self.creative_sources = self._initialize_creative_sources()
        self.llm_analyzer = llm_analyzer  # Gemini integration

        # Initialize cleaner to prevent file growth
        try:
            from .hypothesis_cleaner import HypothesisCleaner
            self.cleaner = HypothesisCleaner(max_per_category=50)
        except ImportError:
            self.cleaner = None

    def load_hypotheses(self) -> Dict:
        """Load hypotheses from disk"""
        if self.hypotheses_db.exists():
            with open(self.hypotheses_db, 'r') as f:
                return json.load(f)
        return {
            'pending': [],
            'testing': [],
            'successful': [],
            'failed': [],
            'crazy_ideas': []
        }

    def save_hypotheses(self):
        """Save hypotheses to disk"""
        # Clean before saving to prevent file growth
        if self.cleaner:
            self.cleaner.clean_hypotheses()
            # Reload after cleaning
            self.hypotheses = self.load_hypotheses()

        with open(self.hypotheses_db, 'w') as f:
            json.dump(self.hypotheses, f, indent=2, default=str)

    def _initialize_creative_sources(self) -> Dict:
        """Initialize sources of creative ideas"""
        return {
            'market_anomalies': [
                'weekend_effect',  # Different behavior on weekends
                'month_end_rebalancing',  # Institutional rebalancing patterns
                'options_expiry_pressure',  # Price pressure near expiry
                'asian_session_divergence',  # Asia vs US session patterns
                'pre_announcement_positioning'  # Before major announcements
            ],
            'cross_market_patterns': [
                'gold_btc_correlation',  # Traditional safe haven correlation
                'dxy_inverse',  # Dollar strength inverse relationship
                'equity_risk_on_off',  # Risk on/off with stock markets
                'oil_inflation_hedge',  # Commodity correlation
                'bond_yield_impact'  # Interest rate sensitivity
            ],
            'sentiment_indicators': [
                'fear_greed_extremes',  # Trade extremes in sentiment
                'social_volume_spike',  # Unusual social media activity
                'whale_accumulation',  # Large wallet movements
                'exchange_flows',  # Exchange in/outflows
                'long_short_ratio_extremes'  # Positioning extremes
            ],
            'technical_patterns': [
                'fibonacci_confluence',  # Multiple fib levels alignment
                'harmonic_patterns',  # Gartley, Butterfly patterns
                'elliott_wave_completion',  # Wave pattern completion
                'wyckoff_accumulation',  # Wyckoff method signals
                'order_block_retests'  # Institutional order zones
            ],
            'defi_indicators': [
                'stablecoin_flows',  # USDT/USDC movements
                'defi_tvl_shifts',  # Total value locked changes
                'lending_rate_spreads',  # DeFi vs CeFi rate arbitrage
                'liquidation_cascades',  # Liquidation level clustering
                'bridge_volume_anomalies'  # Cross-chain flow patterns
            ],
            'unconventional': [
                'lunar_cycles',  # Moon phase correlation (yes, really)
                'weather_patterns',  # Weather impact on trading
                'sports_events',  # Major sports event correlations
                'holiday_effects',  # Holiday season patterns
                'meme_momentum'  # Meme-driven price action
            ]
        }

    def generate_hypothesis(self, market_context: Dict = None) -> Dict:
        """Generate a new trading hypothesis"""
        # Use LLM if available for smarter generation
        if self.llm_analyzer and market_context:
            # Try to generate LLM-powered hypothesis
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # If already in async context, create task
                    hypothesis = asyncio.create_task(self._generate_llm_hypothesis(market_context))
                else:
                    # If not in async context, run directly
                    hypothesis = loop.run_until_complete(self._generate_llm_hypothesis(market_context))

                if hypothesis:
                    self.hypotheses['pending'].append(hypothesis)
                    self.save_hypotheses()
                    return hypothesis
            except Exception:
                pass  # Fall back to traditional generation

        # Traditional generation
        source_category = random.choice(list(self.creative_sources.keys()))
        source_pattern = random.choice(self.creative_sources[source_category])

        # Generate hypothesis based on pattern
        hypothesis = self._create_hypothesis_from_pattern(source_category, source_pattern, market_context)

        # Add to pending hypotheses
        self.hypotheses['pending'].append(hypothesis)
        self.save_hypotheses()

        return hypothesis

    async def _generate_llm_hypothesis(self, market_context: Dict) -> Optional[Dict]:
        """Generate hypothesis using LLM analysis"""
        if not self.llm_analyzer:
            return None

        try:
            # Use LLM to generate creative hypothesis
            llm_hypothesis = await self.llm_analyzer.generate_trading_hypothesis(market_context)

            if llm_hypothesis:
                # Convert LLM output to our format
                hypothesis_id = hashlib.md5(
                    f"{llm_hypothesis.get('thesis', '')}_{datetime.now(timezone.utc).isoformat()}".encode()
                ).hexdigest()[:8]

                hypothesis = {
                    'id': hypothesis_id,
                    'name': llm_hypothesis.get('thesis', 'LLM Generated Strategy')[:50],
                    'category': 'llm_generated',
                    'pattern': 'ai_insight',
                    'description': llm_hypothesis.get('thesis', ''),
                    'entry_conditions': llm_hypothesis.get('entry_conditions', []),
                    'exit_conditions': llm_hypothesis.get('exit_conditions', []),
                    'risk_parameters': llm_hypothesis.get('risk_parameters', self._generate_risk_parameters()),
                    'confidence': llm_hypothesis.get('confidence', 50),
                    'created_at': datetime.now(timezone.utc).isoformat(),
                    'status': 'pending',
                    'backtest_required': True,
                    'llm_generated': True,
                    'expected_outcome': llm_hypothesis.get('expected_outcome', 'Unknown')
                }

                return hypothesis
        except Exception:
            return None

        return None

    def _create_hypothesis_from_pattern(self, category: str, pattern: str, context: Dict) -> Dict:
        """Create a specific hypothesis from a pattern"""
        hypothesis_id = hashlib.md5(f"{pattern}_{datetime.now(timezone.utc).isoformat()}".encode()).hexdigest()[:8]

        hypothesis = {
            'id': hypothesis_id,
            'name': f"{pattern.replace('_', ' ').title()} Strategy",
            'category': category,
            'pattern': pattern,
            'description': self._generate_description(category, pattern),
            'entry_conditions': self._generate_entry_conditions(category, pattern),
            'exit_conditions': self._generate_exit_conditions(category, pattern),
            'risk_parameters': self._generate_risk_parameters(),
            'confidence': random.randint(30, 70),  # Initial confidence
            'created_at': datetime.now(timezone.utc).isoformat(),
            'status': 'pending',
            'backtest_required': True
        }

        return hypothesis

    def _generate_description(self, category: str, pattern: str) -> str:
        """Generate hypothesis description"""
        descriptions = {
            'weekend_effect': "Exploit lower weekend liquidity and reduced institutional activity for mean reversion trades",
            'lunar_cycles': "Test correlation between full/new moon cycles and market volatility spikes",
            'whale_accumulation': "Follow large wallet accumulation patterns for early trend detection",
            'fear_greed_extremes': "Counter-trade extreme fear/greed readings for mean reversion",
            'fibonacci_confluence': "Enter positions when multiple fibonacci levels align with support/resistance",
            'stablecoin_flows': "Track stablecoin movements to predict buying/selling pressure",
            'gold_btc_correlation': "Trade BTC based on gold correlation breaks or confirmations",
            'options_expiry_pressure': "Position before monthly options expiry for predictable price movements"
        }

        return descriptions.get(pattern, f"Experimental strategy based on {pattern.replace('_', ' ')} patterns")

    def _generate_entry_conditions(self, category: str, pattern: str) -> List[Dict]:
        """Generate entry conditions for hypothesis"""
        base_conditions = []

        if category == 'market_anomalies':
            base_conditions.append({'type': 'time_based', 'condition': f'{pattern}_active'})
            base_conditions.append({'type': 'volatility', 'condition': 'below_average'})

        elif category == 'sentiment_indicators':
            base_conditions.append({'type': 'sentiment', 'condition': f'{pattern}_triggered'})
            base_conditions.append({'type': 'volume', 'condition': 'above_average'})

        elif category == 'technical_patterns':
            base_conditions.append({'type': 'pattern', 'condition': f'{pattern}_formed'})
            base_conditions.append({'type': 'confirmation', 'condition': 'volume_confirmation'})

        elif category == 'defi_indicators':
            base_conditions.append({'type': 'on_chain', 'condition': f'{pattern}_signal'})
            base_conditions.append({'type': 'threshold', 'condition': 'above_threshold'})

        else:  # unconventional
            base_conditions.append({'type': 'experimental', 'condition': f'{pattern}_aligned'})
            base_conditions.append({'type': 'risk_check', 'condition': 'risk_acceptable'})

        return base_conditions

    def _generate_exit_conditions(self, category: str, pattern: str) -> List[Dict]:
        """Generate exit conditions for hypothesis"""
        exit_conditions = [
            {'type': 'take_profit', 'value': random.uniform(0.5, 2.0)},  # 0.5-2% TP
            {'type': 'stop_loss', 'value': random.uniform(0.3, 1.0)},  # 0.3-1% SL
            {'type': 'time_based', 'value': random.randint(4, 48)}  # 4-48 hours
        ]

        # Add pattern-specific exit
        if 'expiry' in pattern:
            exit_conditions.append({'type': 'event', 'condition': 'expiry_passed'})
        elif 'session' in pattern:
            exit_conditions.append({'type': 'session', 'condition': 'session_end'})

        return exit_conditions

    def _generate_risk_parameters(self) -> Dict:
        """Generate risk parameters for hypothesis"""
        return {
            'max_position_size': random.uniform(100, 500),  # USDT
            'max_daily_trades': random.randint(1, 5),
            'max_correlation': 0.7,  # Max correlation with other strategies
            'required_edge_bps': random.uniform(0.3, 1.0),
            'min_liquidity': 1000000  # Min 1M daily volume
        }

    def generate_crazy_idea(self) -> Dict:
        """Generate a particularly creative/unusual hypothesis"""
        crazy_patterns = [
            {
                'name': 'Mercury Retrograde Trader',
                'description': 'Trade inversely during Mercury retrograde periods based on historical correlation',
                'source': 'Astrological market analysis'
            },
            {
                'name': 'Emoji Sentiment Analyzer',
                'description': 'Trade based on emoji usage patterns in crypto Twitter',
                'source': 'Social media sentiment evolution'
            },
            {
                'name': 'Fibonacci Pizza Strategy',
                'description': 'Enter positions when price touches fibonacci levels during Bitcoin Pizza Day week',
                'source': 'Historical meme event analysis'
            },
            {
                'name': 'Whale Sneeze Detector',
                'description': 'Detect and trade micro-movements before whale market orders',
                'source': 'Order book microstructure analysis'
            },
            {
                'name': 'Weekend Warrior',
                'description': 'Exploit thin weekend liquidity with grid trading in range-bound conditions',
                'source': 'Liquidity pattern analysis'
            },
            {
                'name': 'Meme Coin Correlation Matrix',
                'description': 'Trade BTC based on aggregate meme coin momentum shifts',
                'source': 'Alternative asset correlation'
            },
            {
                'name': 'Full Moon Funding Hunter',
                'description': 'Increase position size during full moon if funding is positive',
                'source': 'Lunar cycle correlation study'
            },
            {
                'name': 'Twitter CEO Tweet Fade',
                'description': 'Counter-trade immediate reactions to influential figure tweets',
                'source': 'Social media overreaction patterns'
            }
        ]

        crazy_idea = random.choice(crazy_patterns)
        hypothesis_id = hashlib.md5(f"{crazy_idea['name']}_{datetime.now(timezone.utc).isoformat()}".encode()).hexdigest()[:8]

        hypothesis = {
            'id': hypothesis_id,
            'name': crazy_idea['name'],
            'category': 'crazy_idea',
            'description': crazy_idea['description'],
            'source': crazy_idea['source'],
            'confidence': random.randint(10, 40),  # Low initial confidence for crazy ideas
            'risk_limit': 100,  # Small position for crazy ideas
            'created_at': datetime.now(timezone.utc).isoformat(),
            'status': 'experimental',
            'explanation': f"AI generated this based on: {crazy_idea['source']}"
        }

        self.hypotheses['crazy_ideas'].append(hypothesis)
        self.save_hypotheses()

        return hypothesis

    def evaluate_hypothesis(self, hypothesis_id: str, results: Dict):
        """Evaluate hypothesis based on testing results"""
        # Find hypothesis
        hypothesis = None
        for status in ['testing', 'pending']:
            for h in self.hypotheses[status]:
                if h['id'] == hypothesis_id:
                    hypothesis = h
                    self.hypotheses[status].remove(h)
                    break

        if not hypothesis:
            return

        # Update hypothesis with results
        hypothesis['results'] = results
        hypothesis['evaluated_at'] = datetime.now(timezone.utc).isoformat()

        # Categorize based on performance
        if results.get('win_rate', 0) > 60 and results.get('profit', 0) > 0:
            hypothesis['status'] = 'successful'
            self.hypotheses['successful'].append(hypothesis)
            # Increase confidence in similar patterns
            self._boost_similar_hypotheses(hypothesis)
        else:
            hypothesis['status'] = 'failed'
            self.hypotheses['failed'].append(hypothesis)
            # Decrease confidence in similar patterns
            self._reduce_similar_hypotheses(hypothesis)

        self.save_hypotheses()

    def _boost_similar_hypotheses(self, successful_hypothesis: Dict):
        """Increase confidence in similar pending hypotheses"""
        pattern = successful_hypothesis.get('pattern', '')
        category = successful_hypothesis.get('category', '')

        for h in self.hypotheses['pending']:
            if h.get('category') == category or h.get('pattern', '').startswith(pattern[:5]):
                h['confidence'] = min(100, h.get('confidence', 50) + 10)

    def _reduce_similar_hypotheses(self, failed_hypothesis: Dict):
        """Decrease confidence in similar pending hypotheses"""
        pattern = failed_hypothesis.get('pattern', '')
        category = failed_hypothesis.get('category', '')

        for h in self.hypotheses['pending']:
            if h.get('category') == category or h.get('pattern', '').startswith(pattern[:5]):
                h['confidence'] = max(0, h.get('confidence', 50) - 5)

    def get_next_hypothesis_to_test(self) -> Optional[Dict]:
        """Get the next best hypothesis to test"""
        if not self.hypotheses['pending']:
            # Generate new hypothesis if none pending
            return self.generate_hypothesis()

        # Sort by confidence and pick top
        pending = sorted(
            self.hypotheses['pending'],
            key=lambda x: x.get('confidence', 0),
            reverse=True
        )

        if pending:
            hypothesis = pending[0]
            self.hypotheses['pending'].remove(hypothesis)
            self.hypotheses['testing'].append(hypothesis)
            hypothesis['status'] = 'testing'
            hypothesis['testing_started'] = datetime.now(timezone.utc).isoformat()
            self.save_hypotheses()
            return hypothesis

        return None

    def get_statistics(self) -> Dict:
        """Get hypothesis testing statistics"""
        total_tested = len(self.hypotheses['successful']) + len(self.hypotheses['failed'])
        success_rate = len(self.hypotheses['successful']) / total_tested if total_tested > 0 else 0

        return {
            'total_generated': sum(len(self.hypotheses[k]) for k in self.hypotheses.keys()),
            'pending': len(self.hypotheses['pending']),
            'currently_testing': len(self.hypotheses['testing']),
            'successful': len(self.hypotheses['successful']),
            'failed': len(self.hypotheses['failed']),
            'crazy_ideas': len(self.hypotheses['crazy_ideas']),
            'success_rate': success_rate * 100,
            'top_patterns': self._get_top_patterns()
        }

    def _get_top_patterns(self) -> List[str]:
        """Get most successful patterns"""
        pattern_success = {}
        for h in self.hypotheses['successful']:
            pattern = h.get('pattern', 'unknown')
            pattern_success[pattern] = pattern_success.get(pattern, 0) + 1

        # Sort by success count
        sorted_patterns = sorted(pattern_success.items(), key=lambda x: x[1], reverse=True)
        return [p[0] for p in sorted_patterns[:5]]  # Top 5 patterns