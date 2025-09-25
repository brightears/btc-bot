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

    async def generate_hypothesis_with_web_research(self, market_context: Dict = None) -> Dict:
        """Generate hypothesis enhanced with web research"""
        if not self.llm_analyzer:
            return self.generate_hypothesis(market_context)

        try:
            # Search for successful trading strategies
            search_queries = [
                "successful Bitcoin trading strategies 2024",
                "profitable cryptocurrency arbitrage methods",
                "Bitcoin futures funding rate strategy",
                "crypto market making profitable strategies"
            ]

            web_insights = []
            for query in search_queries[:2]:  # Limit to 2 searches
                try:
                    results = await self.llm_analyzer.search_market_intel(query)
                    if results and results.get('insights'):
                        web_insights.extend(results['insights'][:2])  # Top 2 insights per query
                except Exception as e:
                    print(f"Web research error for query '{query}': {e}")

            # Generate hypothesis with web insights
            if web_insights:
                enhanced_context = market_context or {}
                enhanced_context['web_insights'] = web_insights

                hypothesis = await self._generate_llm_hypothesis(enhanced_context)
                if hypothesis:
                    hypothesis['web_research'] = True
                    hypothesis['insights_used'] = len(web_insights)
                    self.hypotheses['pending'].append(hypothesis)
                    self.save_hypotheses()
                    return hypothesis

            # Fallback to regular generation
            return self.generate_hypothesis(market_context)

        except Exception as e:
            print(f"Error in web research hypothesis generation: {e}")
            return self.generate_hypothesis(market_context)

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

    def mutate_successful_strategy(self, successful_hypothesis: Dict) -> Dict:
        """Create a mutation of a successful strategy"""
        base_id = successful_hypothesis['id']
        mutation_id = hashlib.md5(f"mutation_{base_id}_{datetime.now(timezone.utc).isoformat()}".encode()).hexdigest()[:8]

        # Create variations
        variations = [
            "tighter_risk_parameters",
            "wider_entry_conditions",
            "different_timeframe",
            "adjusted_thresholds",
            "combined_with_sentiment"
        ]

        variation = random.choice(variations)

        mutated_hypothesis = {
            'id': mutation_id,
            'name': f"{successful_hypothesis['name']} - {variation.replace('_', ' ').title()}",
            'category': 'strategy_mutation',
            'pattern': successful_hypothesis.get('pattern', 'unknown'),
            'parent_strategy': base_id,
            'mutation_type': variation,
            'description': f"Mutated version of successful strategy: {successful_hypothesis['description']}",
            'entry_conditions': self._mutate_conditions(successful_hypothesis.get('entry_conditions', []), variation),
            'exit_conditions': self._mutate_conditions(successful_hypothesis.get('exit_conditions', []), variation),
            'risk_parameters': self._mutate_risk_parameters(successful_hypothesis.get('risk_parameters', {}), variation),
            'confidence': max(40, successful_hypothesis.get('confidence', 50) - 10),  # Slightly lower confidence
            'created_at': datetime.now(timezone.utc).isoformat(),
            'status': 'pending',
            'backtest_required': True,
            'is_mutation': True
        }

        self.hypotheses['pending'].append(mutated_hypothesis)
        self.save_hypotheses()

        return mutated_hypothesis

    def _mutate_conditions(self, conditions: List[Dict], variation_type: str) -> List[Dict]:
        """Mutate strategy conditions based on variation type"""
        if not conditions:
            return conditions

        mutated = conditions.copy()

        if variation_type == "tighter_risk_parameters":
            # Make conditions more restrictive
            for condition in mutated:
                if condition.get('type') == 'threshold' and 'value' in condition:
                    condition['value'] *= 0.8  # 20% tighter

        elif variation_type == "wider_entry_conditions":
            # Make entry easier
            for condition in mutated:
                if condition.get('type') == 'threshold' and 'value' in condition:
                    condition['value'] *= 1.2  # 20% wider

        elif variation_type == "combined_with_sentiment":
            # Add sentiment condition
            mutated.append({'type': 'sentiment', 'condition': 'positive_sentiment_required'})

        return mutated

    def _mutate_risk_parameters(self, risk_params: Dict, variation_type: str) -> Dict:
        """Mutate risk parameters"""
        mutated = risk_params.copy()

        if variation_type == "tighter_risk_parameters":
            mutated['max_position_size'] = mutated.get('max_position_size', 100) * 0.7
            mutated['required_edge_bps'] = mutated.get('required_edge_bps', 0.3) * 1.5

        elif variation_type == "different_timeframe":
            mutated['holding_period_hours'] = random.choice([1, 4, 8, 24, 48])

        return mutated

    def import_proven_strategies(self) -> List[Dict]:
        """Import proven strategy templates as base hypotheses"""
        try:
            from strategies.proven_strategies import get_proven_strategies

            proven_strategies = get_proven_strategies()
            imported_hypotheses = []

            for strategy in proven_strategies:
                hypothesis_id = hashlib.md5(f"proven_{strategy.name}_{datetime.now(timezone.utc).isoformat()}".encode()).hexdigest()[:8]

                hypothesis = {
                    'id': hypothesis_id,
                    'name': f"Proven: {strategy.name}",
                    'category': 'proven_strategy',
                    'pattern': strategy.name.lower().replace(" ", "_"),
                    'description': strategy.description,
                    'entry_conditions': [{'type': 'proven_logic', 'condition': 'use_strategy_analyze_method'}],
                    'exit_conditions': [{'type': 'stop_loss', 'value': 1.0}, {'type': 'take_profit', 'value': 2.0}],
                    'risk_parameters': {
                        'max_position_size': 200,
                        'max_daily_trades': 5,
                        'required_edge_bps': 0.2
                    },
                    'confidence': 70,  # High confidence for proven strategies
                    'created_at': datetime.now(timezone.utc).isoformat(),
                    'status': 'pending',
                    'backtest_required': True,
                    'is_proven': True,
                    'strategy_class': strategy.__class__.__name__
                }

                imported_hypotheses.append(hypothesis)
                self.hypotheses['pending'].append(hypothesis)

            self.save_hypotheses()
            print(f"✅ Imported {len(imported_hypotheses)} proven strategy templates")

            return imported_hypotheses

        except ImportError as e:
            print(f"Could not import proven strategies: {e}")
            return []

    def _create_hypothesis_from_pattern(self, category: str, pattern: str, context: Dict = None) -> Dict:
        """Create a specific hypothesis from a pattern"""
        hypothesis_id = hashlib.md5(f"{pattern}_{datetime.now(timezone.utc).isoformat()}".encode()).hexdigest()[:8]

        hypothesis = {
            'id': hypothesis_id,
            'name': f"{pattern.replace('_', ' ').title()} Strategy",
            'category': category,
            'pattern': pattern,
            'description': self._generate_description(category, pattern),
            'entry_conditions': self._generate_entry_conditions(category, pattern),
            'exit_conditions': self._generate_exit_conditions(category, pattern, context),
            'risk_parameters': self._generate_risk_parameters(context),
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

    def _generate_exit_conditions(self, category: str, pattern: str, market_context: Dict = None) -> List[Dict]:
        """Generate exit conditions based on REAL market volatility"""
        # Use actual market volatility if available
        if market_context and market_context.get('is_real_data'):
            # Calculate ATR-based stops from real data
            price_history = market_context.get('price_history', [])
            if len(price_history) >= 14:
                # Calculate Average True Range
                atr = self._calculate_atr(price_history)
                current_price = market_context.get('price', 100000)
                atr_percent = (atr / current_price) * 100

                # Use ATR for realistic stops
                take_profit = min(3.0, atr_percent * 2)  # 2x ATR for TP, max 3%
                stop_loss = min(1.5, atr_percent)  # 1x ATR for SL, max 1.5%
            else:
                # Conservative defaults if not enough data
                take_profit = 1.0
                stop_loss = 0.5
        else:
            # Conservative defaults when no real data
            take_profit = 1.0
            stop_loss = 0.5

        exit_conditions = [
            {'type': 'take_profit', 'value': take_profit},
            {'type': 'stop_loss', 'value': stop_loss},
            {'type': 'time_based', 'value': 24}  # 24 hours default
        ]

        # Add pattern-specific exit
        if 'expiry' in pattern:
            exit_conditions.append({'type': 'event', 'condition': 'expiry_passed'})
        elif 'session' in pattern:
            exit_conditions.append({'type': 'session', 'condition': 'session_end'})

        return exit_conditions

    def _generate_risk_parameters(self, market_context: Dict = None) -> Dict:
        """Generate risk parameters based on REAL market conditions"""
        # Base position size on actual market conditions
        if market_context and market_context.get('is_real_data'):
            volume = market_context.get('volume', 1000000)
            volatility = market_context.get('volatility', 'medium')

            # Adjust position size based on liquidity
            if volume > 10000000:  # High liquidity
                max_position = 500
            elif volume > 5000000:  # Medium liquidity
                max_position = 300
            else:  # Low liquidity
                max_position = 100

            # Adjust trades based on volatility
            if volatility == 'high':
                max_trades = 2  # Fewer trades in high volatility
            elif volatility == 'low':
                max_trades = 5  # More trades in low volatility
            else:
                max_trades = 3

            # Required edge based on market conditions
            required_edge = 0.5 if volatility == 'high' else 0.3
        else:
            # Conservative defaults without real data
            max_position = 100
            max_trades = 2
            required_edge = 0.5

        return {
            'max_position_size': max_position,
            'max_daily_trades': max_trades,
            'max_correlation': 0.7,
            'required_edge_bps': required_edge,
            'min_liquidity': 1000000
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

    def _calculate_atr(self, price_history: List[float], period: int = 14) -> float:
        """Calculate Average True Range from price history"""
        if len(price_history) < period + 1:
            return 0

        true_ranges = []
        for i in range(1, min(period + 1, len(price_history))):
            high = max(price_history[i], price_history[i-1])
            low = min(price_history[i], price_history[i-1])
            true_range = high - low
            true_ranges.append(true_range)

        return sum(true_ranges) / len(true_ranges) if true_ranges else 0