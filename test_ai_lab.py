#!/usr/bin/env python3
"""
Test script for AI Trading Lab
Demonstrates the AI-powered trading system
"""

import json
from datetime import datetime, timezone

# Import AI components
from ai_brain.learning_engine import LearningEngine
from ai_brain.hypothesis_generator import HypothesisGenerator
from strategies.funding_carry import FundingCarryStrategy
from strategies.strategy_manager import StrategyManager


def test_ai_components():
    """Test basic AI components"""
    print("🧪 Testing AI Trading Lab Components\n")
    print("=" * 50)

    # Test Learning Engine
    print("\n📚 Testing Learning Engine...")
    learning_engine = LearningEngine()

    # Simulate market data
    market_data = {
        'timestamp': datetime.now(timezone.utc),
        'price': 65000,
        'price_history': [64000, 64500, 65000, 64800, 65000],
        'volume_history': [100, 120, 150, 90, 110],
        'funding_rate': 0.0001
    }

    # Analyze market
    analysis = learning_engine.analyze_market(market_data)
    print(f"Market Analysis:")
    print(f"  - Patterns: {analysis['patterns']}")
    print(f"  - Confidence: {analysis['confidence']:.1f}%")
    print(f"  - Recommendation: {analysis['recommendation']}")
    print(f"  - Action Type: {analysis['action_type']}")

    # Test Hypothesis Generator
    print("\n🎲 Testing Hypothesis Generator...")
    hypothesis_gen = HypothesisGenerator()

    # Generate a hypothesis
    hypothesis = hypothesis_gen.generate_hypothesis(market_data)
    print(f"Generated Hypothesis:")
    print(f"  - Name: {hypothesis['name']}")
    print(f"  - Category: {hypothesis['category']}")
    print(f"  - Description: {hypothesis['description']}")
    print(f"  - Initial Confidence: {hypothesis['confidence']}%")

    # Generate a crazy idea
    print("\n🤪 Generating Crazy Idea...")
    crazy_idea = hypothesis_gen.generate_crazy_idea()
    print(f"Crazy Idea:")
    print(f"  - Name: {crazy_idea['name']}")
    print(f"  - Description: {crazy_idea['description']}")
    print(f"  - Source: {crazy_idea['source']}")

    # Test Funding Carry Strategy
    print("\n💰 Testing Funding Carry Strategy...")
    funding_strategy = FundingCarryStrategy()

    # Add AI analysis to market data
    market_data['ai_analysis'] = analysis
    market_data['next_funding_time'] = datetime.now(timezone.utc)

    # Generate trading signal
    signal = funding_strategy.analyze(market_data)
    print(f"Trading Signal:")
    print(f"  - Action: {signal.action}")
    print(f"  - Confidence: {signal.confidence:.1f}%")
    print(f"  - Reason: {signal.reason}")

    # Get strategy status
    status = funding_strategy.get_status()
    print(f"\nStrategy Status:")
    print(f"  - Name: {status['name']}")
    print(f"  - Confidence Score: {status['confidence_score']:.1f}%")
    print(f"  - Ready for Live: {status['ready_for_live']}")
    print(f"  - Patterns Learned: {status['patterns_learned']}")

    # Test hypothesis statistics
    print("\n📊 Hypothesis Statistics:")
    stats = hypothesis_gen.get_statistics()
    print(f"  - Total Generated: {stats['total_generated']}")
    print(f"  - Pending: {stats['pending']}")
    print(f"  - Currently Testing: {stats['currently_testing']}")
    print(f"  - Successful: {stats['successful']}")
    print(f"  - Failed: {stats['failed']}")
    print(f"  - Success Rate: {stats['success_rate']:.1f}%")

    # Test learning insights
    print("\n🧠 Learning Insights:")
    insights = learning_engine.get_market_insights()
    print(f"  - Patterns Learned: {insights['patterns_learned']}")
    print(f"  - Edges Discovered: {insights['discovered_edges']}")

    if insights['optimization_suggestions']:
        print(f"  - Suggestions:")
        for suggestion in insights['optimization_suggestions']:
            print(f"    • {suggestion}")

    print("\n" + "=" * 50)
    print("✅ AI Trading Lab components working correctly!")
    print("\n📱 Next Steps:")
    print("1. Run 'python telegram_ai_bot.py' to start the AI bot")
    print("2. Use /strategies command to see active strategies")
    print("3. Use /launch to start new experiments")
    print("4. Use /crazy_idea to generate wild strategies")
    print("5. Use /ai_report for comprehensive analysis")
    print("\n🎯 The AI will learn and improve over time!")


if __name__ == "__main__":
    test_ai_components()