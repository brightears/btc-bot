"""
AI Learning Engine
Learns from trading patterns and continuously improves strategies
"""

import json
import numpy as np
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
from collections import defaultdict
import statistics


class PatternRecognition:
    """Identifies and learns from market patterns"""

    def __init__(self):
        self.patterns_db = Path("knowledge/patterns.json")
        self.patterns_db.parent.mkdir(parents=True, exist_ok=True)
        self.patterns = self.load_patterns()

    def load_patterns(self) -> Dict:
        """Load learned patterns from disk"""
        if self.patterns_db.exists():
            with open(self.patterns_db, 'r') as f:
                return json.load(f)
        return {
            'price_patterns': [],
            'volume_patterns': [],
            'time_patterns': [],
            'correlation_patterns': [],
            'successful_conditions': []
        }

    def save_patterns(self):
        """Save patterns to disk"""
        with open(self.patterns_db, 'w') as f:
            json.dump(self.patterns, f, indent=2, default=str)

    def identify_pattern(self, market_data: Dict) -> Dict:
        """Identify patterns in current market data"""
        patterns_found = {
            'trend': self._identify_trend(market_data),
            'volatility': self._calculate_volatility(market_data),
            'volume_profile': self._analyze_volume(market_data),
            'time_pattern': self._identify_time_pattern(market_data),
            'funding_pattern': self._analyze_funding_pattern(market_data)
        }

        return patterns_found

    def _identify_trend(self, data: Dict) -> str:
        """Identify price trend"""
        prices = data.get('price_history', [])
        if len(prices) < 2:
            return 'neutral'

        recent_avg = np.mean(prices[-10:]) if len(prices) >= 10 else np.mean(prices)
        older_avg = np.mean(prices[-20:-10]) if len(prices) >= 20 else prices[0]

        if recent_avg > older_avg * 1.01:
            return 'bullish'
        elif recent_avg < older_avg * 0.99:
            return 'bearish'
        else:
            return 'neutral'

    def _calculate_volatility(self, data: Dict) -> str:
        """Calculate market volatility"""
        prices = data.get('price_history', [])
        if len(prices) < 2:
            return 'low'

        returns = [(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices))]
        volatility = np.std(returns) if returns else 0

        if volatility > 0.03:
            return 'high'
        elif volatility > 0.01:
            return 'medium'
        else:
            return 'low'

    def _analyze_volume(self, data: Dict) -> str:
        """Analyze volume patterns"""
        volumes = data.get('volume_history', [])
        if not volumes:
            return 'normal'

        avg_volume = np.mean(volumes)
        recent_volume = volumes[-1] if volumes else 0

        if recent_volume > avg_volume * 1.5:
            return 'high'
        elif recent_volume < avg_volume * 0.5:
            return 'low'
        else:
            return 'normal'

    def _identify_time_pattern(self, data: Dict) -> str:
        """Identify time-based patterns"""
        timestamp = data.get('timestamp', datetime.now(timezone.utc))
        hour = timestamp.hour

        # Define time zones
        if 14 <= hour <= 18:  # Discovered optimal hours
            return 'prime_time'
        elif 2 <= hour <= 6:
            return 'quiet_hours'
        else:
            return 'normal_hours'

    def _analyze_funding_pattern(self, data: Dict) -> str:
        """Analyze funding rate patterns"""
        funding_rate = data.get('funding_rate', 0)

        if funding_rate > 0.01:  # > 1%
            return 'extreme_positive'
        elif funding_rate > 0.005:
            return 'positive'
        elif funding_rate < -0.005:
            return 'negative'
        elif funding_rate < -0.01:
            return 'extreme_negative'
        else:
            return 'neutral'

    def learn_from_outcome(self, pattern: Dict, outcome: Dict):
        """Learn from trading outcome"""
        # Store successful patterns
        if outcome['profitable']:
            self.patterns['successful_conditions'].append({
                'pattern': pattern,
                'profit': outcome['profit'],
                'timestamp': datetime.now(timezone.utc).isoformat()
            })

            # Keep only recent successful patterns (last 1000)
            self.patterns['successful_conditions'] = self.patterns['successful_conditions'][-1000:]

        self.save_patterns()


