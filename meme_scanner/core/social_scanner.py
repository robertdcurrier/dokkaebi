"""
Social Media Scanner - Where we detect the rumbles before the earthquake
Reddit + Twitter = Early signals for tendies
"""
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import praw
import tweepy
from collections import Counter, defaultdict
import re
import time
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import numpy as np
from dataclasses import dataclass
import json

@dataclass
class SocialSignal:
    """A single social media signal"""
    ticker: str
    source: str  # 'reddit' or 'twitter'
    timestamp: datetime
    mentions: int
    sentiment: float
    engagement: float  # upvotes, likes, etc
    url: Optional[str] = None
    author_influence: float = 0.0
    content_preview: str = ""


class RedditScanner:
    """
    Scans Reddit for meme stock signals
    WSB is our home, but we monitor all the degenerate corners
    """
    
    def __init__(self, client_id: str, client_secret: str, user_agent: str):
        """Initialize Reddit API connection"""
        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
        self.ticker_pattern = re.compile(r'\b[A-Z]{1,5}\b')
        
        # Common false positives to filter
        self.false_positives = {
            'I', 'A', 'THE', 'IS', 'IT', 'OR', 'AND', 'NOT', 'IF', 'BE',
            'TO', 'IN', 'ON', 'AT', 'CEO', 'IPO', 'ETF', 'FDA', 'SEC',
            'USA', 'UK', 'EU', 'GDP', 'CPI', 'IMO', 'YOLO', 'FOMO', 'DD',
            'WSB', 'HODL', 'LOL', 'LMAO', 'WTF', 'IDK', 'IMHO', 'EPS'
        }
    
    async def scan_subreddit(self, subreddit_name: str, 
                            limit: int = 100,
                            timeframe: str = 'day') -> Dict[str, SocialSignal]:
        """Scan a single subreddit for ticker mentions"""
        signals = {}
        subreddit = self.reddit.subreddit(subreddit_name)
        
        # Get hot, new, and top posts
        posts_to_scan = []
        posts_to_scan.extend(subreddit.hot(limit=limit//3))
        posts_to_scan.extend(subreddit.new(limit=limit//3))
        posts_to_scan.extend(subreddit.top(timeframe, limit=limit//3))
        
        ticker_mentions = defaultdict(lambda: {
            'count': 0, 
            'sentiment_scores': [],
            'engagement': [],
            'posts': []
        })
        
        for post in posts_to_scan:
            # Extract tickers from title and selftext
            text = f"{post.title} {post.selftext}"
            potential_tickers = self.ticker_pattern.findall(text)
            
            # Filter out false positives
            tickers = [t for t in potential_tickers 
                      if t not in self.false_positives and len(t) >= 2]
            
            if tickers:
                # Calculate sentiment
                sentiment = self.sentiment_analyzer.polarity_scores(text)
                sentiment_score = sentiment['compound']
                
                # Calculate engagement
                engagement = post.score + (post.num_comments * 2)
                
                for ticker in set(tickers):  # Unique tickers per post
                    ticker_mentions[ticker]['count'] += 1
                    ticker_mentions[ticker]['sentiment_scores'].append(sentiment_score)
                    ticker_mentions[ticker]['engagement'].append(engagement)
                    ticker_mentions[ticker]['posts'].append({
                        'title': post.title[:100],
                        'url': f"https://reddit.com{post.permalink}",
                        'score': post.score,
                        'comments': post.num_comments
                    })
        
        # Create signals from aggregated data
        for ticker, data in ticker_mentions.items():
            if data['count'] >= 3:  # Minimum threshold
                signals[ticker] = SocialSignal(
                    ticker=ticker,
                    source='reddit',
                    timestamp=datetime.now(),
                    mentions=data['count'],
                    sentiment=np.mean(data['sentiment_scores']),
                    engagement=np.sum(data['engagement']),
                    url=data['posts'][0]['url'] if data['posts'] else None,
                    content_preview=data['posts'][0]['title'] if data['posts'] else ""
                )
        
        return signals
    
    async def scan_all_subreddits(self, subreddits: List[str]) -> Dict[str, SocialSignal]:
        """Scan multiple subreddits and aggregate results"""
        all_signals = {}
        
        for subreddit in subreddits:
            try:
                print(f"Scanning r/{subreddit}...")
                signals = await self.scan_subreddit(subreddit)
                
                # Merge signals
                for ticker, signal in signals.items():
                    if ticker in all_signals:
                        # Combine signals for same ticker
                        all_signals[ticker].mentions += signal.mentions
                        all_signals[ticker].engagement += signal.engagement
                        # Weighted average for sentiment
                        total_mentions = all_signals[ticker].mentions
                        all_signals[ticker].sentiment = (
                            (all_signals[ticker].sentiment * (total_mentions - signal.mentions) +
                             signal.sentiment * signal.mentions) / total_mentions
                        )
                    else:
                        all_signals[ticker] = signal
                        
            except Exception as e:
                print(f"Error scanning r/{subreddit}: {e}")
                continue
        
        return all_signals
    
    def get_trending_dd(self, subreddit_name: str = 'wallstreetbets', 
                       limit: int = 10) -> List[Dict]:
        """Get top Due Diligence posts"""
        subreddit = self.reddit.subreddit(subreddit_name)
        dd_posts = []
        
        for post in subreddit.search('flair:DD', limit=limit, sort='hot'):
            # Extract main ticker from post
            tickers = self.ticker_pattern.findall(f"{post.title} {post.selftext}")
            tickers = [t for t in tickers if t not in self.false_positives]
            
            if tickers:
                dd_posts.append({
                    'ticker': Counter(tickers).most_common(1)[0][0],
                    'title': post.title,
                    'url': f"https://reddit.com{post.permalink}",
                    'score': post.score,
                    'comments': post.num_comments,
                    'created': datetime.fromtimestamp(post.created_utc),
                    'preview': post.selftext[:500] if post.selftext else ""
                })
        
        return dd_posts


class TwitterScanner:
    """
    Twitter/X Scanner - Where news breaks and pumps begin
    """
    
    def __init__(self, api_key: str, api_secret: str, 
                 access_token: str, access_secret: str):
        """Initialize Twitter API v2 connection"""
        self.client = tweepy.Client(
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_secret
        )
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
        self.ticker_pattern = re.compile(r'\$[A-Z]{1,5}\b')
        
        # Track velocity (mentions over time)
        self.mention_history = defaultdict(list)
        
    async def search_ticker(self, ticker: str, max_results: int = 100) -> SocialSignal:
        """Search for a specific ticker on Twitter"""
        query = f"${ticker} -is:retweet lang:en"
        
        try:
            tweets = self.client.search_recent_tweets(
                query=query,
                max_results=max_results,
                tweet_fields=['created_at', 'public_metrics', 'author_id']
            )
            
            if not tweets.data:
                return None
            
            mentions = len(tweets.data)
            sentiments = []
            total_engagement = 0
            
            for tweet in tweets.data:
                # Calculate sentiment
                sentiment = self.sentiment_analyzer.polarity_scores(tweet.text)
                sentiments.append(sentiment['compound'])
                
                # Calculate engagement
                metrics = tweet.public_metrics
                engagement = (
                    metrics['like_count'] * 1 +
                    metrics['retweet_count'] * 2 +
                    metrics['reply_count'] * 0.5 +
                    metrics['quote_count'] * 1.5
                )
                total_engagement += engagement
            
            # Track velocity
            self.mention_history[ticker].append({
                'timestamp': datetime.now(),
                'mentions': mentions
            })
            
            velocity = self._calculate_velocity(ticker)
            
            return SocialSignal(
                ticker=ticker,
                source='twitter',
                timestamp=datetime.now(),
                mentions=mentions,
                sentiment=np.mean(sentiments) if sentiments else 0,
                engagement=total_engagement,
                author_influence=velocity  # Using velocity as proxy for now
            )
            
        except Exception as e:
            print(f"Error searching Twitter for {ticker}: {e}")
            return None
    
    def _calculate_velocity(self, ticker: str) -> float:
        """Calculate mention velocity (acceleration of mentions)"""
        history = self.mention_history[ticker]
        
        if len(history) < 2:
            return 0.0
        
        # Get mentions from last hour vs previous hour
        now = datetime.now()
        hour_ago = now - timedelta(hours=1)
        two_hours_ago = now - timedelta(hours=2)
        
        recent_mentions = sum(
            h['mentions'] for h in history 
            if h['timestamp'] > hour_ago
        )
        
        previous_mentions = sum(
            h['mentions'] for h in history 
            if two_hours_ago < h['timestamp'] <= hour_ago
        )
        
        if previous_mentions == 0:
            return recent_mentions  # All new mentions
        
        return (recent_mentions - previous_mentions) / previous_mentions * 100
    
    async def monitor_influencers(self, influencer_handles: List[str], 
                                 lookback_hours: int = 24) -> Dict[str, List[str]]:
        """Monitor influential accounts for ticker mentions"""
        ticker_mentions = defaultdict(list)
        
        for handle in influencer_handles:
            try:
                # Get user ID
                user = self.client.get_user(username=handle)
                if not user.data:
                    continue
                    
                user_id = user.data.id
                
                # Get recent tweets
                tweets = self.client.get_users_tweets(
                    user_id,
                    max_results=50,
                    tweet_fields=['created_at'],
                    exclude=['retweets', 'replies']
                )
                
                if tweets.data:
                    for tweet in tweets.data:
                        # Extract ticker symbols
                        tickers = self.ticker_pattern.findall(tweet.text)
                        for ticker in tickers:
                            ticker = ticker.replace('$', '')
                            ticker_mentions[ticker].append(handle)
                            
            except Exception as e:
                print(f"Error monitoring @{handle}: {e}")
                continue
        
        return dict(ticker_mentions)
    
    async def get_trending_tickers(self, limit: int = 20) -> List[Tuple[str, int]]:
        """Get currently trending stock tickers"""
        query = "($TSLA OR $AAPL OR $GME OR $AMC OR $SPY) -is:retweet lang:en"
        
        try:
            tweets = self.client.search_recent_tweets(
                query=query,
                max_results=100,
                tweet_fields=['created_at']
            )
            
            ticker_counts = Counter()
            
            if tweets.data:
                for tweet in tweets.data:
                    tickers = self.ticker_pattern.findall(tweet.text)
                    for ticker in tickers:
                        ticker = ticker.replace('$', '')
                        ticker_counts[ticker] += 1
            
            return ticker_counts.most_common(limit)
            
        except Exception as e:
            print(f"Error getting trending tickers: {e}")
            return []


class SocialMediaAggregator:
    """
    Master aggregator - combines all social signals into actionable intelligence
    """
    
    def __init__(self, reddit_scanner: Optional[RedditScanner] = None,
                 twitter_scanner: Optional[TwitterScanner] = None):
        self.reddit_scanner = reddit_scanner
        self.twitter_scanner = twitter_scanner
        self.signal_cache = {}
        self.last_scan = {}
        
    async def get_combined_signals(self, tickers: List[str]) -> Dict[str, Dict]:
        """Get combined social signals for multiple tickers"""
        combined_signals = {}
        
        for ticker in tickers:
            signals = {
                'ticker': ticker,
                'timestamp': datetime.now(),
                'reddit': None,
                'twitter': None,
                'combined_score': 0,
                'alert_level': 'LOW'
            }
            
            # Get Reddit signals
            if self.reddit_scanner:
                reddit_signals = await self.reddit_scanner.scan_all_subreddits(
                    ['wallstreetbets', 'stocks', 'pennystocks']
                )
                if ticker in reddit_signals:
                    signals['reddit'] = reddit_signals[ticker]
            
            # Get Twitter signals
            if self.twitter_scanner:
                twitter_signal = await self.twitter_scanner.search_ticker(ticker)
                if twitter_signal:
                    signals['twitter'] = twitter_signal
            
            # Calculate combined score
            score = 0
            if signals['reddit']:
                score += signals['reddit'].mentions * 2
                score += signals['reddit'].sentiment * 50
                
            if signals['twitter']:
                score += signals['twitter'].mentions
                score += signals['twitter'].author_influence
            
            signals['combined_score'] = score
            
            # Determine alert level
            if score > 500:
                signals['alert_level'] = 'EXTREME'
            elif score > 200:
                signals['alert_level'] = 'HIGH'
            elif score > 100:
                signals['alert_level'] = 'MEDIUM'
            else:
                signals['alert_level'] = 'LOW'
            
            combined_signals[ticker] = signals
        
        return combined_signals
    
    def get_momentum_changes(self, lookback_hours: int = 24) -> Dict[str, float]:
        """Identify stocks with rapidly increasing social momentum"""
        # This would track historical data and calculate rate of change
        # Placeholder for now
        return {}
    
    async def continuous_scan(self, tickers: List[str], 
                            interval_seconds: int = 300):
        """Continuously scan for signals"""
        while True:
            try:
                print(f"Starting social scan at {datetime.now()}")
                signals = await self.get_combined_signals(tickers)
                
                # Alert on high-priority signals
                for ticker, signal in signals.items():
                    if signal['alert_level'] in ['HIGH', 'EXTREME']:
                        print(f"🚨 ALERT: {ticker} showing {signal['alert_level']} social activity!")
                        print(f"   Score: {signal['combined_score']}")
                        if signal['reddit']:
                            print(f"   Reddit: {signal['reddit'].mentions} mentions, "
                                  f"sentiment: {signal['reddit'].sentiment:.2f}")
                        if signal['twitter']:
                            print(f"   Twitter: {signal['twitter'].mentions} mentions, "
                                  f"velocity: {signal['twitter'].author_influence:.1f}%")
                
                # Cache results
                self.signal_cache = signals
                self.last_scan[datetime.now()] = signals
                
                # Wait for next scan
                await asyncio.sleep(interval_seconds)
                
            except Exception as e:
                print(f"Error in continuous scan: {e}")
                await asyncio.sleep(60)  # Wait a minute on error