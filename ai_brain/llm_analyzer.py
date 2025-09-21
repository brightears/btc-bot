"""
LLM Analyzer with Gemini 2.5 Flash
Real-time market analysis, news processing, and intelligent insights
"""

import os
import json
import asyncio
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path
import google.generativeai as genai
from dotenv import load_dotenv
import logging

load_dotenv()

class GeminiAnalyzer:
    """Gemini 2.5 Flash for ultra-fast market analysis"""

    def __init__(self):
        """Initialize Gemini 2.5 Flash"""
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")

        # Configure Gemini
        genai.configure(api_key=self.api_key)

        # Use Gemini 2.5 Flash for speed and cost efficiency
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')

        # Enable grounding with Google Search (free up to 1,500 requests/day)
        self.grounded_model = genai.GenerativeModel(
            'gemini-2.0-flash-exp',
            tools='google_search_retrieval'
        )

        # Cache for recent analyses
        self.analysis_cache = {}
        self.cache_duration = timedelta(minutes=5)

        # Set up logging
        self.logger = logging.getLogger(__name__)

    async def analyze_news(self, news_items: List[Dict]) -> Dict:
        """Analyze news sentiment and impact on market"""
        if not news_items:
            return {'sentiment': 'neutral', 'impact': 'low', 'summary': 'No recent news'}

        # Prepare news for analysis
        news_text = "\n".join([
            f"- {item.get('title', '')}: {item.get('summary', '')}"
            for item in news_items[:10]  # Analyze top 10 news items
        ])

        prompt = f"""Analyze these cryptocurrency news items and provide:
        1. Overall market sentiment (bullish/neutral/bearish)
        2. Potential price impact (high/medium/low)
        3. Key events or factors traders should know
        4. Trading opportunities or risks

        News:
        {news_text}

        Provide analysis in JSON format with keys: sentiment, impact, key_factors, opportunities, risks"""

        try:
            response = await self._async_generate(prompt)
            # Parse JSON from response
            return self._parse_json_response(response.text)
        except Exception as e:
            self.logger.error(f"News analysis error: {e}")
            return {
                'sentiment': 'neutral',
                'impact': 'low',
                'key_factors': [],
                'opportunities': [],
                'risks': ['Analysis unavailable']
            }

    async def analyze_market_conditions(self, market_data: Dict) -> Dict:
        """Comprehensive market analysis with Gemini"""
        prompt = f"""Analyze current Bitcoin market conditions:

        Price: ${market_data.get('price', 'N/A')}
        24h Volume: ${market_data.get('volume', 'N/A')}
        Funding Rate: {market_data.get('funding_rate', 'N/A')}
        Volatility: {market_data.get('volatility', 'N/A')}

        Provide analysis including:
        1. Current market state (trending/ranging/volatile)
        2. Strength of current trend
        3. Support and resistance levels
        4. Recommended trading stance (aggressive/conservative/neutral)
        5. Key risks to watch

        Format as JSON with keys: market_state, trend_strength, support_levels, resistance_levels, trading_stance, key_risks"""

        try:
            response = await self._async_generate(prompt)
            return self._parse_json_response(response.text)
        except Exception as e:
            self.logger.error(f"Market analysis error: {e}")
            return self._default_market_analysis()

    async def search_market_intel(self, query: str) -> Dict:
        """Use Google Search grounding for real-time market intelligence"""
        prompt = f"""Search and analyze: {query}

        Focus on:
        1. Most recent information (last 24 hours preferred)
        2. Credible sources only
        3. Actionable insights for traders
        4. Potential market impact

        Provide summary with: findings, sources, impact_assessment, trading_implications"""

        try:
            # Use grounded model for search
            response = await self._async_generate_grounded(prompt)
            return self._parse_json_response(response.text)
        except Exception as e:
            self.logger.error(f"Market intel search error: {e}")
            return {'findings': 'Search unavailable', 'impact_assessment': 'unknown'}

    async def generate_trading_hypothesis(self, market_context: Dict) -> Dict:
        """Generate creative trading strategies based on current conditions"""
        prompt = f"""Based on current market conditions, generate a unique trading hypothesis:

        Market Context:
        - Sentiment: {market_context.get('sentiment', 'neutral')}
        - Volatility: {market_context.get('volatility', 'medium')}
        - Recent patterns: {market_context.get('patterns', [])}
        - News factors: {market_context.get('news_factors', [])}

        Create a hypothesis that includes:
        1. Core thesis (what you believe will happen and why)
        2. Entry conditions
        3. Exit conditions
        4. Risk parameters
        5. Expected outcome
        6. Confidence level (0-100)

        Be creative but grounded in market reality. Format as JSON."""

        try:
            response = await self._async_generate(prompt)
            hypothesis = self._parse_json_response(response.text)
            hypothesis['generated_at'] = datetime.now(timezone.utc).isoformat()
            return hypothesis
        except Exception as e:
            self.logger.error(f"Hypothesis generation error: {e}")
            return self._default_hypothesis()

    async def evaluate_strategy(self, strategy: Dict, performance: Dict) -> Dict:
        """Evaluate strategy performance and suggest improvements"""
        prompt = f"""Evaluate this trading strategy's performance:

        Strategy: {json.dumps(strategy, indent=2)}
        Performance: {json.dumps(performance, indent=2)}

        Provide evaluation including:
        1. Effectiveness rating (0-100)
        2. Strengths and weaknesses
        3. Suggested improvements
        4. Risk assessment
        5. Should continue (yes/no/modify)

        Format as JSON with keys: effectiveness, strengths, weaknesses, improvements, risk_level, recommendation"""

        try:
            response = await self._async_generate(prompt)
            return self._parse_json_response(response.text)
        except Exception as e:
            self.logger.error(f"Strategy evaluation error: {e}")
            return {'effectiveness': 50, 'recommendation': 'continue with caution'}

    async def identify_market_regime(self, historical_data: List[Dict]) -> str:
        """Identify current market regime using LLM pattern recognition"""
        prompt = f"""Analyze this market data to identify the current regime:

        Recent price action: {historical_data[-20:] if len(historical_data) > 20 else historical_data}

        Classify as one of:
        - Bull Market (strong uptrend)
        - Bear Market (strong downtrend)
        - Accumulation (bottoming, smart money buying)
        - Distribution (topping, smart money selling)
        - Ranging (sideways, no clear trend)
        - Volatile (high volatility, unclear direction)

        Also explain your reasoning and key indicators."""

        try:
            response = await self._async_generate(prompt)
            # Extract regime from response
            for regime in ['Bull Market', 'Bear Market', 'Accumulation', 'Distribution', 'Ranging', 'Volatile']:
                if regime.lower() in response.text.lower():
                    return regime
            return 'Ranging'
        except Exception as e:
            self.logger.error(f"Regime identification error: {e}")
            return 'Ranging'

    async def _async_generate(self, prompt: str) -> Any:
        """Async wrapper for Gemini generation"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.model.generate_content, prompt)

    async def _async_generate_grounded(self, prompt: str) -> Any:
        """Async wrapper for grounded Gemini generation"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.grounded_model.generate_content, prompt)

    def _parse_json_response(self, text: str) -> Dict:
        """Parse JSON from Gemini response"""
        try:
            # Try to extract JSON from the response
            import re
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())

            # If no JSON found, parse structured response
            return self._parse_structured_response(text)
        except Exception as e:
            self.logger.error(f"JSON parsing error: {e}")
            return {}

    def _parse_structured_response(self, text: str) -> Dict:
        """Parse structured text response into dictionary"""
        result = {}
        lines = text.strip().split('\n')

        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower().replace(' ', '_')
                value = value.strip()

                # Try to parse value as appropriate type
                if value.lower() in ['true', 'false']:
                    result[key] = value.lower() == 'true'
                elif value.replace('.', '').replace('-', '').isdigit():
                    result[key] = float(value) if '.' in value else int(value)
                else:
                    result[key] = value

        return result

    def _default_market_analysis(self) -> Dict:
        """Default market analysis when LLM fails"""
        return {
            'market_state': 'unknown',
            'trend_strength': 50,
            'support_levels': [],
            'resistance_levels': [],
            'trading_stance': 'neutral',
            'key_risks': ['Analysis unavailable']
        }

    def _default_hypothesis(self) -> Dict:
        """Default hypothesis when generation fails"""
        return {
            'thesis': 'Market conditions unclear',
            'entry_conditions': [],
            'exit_conditions': [],
            'risk_parameters': {'stop_loss': 2, 'take_profit': 4},
            'confidence': 30,
            'generated_at': datetime.now(timezone.utc).isoformat()
        }