class LearningEngine:
    """Main AI learning engine that coordinates all learning activities"""

    def __init__(self):
        self.pattern_recognition = PatternRecognition()
        self.insights_db = Path("knowledge/insights.json")
        self.insights_db.parent.mkdir(parents=True, exist_ok=True)
        self.insights = self.load_insights()
        self.learning_rate = 0.1
        self.exploration_rate = 0.2  # How often to try new things

        # Initialize Experience Replay Buffer
        try:
            from .experience_replay import PrioritizedReplayBuffer, Experience
            self.replay_buffer = PrioritizedReplayBuffer(capacity=10000)
            self.Experience = Experience
            self.has_replay = True
        except ImportError:
            self.replay_buffer = None
            self.has_replay = False
            print("Experience replay not available, continuing without it")

    def load_insights(self) -> Dict:
        """Load AI insights from disk"""
        if self.insights_db.exists():
            with open(self.insights_db, 'r') as f:
                return json.load(f)
        return {
            'market_correlations': {},
            'optimal_parameters': {},
            'strategy_performance': {},
            'discovered_edges': [],
            'failed_hypotheses': [],
            'confidence_levels': {}
        }

    def save_insights(self):
        """Save insights to disk"""
        with open(self.insights_db, 'w') as f:
            json.dump(self.insights, f, indent=2, default=str)

    def analyze_market(self, market_data: Dict) -> Dict:
        """Comprehensive market analysis with pattern recognition"""
        # Identify patterns
        patterns = self.pattern_recognition.identify_pattern(market_data)

        # Check against learned successful conditions
        similarity_scores = self._calculate_similarity_scores(patterns)

        # Generate confidence score
        confidence = self._calculate_confidence(patterns, similarity_scores)

        # Determine if we should explore or exploit
        action_type = 'explore' if np.random.random() < self.exploration_rate else 'exploit'

        analysis = {
            'patterns': patterns,
            'confidence': confidence,
            'action_type': action_type,
            'similarity_to_successful': max(similarity_scores) if similarity_scores else 0,
            'recommendation': self._generate_recommendation(patterns, confidence, action_type)
        }

        return analysis

    def _calculate_similarity_scores(self, current_pattern: Dict) -> List[float]:
        """Calculate similarity to successful patterns"""
        scores = []
        successful_patterns = self.pattern_recognition.patterns.get('successful_conditions', [])

        for past_success in successful_patterns[-100:]:  # Check last 100 successful patterns
            similarity = self._pattern_similarity(current_pattern, past_success.get('pattern', {}))
            scores.append(similarity)

        return scores

    def _pattern_similarity(self, pattern1: Dict, pattern2: Dict) -> float:
        """Calculate similarity between two patterns"""
        if not pattern1 or not pattern2:
            return 0.0

        matches = 0
        total = 0

        for key in pattern1:
            if key in pattern2:
                total += 1
                if pattern1[key] == pattern2[key]:
                    matches += 1

        return matches / total if total > 0 else 0.0

    def _calculate_confidence(self, patterns: Dict, similarity_scores: List[float]) -> float:
        """Calculate overall confidence in current market conditions"""
        base_confidence = 50.0

        # Adjust based on pattern recognition
        if patterns.get('trend') == 'neutral':
            base_confidence += 10
        if patterns.get('volatility') == 'low':
            base_confidence += 5
        if patterns.get('time_pattern') == 'prime_time':
            base_confidence += 15

        # Adjust based on similarity to successful patterns
        if similarity_scores:
            max_similarity = max(similarity_scores)
            base_confidence += max_similarity * 20

        # Cap confidence between 0 and 100
        return min(100, max(0, base_confidence))

    def _generate_recommendation(self, patterns: Dict, confidence: float, action_type: str) -> str:
        """Generate trading recommendation based on analysis"""
        if confidence > 70 and action_type == 'exploit':
            return 'strong_entry'
        elif confidence > 60:
            return 'cautious_entry'
        elif confidence < 30:
            return 'avoid'
        else:
            return 'monitor'

    def learn_from_trade(self, trade_data: Dict):
        """Learn from a completed trade"""
        strategy_id = trade_data.get('strategy_id', 'unknown')
        profit = trade_data.get('profit', 0)
        patterns = trade_data.get('patterns', {})

        # Store experience in replay buffer if available
        if self.has_replay and self.replay_buffer:
            state = trade_data.get('state', {})
            action = trade_data.get('action', 'hold')
            next_state = trade_data.get('next_state', state)
            done = trade_data.get('done', False)

            # Create experience
            experience = self.Experience(
                state=state,
                action=action,
                reward=profit,
                next_state=next_state,
                done=done,
                metadata={
                    'strategy': strategy_id,
                    'patterns': patterns,
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
            )

            # Add with priority based on profit magnitude
            priority = abs(profit) + 0.1  # Higher priority for larger profits/losses
            self.replay_buffer.add(experience, priority)

            # Learn from similar past experiences
            similar_experiences = self.replay_buffer.find_similar_experiences(state, k=5)
            if similar_experiences:
                # Adjust learning based on similar past outcomes
                avg_reward = sum(exp.reward for exp in similar_experiences) / len(similar_experiences)
                if avg_reward > 0:
                    self.learning_rate = min(0.2, self.learning_rate * 1.1)  # Learn faster from success
                else:
                    self.learning_rate = max(0.05, self.learning_rate * 0.95)  # Learn slower from failure

        # Update strategy performance tracking
        if strategy_id not in self.insights['strategy_performance']:
            self.insights['strategy_performance'][strategy_id] = {
                'total_trades': 0,
                'profitable_trades': 0,
                'total_profit': 0.0,
                'avg_profit': 0.0
            }

        perf = self.insights['strategy_performance'][strategy_id]
        perf['total_trades'] += 1
        perf['total_profit'] += profit

        if profit > 0:
            perf['profitable_trades'] += 1
            # Learn from successful pattern
            self.pattern_recognition.learn_from_outcome(
                patterns,
                {'profitable': True, 'profit': profit}
            )

        perf['avg_profit'] = perf['total_profit'] / perf['total_trades']

        # Discover new edges
        if profit > 0 and patterns:
            edge_description = f"{patterns.get('trend', 'unknown')}_trend_" \
                             f"{patterns.get('volatility', 'unknown')}_vol"
            if edge_description not in self.insights['discovered_edges']:
                self.insights['discovered_edges'].append({
                    'description': edge_description,
                    'discovered_at': datetime.now(timezone.utc).isoformat(),
                    'profit': profit
                })

        self.save_insights()

    def optimize_parameters(self, strategy_id: str, current_params: Dict, performance: float) -> Dict:
        """Optimize strategy parameters using gradient ascent"""
        if strategy_id not in self.insights['optimal_parameters']:
            self.insights['optimal_parameters'][strategy_id] = current_params.copy()

        optimal = self.insights['optimal_parameters'][strategy_id]

        # Simple gradient ascent optimization
        for param, value in current_params.items():
            if isinstance(value, (int, float)):
                # Calculate gradient direction
                gradient = performance - self.insights['strategy_performance'].get(
                    strategy_id, {}
                ).get('avg_profit', 0)

                if gradient > 0:
                    # Move parameters in the direction of better performance
                    optimal[param] = value + (value * self.learning_rate * gradient)
                else:
                    # Explore in opposite direction
                    optimal[param] = value - (value * self.learning_rate * abs(gradient))

        self.insights['optimal_parameters'][strategy_id] = optimal
        self.save_insights()

        return optimal

    def get_market_insights(self) -> Dict:
        """Get current market insights"""
        insights = {
            'discovered_edges': len(self.insights['discovered_edges']),
            'patterns_learned': len(self.pattern_recognition.patterns.get('successful_conditions', [])),
            'top_strategies': self._get_top_strategies(),
            'recent_discoveries': self.insights['discovered_edges'][-3:] if self.insights['discovered_edges'] else [],
            'optimization_suggestions': self._generate_optimization_suggestions()
        }

        # Add experience replay insights if available
        if self.has_replay and self.replay_buffer and len(self.replay_buffer) > 0:
            replay_stats = self.replay_buffer.get_recent_performance(100)
            insights['experience_memory'] = {
                'total_experiences': len(self.replay_buffer),
                'recent_win_rate': replay_stats.get('win_rate', 0),
                'recent_avg_reward': replay_stats.get('avg_reward', 0),
                'sharpe_ratio': replay_stats.get('sharpe_ratio', 0)
            }

            # Get strategy performance from replay buffer
            strategy_perf = self.replay_buffer.get_strategy_performance()
            if strategy_perf:
                insights['strategy_memory'] = strategy_perf

        return insights

    def _get_top_strategies(self) -> List[Dict]:
        """Get top performing strategies"""
        strategies = []
        for strategy_id, perf in self.insights['strategy_performance'].items():
            if perf['total_trades'] > 0:
                strategies.append({
                    'id': strategy_id,
                    'win_rate': (perf['profitable_trades'] / perf['total_trades']) * 100,
                    'avg_profit': perf['avg_profit'],
                    'total_profit': perf['total_profit']
                })

        # Sort by total profit
        strategies.sort(key=lambda x: x['total_profit'], reverse=True)
        return strategies[:5]  # Top 5

    def _generate_optimization_suggestions(self) -> List[str]:
        """Generate optimization suggestions based on learnings"""
        suggestions = []

        # Check time patterns
        successful_times = [p['pattern'].get('time_pattern') for p in
                           self.pattern_recognition.patterns.get('successful_conditions', [])
                           if p.get('pattern', {}).get('time_pattern')]

        if successful_times:
            most_common_time = max(set(successful_times), key=successful_times.count)
            suggestions.append(f"Focus trading during {most_common_time}")

        # Check volatility preferences
        successful_vols = [p['pattern'].get('volatility') for p in
                          self.pattern_recognition.patterns.get('successful_conditions', [])
                          if p.get('pattern', {}).get('volatility')]

        if successful_vols:
            most_common_vol = max(set(successful_vols), key=successful_vols.count)
            suggestions.append(f"Best performance during {most_common_vol} volatility")

        return suggestions

    def should_explore_new_strategy(self) -> bool:
        """Determine if we should explore new strategies"""
        # Explore more if we haven't found good edges
        if len(self.insights['discovered_edges']) < 5:
            return np.random.random() < 0.5  # 50% chance

        # Explore less if we have successful strategies
        top_strategies = self._get_top_strategies()
        if top_strategies and top_strategies[0]['win_rate'] > 70:
            return np.random.random() < 0.1  # 10% chance

        # Default exploration rate
        return np.random.random() < self.exploration_rate