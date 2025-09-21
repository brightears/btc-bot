"""
Real-time Crypto News Fetcher
Aggregates news from multiple sources for LLM analysis
"""

import asyncio
import aiohttp
import feedparser
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional
import logging
import json
import os
from pathlib import Path

class CryptoNewsFetcher:
    """Fetches and aggregates crypto news from multiple sources"""

    def __init__(self):
        """Initialize news fetcher with multiple sources"""
        self.logger = logging.getLogger(__name__)

        # RSS feeds for crypto news
        self.rss_feeds = {
            'CoinDesk': 'https://feeds.feedburner.com/CoinDesk',
            'CryptoSlate': 'https://cryptoslate.com/feed/',
            'BeInCrypto': 'https://beincrypto.com/feed/',
            'Decrypt': 'https://decrypt.co/feed',
            'The Block': 'https://www.theblock.co/rss.xml',
            'Bitcoin Magazine': 'https://bitcoinmagazine.com/feed'
        }

        # API endpoints for additional sources
        self.api_sources = {
            'cryptopanic': {
                'url': 'https://cryptopanic.com/api/v1/posts/',
                'params': {
                    'auth_token': os.getenv('CRYPTOPANIC_TOKEN', 'demo'),
                    'currencies': 'BTC',
                    'filter': 'hot',
                    'kind': 'news'
                }
            }
        }

        # Cache settings
        self.cache_dir = Path('cache/news')
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_duration = timedelta(minutes=15)
        self.last_fetch = {}
        self.news_cache = {}

        # Keywords for filtering relevant news
        self.btc_keywords = [
            'bitcoin', 'btc', 'satoshi', 'lightning network',
            'mining', 'halving', 'difficulty adjustment', 'hash rate',
            'institutional', 'etf', 'grayscale', 'microstrategy',
            'el salvador', 'crypto regulation', 'sec', 'cftc'
        ]

        # Negative keywords to filter out noise
        self.filter_keywords = [
            'sponsored', 'advertisement', 'press release',
            'airdrop', 'giveaway', 'casino', 'lottery'
        ]

    async def fetch_all_news(self, max_age_hours: int = 24) -> List[Dict]:
        """Fetch news from all sources"""
        all_news = []

        # Check cache first
        cache_key = f"all_news_{max_age_hours}h"
        if self._is_cache_valid(cache_key):
            return self.news_cache[cache_key]

        # Fetch from RSS feeds
        rss_news = await self._fetch_rss_news(max_age_hours)
        all_news.extend(rss_news)

        # Fetch from APIs
        api_news = await self._fetch_api_news(max_age_hours)
        all_news.extend(api_news)

        # Sort by timestamp and deduplicate
        all_news = self._deduplicate_news(all_news)
        all_news.sort(key=lambda x: x['timestamp'], reverse=True)

        # Filter and rank
        filtered_news = self._filter_relevant_news(all_news)

        # Cache results
        self.news_cache[cache_key] = filtered_news
        self.last_fetch[cache_key] = datetime.now(timezone.utc)

        self.logger.info(f"Fetched {len(filtered_news)} relevant news items from {len(all_news)} total")
        return filtered_news

    async def _fetch_rss_news(self, max_age_hours: int) -> List[Dict]:
        """Fetch news from RSS feeds"""
        news_items = []
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)

        async with aiohttp.ClientSession() as session:
            tasks = []
            for source, url in self.rss_feeds.items():
                tasks.append(self._fetch_single_rss(session, source, url, cutoff_time))

            results = await asyncio.gather(*tasks, return_exceptions=True)

            for result in results:
                if isinstance(result, list):
                    news_items.extend(result)
                elif isinstance(result, Exception):
                    self.logger.error(f"RSS fetch error: {result}")

        return news_items

    async def _fetch_single_rss(self, session, source: str, url: str, cutoff_time: datetime) -> List[Dict]:
        """Fetch news from a single RSS feed"""
        try:
            async with session.get(url, timeout=10) as response:
                if response.status != 200:
                    return []

                content = await response.text()
                feed = feedparser.parse(content)

                news_items = []
                for entry in feed.entries[:20]:  # Limit to recent 20 items
                    try:
                        # Parse publication date
                        pub_date = self._parse_date(entry.get('published', entry.get('updated', '')))
                        if not pub_date or pub_date < cutoff_time:
                            continue

                        news_item = {
                            'source': source,
                            'title': entry.get('title', ''),
                            'summary': self._clean_html(entry.get('summary', '')),
                            'url': entry.get('link', ''),
                            'timestamp': pub_date,
                            'tags': [tag.term.lower() for tag in entry.get('tags', [])]
                        }

                        news_items.append(news_item)
                    except Exception as e:
                        self.logger.debug(f"Error parsing entry from {source}: {e}")

                return news_items

        except Exception as e:
            self.logger.error(f"Error fetching RSS from {source}: {e}")
            return []

    async def _fetch_api_news(self, max_age_hours: int) -> List[Dict]:
        """Fetch news from API sources"""
        news_items = []

        # CryptoPanic API
        if 'cryptopanic' in self.api_sources:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        self.api_sources['cryptopanic']['url'],
                        params=self.api_sources['cryptopanic']['params'],
                        timeout=10
                    ) as response:
                        if response.status == 200:
                            data = await response.json()

                            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)

                            for post in data.get('results', [])[:30]:
                                pub_date = self._parse_date(post.get('published_at', ''))
                                if not pub_date or pub_date < cutoff_time:
                                    continue

                                news_items.append({
                                    'source': 'CryptoPanic',
                                    'title': post.get('title', ''),
                                    'summary': post.get('title', ''),  # CryptoPanic doesn't provide summaries
                                    'url': post.get('url', ''),
                                    'timestamp': pub_date,
                                    'tags': [curr.lower() for curr in post.get('currencies', [])]
                                })
            except Exception as e:
                self.logger.error(f"Error fetching from CryptoPanic: {e}")

        return news_items

    async def get_breaking_news(self, max_age_minutes: int = 30) -> List[Dict]:
        """Get only very recent breaking news"""
        all_news = await self.fetch_all_news(max_age_hours=1)

        cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=max_age_minutes)
        breaking = [
            news for news in all_news
            if news['timestamp'] > cutoff_time
        ]

        return breaking

    async def get_market_moving_news(self) -> List[Dict]:
        """Get news likely to move markets"""
        all_news = await self.fetch_all_news(max_age_hours=6)

        # Keywords indicating market-moving events
        market_movers = [
            'sec', 'etf', 'approval', 'regulation', 'ban', 'adopt',
            'institutional', 'microstrategy', 'tesla', 'paypal',
            'hack', 'exploit', 'liquidation', 'whale', 'exchange',
            'halving', 'upgrade', 'fork', 'rate', 'inflation', 'fed'
        ]

        moving_news = []
        for news in all_news:
            title_lower = news['title'].lower()
            summary_lower = news.get('summary', '').lower()

            # Check for market-moving keywords
            for keyword in market_movers:
                if keyword in title_lower or keyword in summary_lower:
                    news['impact_score'] = self._calculate_impact_score(news, market_movers)
                    moving_news.append(news)
                    break

        # Sort by impact score
        moving_news.sort(key=lambda x: x.get('impact_score', 0), reverse=True)
        return moving_news[:10]  # Top 10 market movers

    def _filter_relevant_news(self, news_items: List[Dict]) -> List[Dict]:
        """Filter news for Bitcoin relevance"""
        filtered = []

        for item in news_items:
            # Skip if contains negative keywords
            text = f"{item['title']} {item.get('summary', '')}".lower()
            if any(keyword in text for keyword in self.filter_keywords):
                continue

            # Check for Bitcoin relevance
            relevance_score = 0
            for keyword in self.btc_keywords:
                if keyword in text:
                    relevance_score += 1

            # Include if relevant
            if relevance_score > 0 or 'btc' in item.get('tags', []):
                item['relevance_score'] = relevance_score
                filtered.append(item)

        return filtered

    def _deduplicate_news(self, news_items: List[Dict]) -> List[Dict]:
        """Remove duplicate news items"""
        seen_titles = set()
        unique_news = []

        for item in news_items:
            # Create a normalized title for comparison
            normalized = item['title'].lower().strip()
            normalized = ''.join(c for c in normalized if c.isalnum() or c.isspace())

            if normalized not in seen_titles:
                seen_titles.add(normalized)
                unique_news.append(item)

        return unique_news

    def _calculate_impact_score(self, news: Dict, keywords: List[str]) -> float:
        """Calculate potential market impact score"""
        score = 0
        text = f"{news['title']} {news.get('summary', '')}".lower()

        # Count keyword occurrences
        for keyword in keywords:
            score += text.count(keyword) * 2

        # Boost for very recent news
        age = datetime.now(timezone.utc) - news['timestamp']
        if age < timedelta(minutes=30):
            score += 5
        elif age < timedelta(hours=2):
            score += 2

        # Boost for certain sources
        trusted_sources = ['CoinDesk', 'The Block', 'CryptoPanic']
        if news['source'] in trusted_sources:
            score += 3

        return score

    def _parse_date(self, date_string: str) -> Optional[datetime]:
        """Parse various date formats"""
        if not date_string:
            return None

        # Common date formats
        formats = [
            '%Y-%m-%dT%H:%M:%S%z',
            '%Y-%m-%dT%H:%M:%SZ',
            '%a, %d %b %Y %H:%M:%S %z',
            '%Y-%m-%d %H:%M:%S',
        ]

        for fmt in formats:
            try:
                dt = datetime.strptime(date_string.replace('Z', '+0000'), fmt)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt
            except:
                continue

        return None

    def _clean_html(self, text: str) -> str:
        """Remove HTML tags from text"""
        import re
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        # Remove extra whitespace
        text = ' '.join(text.split())
        # Limit length
        if len(text) > 500:
            text = text[:497] + '...'
        return text

    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cache is still valid"""
        if cache_key not in self.last_fetch:
            return False

        age = datetime.now(timezone.utc) - self.last_fetch[cache_key]
        return age < self.cache_duration

    async def save_news_snapshot(self, news_items: List[Dict], filename: str = None):
        """Save news snapshot for analysis"""
        if not filename:
            filename = f"news_snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        filepath = self.cache_dir / filename

        # Convert datetime objects to strings
        serializable = []
        for item in news_items:
            item_copy = item.copy()
            if 'timestamp' in item_copy and isinstance(item_copy['timestamp'], datetime):
                item_copy['timestamp'] = item_copy['timestamp'].isoformat()
            serializable.append(item_copy)

        with open(filepath, 'w') as f:
            json.dump(serializable, f, indent=2)

        self.logger.info(f"Saved news snapshot to {filepath}")