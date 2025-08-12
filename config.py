"""
Meme Stock Scanner Configuration
Where we define the parameters that separate tendies from losses
"""
import os
from dataclasses import dataclass, field
from typing import List, Dict, Any
from datetime import timedelta

def default_reddit_subreddits():
    return [
        'wallstreetbets',
        'stocks',
        'StockMarket',
        'pennystocks',
        'Superstonk',
        'options',
        'thetagang',
        'ValueInvesting',
        'SPACs',
        'Shortsqueeze'
    ]

def default_twitter_influencers():
    return [
        'Mr_Derivatives',
        'unusual_whales',
        'DeItaone',
        'zerohedge',
        'FirstSquawk',
        'LiveSquawk',
        'OptionsHawk',
        'TruthGundlach',
        'jimcramer',  # Inverse indicator
        'MarketRebels'
    ]

def default_meme_weights():
    return {
        'reddit_mentions': 0.15,
        'reddit_sentiment': 0.10,
        'twitter_velocity': 0.15,
        'influencer_score': 0.10,
        'short_interest': 0.15,
        'options_flow': 0.10,
        'price_momentum': 0.10,
        'volume_spike': 0.10,
        'retail_interest': 0.05
    }

def default_watchlist():
    return [
        'DNUT',  # Krispy Kreme - diabetes play
        'KSS',   # Kohl's - retail resurrection 
        'GPRO',  # GoPro - action cam comeback
        'GME',   # The OG meme
        'AMC',   # Movie stock classic
        'BBBY',  # Bed Bath & Beyond zombie
        'BB',    # BlackBerry pivot play
        'NOK',   # Nokia 5G dreams
        'PLTR',  # Palantir cult following
        'SOFI',  # Fintech disruptor
    ]

@dataclass
class ScannerConfig:
    """Core configuration for the meme scanner"""
    
    # API Keys (load from environment)
    REDDIT_CLIENT_ID: str = os.getenv('REDDIT_CLIENT_ID', '')
    REDDIT_CLIENT_SECRET: str = os.getenv('REDDIT_CLIENT_SECRET', '')
    REDDIT_USER_AGENT: str = 'MemeStockScanner/1.0'
    
    TWITTER_API_KEY: str = os.getenv('TWITTER_API_KEY', '')
    TWITTER_API_SECRET: str = os.getenv('TWITTER_API_SECRET', '')
    TWITTER_ACCESS_TOKEN: str = os.getenv('TWITTER_ACCESS_TOKEN', '')
    TWITTER_ACCESS_SECRET: str = os.getenv('TWITTER_ACCESS_SECRET', '')
    
    # Reddit Monitoring
    REDDIT_SUBREDDITS: List[str] = field(default_factory=default_reddit_subreddits)
    
    # Twitter/X Monitoring
    TWITTER_INFLUENCERS: List[str] = field(default_factory=default_twitter_influencers)
    
    # Meme Score Weights
    MEME_WEIGHTS: Dict[str, float] = field(default_factory=default_meme_weights)
    
    # Technical Thresholds
    VOLUME_SPIKE_THRESHOLD: float = 3.0  # 3x average volume
    RSI_OVERSOLD: float = 30.0
    RSI_OVERBOUGHT: float = 70.0
    SHORT_SQUEEZE_THRESHOLD: float = 20.0  # % short interest
    
    # Sentiment Thresholds
    BULLISH_SENTIMENT_THRESHOLD: float = 0.6
    BEARISH_SENTIMENT_THRESHOLD: float = -0.6
    MENTION_SPIKE_THRESHOLD: float = 5.0  # 5x normal mentions
    
    # Risk Management
    MAX_POSITION_SIZE: float = 0.05  # 5% of portfolio
    STOP_LOSS_PERCENT: float = 0.08  # 8% stop loss
    TAKE_PROFIT_PERCENT: float = 0.25  # 25% take profit
    
    # Scanning Parameters
    SCAN_INTERVAL_SECONDS: int = 60  # Check every minute
    CACHE_EXPIRY_SECONDS: int = 300  # 5 minute cache
    MAX_CONCURRENT_REQUESTS: int = 10
    
    # Alert Thresholds
    MEME_SCORE_ALERT: float = 70.0  # Alert when score > 70
    VOLUME_ALERT_MULTIPLIER: float = 5.0  # Alert on 5x volume
    
    # Database
    DATABASE_URL: str = os.getenv('DATABASE_URL', 'sqlite:///meme_scanner.db')
    REDIS_URL: str = os.getenv('REDIS_URL', 'redis://localhost:6379')
    
    # Watchlist Tickers (your targets)
    INITIAL_WATCHLIST: List[str] = field(default_factory=default_watchlist)
    
    # Feature Flags
    ENABLE_REDDIT_SCANNING: bool = True
    ENABLE_TWITTER_SCANNING: bool = True
    ENABLE_OPTIONS_FLOW: bool = True
    ENABLE_DARK_POOL_MONITORING: bool = True
    ENABLE_REAL_TIME_ALERTS: bool = True
    
    # Backtesting
    BACKTEST_START_DATE: str = '2021-01-01'
    BACKTEST_END_DATE: str = '2024-01-01'
    
    def validate(self) -> bool:
        """Validate configuration"""
        if not self.REDDIT_CLIENT_ID and self.ENABLE_REDDIT_SCANNING:
            print("Warning: Reddit API credentials not configured")
            return False
        if not self.TWITTER_API_KEY and self.ENABLE_TWITTER_SCANNING:
            print("Warning: Twitter API credentials not configured")
            return False
        return True

# Global config instance
config = ScannerConfig()