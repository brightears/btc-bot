"""
Experience Replay Buffer for Deep Reinforcement Learning
Stores and samples trading experiences for improved learning
"""

import random
import json
import numpy as np
from collections import deque
from datetime import datetime, timezone
from typing import Dict, List, Tuple, Optional
from pathlib import Path
import logging


class Experience:
    """Single trading experience (state, action, reward, next_state)"""

    def __init__(self, state: Dict, action: str, reward: float,
                 next_state: Dict, done: bool, metadata: Optional[Dict] = None):
        """
        Initialize a trading experience

        Args:
            state: Market state before action
            action: Trading action taken (buy/sell/hold)
            reward: Profit/loss from action
            next_state: Market state after action
            done: Whether episode ended
            metadata: Additional info (strategy, confidence, etc.)
        """
        self.state = state
        self.action = action
        self.reward = reward
        self.next_state = next_state
        self.done = done
        self.metadata = metadata or {}
        self.timestamp = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> Dict:
        """Convert experience to dictionary"""
        return {
            'state': self.state,
            'action': self.action,
            'reward': self.reward,
            'next_state': self.next_state,
            'done': self.done,
            'metadata': self.metadata,
            'timestamp': self.timestamp
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Experience':
        """Create experience from dictionary"""
        exp = cls(
            state=data['state'],
            action=data['action'],
            reward=data['reward'],
            next_state=data['next_state'],
            done=data['done'],
            metadata=data.get('metadata', {})
        )
        exp.timestamp = data.get('timestamp', datetime.now(timezone.utc).isoformat())
        return exp


class PrioritizedReplayBuffer:
    """
    Prioritized Experience Replay Buffer
    Samples important experiences more frequently
    """

    def __init__(self, capacity: int = 10000, alpha: float = 0.6, beta: float = 0.4):
        """
        Initialize replay buffer

        Args:
            capacity: Maximum number of experiences to store
            alpha: Prioritization exponent (0 = uniform, 1 = full prioritization)
            beta: Importance sampling exponent
        """
        self.capacity = capacity
        self.alpha = alpha
        self.beta = beta
        self.beta_increment = 0.001

        self.buffer = deque(maxlen=capacity)
        self.priorities = deque(maxlen=capacity)
        self.max_priority = 1.0

        # Persistence
        self.save_path = Path("knowledge/experience_replay.json")
        self.save_path.parent.mkdir(parents=True, exist_ok=True)

        # Statistics
        self.stats = {
            'total_experiences': 0,
            'total_samples': 0,
            'avg_reward': 0,
            'win_rate': 0,
            'best_reward': float('-inf'),
            'worst_reward': float('inf')
        }

        self.logger = logging.getLogger(__name__)
        self.load_buffer()

    def add(self, experience: Experience, priority: Optional[float] = None):
        """
        Add experience to buffer with priority

        Args:
            experience: Trading experience to store
            priority: Priority score (higher = more important)
        """
        # Set priority (use max if not specified)
        if priority is None:
            priority = self.max_priority

        self.buffer.append(experience)
        self.priorities.append(priority)

        # Update statistics
        self.stats['total_experiences'] += 1
        reward = experience.reward

        # Update running average reward
        n = self.stats['total_experiences']
        self.stats['avg_reward'] = ((n - 1) * self.stats['avg_reward'] + reward) / n

        # Update win rate
        if reward > 0:
            wins = self.stats.get('wins', 0) + 1
            self.stats['wins'] = wins
            self.stats['win_rate'] = wins / n

        # Track best/worst
        self.stats['best_reward'] = max(self.stats['best_reward'], reward)
        self.stats['worst_reward'] = min(self.stats['worst_reward'], reward)

        # Save periodically
        if len(self.buffer) % 100 == 0:
            self.save_buffer()

    def sample(self, batch_size: int = 32) -> List[Experience]:
        """
        Sample batch of experiences with prioritization

        Args:
            batch_size: Number of experiences to sample

        Returns:
            List of sampled experiences
        """
        if len(self.buffer) < batch_size:
            return list(self.buffer)

        # Calculate sampling probabilities
        priorities = np.array(self.priorities)
        probs = priorities ** self.alpha
        probs /= probs.sum()

        # Sample indices
        indices = np.random.choice(len(self.buffer), batch_size, p=probs)

        # Get experiences
        samples = [self.buffer[i] for i in indices]

        # Update beta for importance sampling
        self.beta = min(1.0, self.beta + self.beta_increment)

        # Update statistics
        self.stats['total_samples'] += batch_size

        return samples

    def update_priorities(self, indices: List[int], priorities: List[float]):
        """
        Update priorities for sampled experiences

        Args:
            indices: Indices of experiences
            priorities: New priority values
        """
        for idx, priority in zip(indices, priorities):
            if 0 <= idx < len(self.priorities):
                self.priorities[idx] = priority
                self.max_priority = max(self.max_priority, priority)

    def get_recent_performance(self, n: int = 100) -> Dict:
        """
        Get performance metrics from recent experiences

        Args:
            n: Number of recent experiences to analyze

        Returns:
            Performance metrics
        """
        recent = list(self.buffer)[-n:] if len(self.buffer) >= n else list(self.buffer)

        if not recent:
            return {}

        rewards = [exp.reward for exp in recent]
        actions = [exp.action for exp in recent]

        return {
            'count': len(recent),
            'avg_reward': np.mean(rewards),
            'std_reward': np.std(rewards),
            'max_reward': max(rewards),
            'min_reward': min(rewards),
            'win_rate': sum(1 for r in rewards if r > 0) / len(rewards),
            'action_distribution': {
                'buy': actions.count('buy') / len(actions),
                'sell': actions.count('sell') / len(actions),
                'hold': actions.count('hold') / len(actions)
            },
            'sharpe_ratio': self._calculate_sharpe(rewards)
        }

    def _calculate_sharpe(self, rewards: List[float], risk_free_rate: float = 0.02) -> float:
        """Calculate Sharpe ratio from rewards"""
        if len(rewards) < 2:
            return 0.0

        returns = np.array(rewards)
        excess_returns = returns - (risk_free_rate / 365 / 24)  # Hourly risk-free rate

        if np.std(excess_returns) == 0:
            return 0.0

        return np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(24 * 365)

    def find_similar_experiences(self, state: Dict, k: int = 5) -> List[Experience]:
        """
        Find similar past experiences using state similarity

        Args:
            state: Current market state
            k: Number of similar experiences to return

        Returns:
            Most similar past experiences
        """
        if not self.buffer:
            return []

        # Calculate similarity scores
        similarities = []

        for exp in self.buffer:
            # Simple similarity based on price and RSI
            price_sim = 1 - abs(state.get('price', 0) - exp.state.get('price', 0)) / max(state.get('price', 1), exp.state.get('price', 1))
            rsi_sim = 1 - abs(state.get('rsi', 50) - exp.state.get('rsi', 50)) / 100
            volume_sim = 1 - abs(state.get('volume', 0) - exp.state.get('volume', 0)) / max(state.get('volume', 1), exp.state.get('volume', 1))

            similarity = (price_sim + rsi_sim + volume_sim) / 3
            similarities.append((similarity, exp))

        # Sort by similarity and return top k
        similarities.sort(key=lambda x: x[0], reverse=True)
        return [exp for _, exp in similarities[:k]]

    def get_strategy_performance(self) -> Dict:
        """Analyze performance by strategy"""
        strategy_stats = {}

        for exp in self.buffer:
            strategy = exp.metadata.get('strategy', 'unknown')

            if strategy not in strategy_stats:
                strategy_stats[strategy] = {
                    'count': 0,
                    'total_reward': 0,
                    'wins': 0,
                    'losses': 0
                }

            stats = strategy_stats[strategy]
            stats['count'] += 1
            stats['total_reward'] += exp.reward

            if exp.reward > 0:
                stats['wins'] += 1
            elif exp.reward < 0:
                stats['losses'] += 1

        # Calculate metrics
        for strategy, stats in strategy_stats.items():
            if stats['count'] > 0:
                stats['avg_reward'] = stats['total_reward'] / stats['count']
                stats['win_rate'] = stats['wins'] / stats['count'] if stats['count'] > 0 else 0

        return strategy_stats

    def save_buffer(self):
        """Save buffer to disk"""
        try:
            data = {
                'experiences': [exp.to_dict() for exp in list(self.buffer)[-1000:]],  # Save last 1000
                'stats': self.stats,
                'priorities': list(self.priorities)[-1000:],
                'saved_at': datetime.now(timezone.utc).isoformat()
            }

            with open(self.save_path, 'w') as f:
                json.dump(data, f, indent=2)

            self.logger.debug(f"Saved {len(data['experiences'])} experiences to disk")

        except Exception as e:
            self.logger.error(f"Error saving replay buffer: {e}")

    def load_buffer(self):
        """Load buffer from disk"""
        try:
            if self.save_path.exists():
                with open(self.save_path, 'r') as f:
                    data = json.load(f)

                # Load experiences
                for exp_data in data.get('experiences', []):
                    exp = Experience.from_dict(exp_data)
                    self.buffer.append(exp)

                # Load priorities
                for priority in data.get('priorities', []):
                    self.priorities.append(priority)

                # Load stats
                self.stats.update(data.get('stats', {}))

                self.logger.info(f"Loaded {len(self.buffer)} experiences from disk")

        except Exception as e:
            self.logger.error(f"Error loading replay buffer: {e}")

    def clear(self):
        """Clear the buffer"""
        self.buffer.clear()
        self.priorities.clear()
        self.stats = {
            'total_experiences': 0,
            'total_samples': 0,
            'avg_reward': 0,
            'win_rate': 0,
            'best_reward': float('-inf'),
            'worst_reward': float('inf')
        }

    def __len__(self):
        return len(self.buffer)

    def __repr__(self):
        return f"PrioritizedReplayBuffer(size={len(self)}/{self.capacity}, win_rate={self.stats['win_rate']:.2%})"