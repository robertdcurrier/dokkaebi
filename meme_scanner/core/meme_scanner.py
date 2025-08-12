"""
Main Meme Scanner Engine - The Command Center
This is where we orchestrate the chaos into profitable signals
"""
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import pandas as pd
import yfinance as yf
import numpy as np
from dataclasses import dataclass
import json
import pickle
from pathlib import Path

from ..models.meme_score import MemeMetrics, MemeScoreCalculator
from .social_scanner import SocialMediaAggregator, RedditScanner, TwitterScanner
from ..data.market_data import MarketDataFetcher
from ..utils.alerts import AlertManager
from config import ScannerConfig


class MemeStockScanner:
    """
    The Master Scanner - Combines all signals into trading opportunities
    This is where tendies are born
    """
    
    def __init__(self, config: ScannerConfig):
        """Initialize the scanner with configuration"""
        self.config = config
        self.score_calculator = MemeScoreCalculator(config.MEME_WEIGHTS)
        
        # Initialize social scanners if credentials available
        self.social_aggregator = self._init_social_scanners()
        
        # Market data fetcher
        self.market_data = MarketDataFetcher()
        
        # Alert manager
        self.alert_manager = AlertManager()
        
        # Cache for efficiency
        self.cache = {}
        self.last_scan_time = {}
        
        # Results storage
        self.scan_history = []
        self.top_picks = []
        
    def _init_social_scanners(self) -> Optional[SocialMediaAggregator]:
        """Initialize social media scanners if credentials available"""
        reddit_scanner = None
        twitter_scanner = None
        
        if self.config.REDDIT_CLIENT_ID and self.config.ENABLE_REDDIT_SCANNING:
            try:
                reddit_scanner = RedditScanner(
                    self.config.REDDIT_CLIENT_ID,
                    self.config.REDDIT_CLIENT_SECRET,
                    self.config.REDDIT_USER_AGENT
                )
                print("✅ Reddit scanner initialized")
            except Exception as e:
                print(f"❌ Failed to initialize Reddit scanner: {e}")
        
        if self.config.TWITTER_API_KEY and self.config.ENABLE_TWITTER_SCANNING:
            try:
                twitter_scanner = TwitterScanner(
                    self.config.TWITTER_API_KEY,
                    self.config.TWITTER_API_SECRET,
                    self.config.TWITTER_ACCESS_TOKEN,
                    self.config.TWITTER_ACCESS_SECRET
                )
                print("✅ Twitter scanner initialized")
            except Exception as e:
                print(f"❌ Failed to initialize Twitter scanner: {e}")
        
        if reddit_scanner or twitter_scanner:
            return SocialMediaAggregator(reddit_scanner, twitter_scanner)
        return None
    
    async def scan_ticker(self, ticker: str) -> Dict:
        """
        Perform complete scan of a single ticker
        Returns comprehensive analysis and score
        """
        print(f"\n🔍 Scanning {ticker}...")
        
        # Gather all metrics
        metrics = await self._gather_metrics(ticker)
        
        if not metrics:
            return {'ticker': ticker, 'error': 'Failed to gather metrics'}
        
        # Calculate meme score
        score_data = self.score_calculator.calculate_score(metrics)
        
        # Prepare comprehensive result
        result = {
            'ticker': ticker,
            'timestamp': datetime.now().isoformat(),
            'score': score_data['total_score'],
            'signal': score_data['signal'],
            'confidence': score_data['confidence'],
            'components': score_data['components'],
            'metrics': {
                'price': metrics.price,
                'price_change_24h': metrics.price_change_24h,
                'volume_ratio': metrics.volume_ratio,
                'short_interest': metrics.short_interest,
                'reddit_mentions': metrics.reddit_mentions_24h,
                'reddit_sentiment': metrics.reddit_sentiment,
                'twitter_velocity': metrics.twitter_velocity,
                'rsi': metrics.rsi,
                'options_volume': metrics.options_volume,
                'put_call_ratio': metrics.put_call_ratio
            },
            'analysis': self._generate_analysis(metrics, score_data)
        }
        
        # Check for alerts
        if score_data['total_score'] >= self.config.MEME_SCORE_ALERT:
            self.alert_manager.send_alert(
                f"🚨 HIGH MEME SCORE: {ticker} scored {score_data['total_score']:.1f}! "
                f"Signal: {score_data['signal']}"
            )
        
        return result
    
    async def _gather_metrics(self, ticker: str) -> Optional[MemeMetrics]:
        """Gather all metrics for a ticker"""
        try:
            metrics = MemeMetrics(
                ticker=ticker,
                timestamp=datetime.now()
            )
            
            # Get market data
            market_data = self.market_data.get_ticker_data(ticker)
            if market_data:
                metrics.price = market_data.get('price', 0)
                metrics.price_change_24h = market_data.get('change_percent', 0)
                metrics.volume = market_data.get('volume', 0)
                metrics.volume_ratio = market_data.get('volume_ratio', 0)
                metrics.market_cap = market_data.get('market_cap', 0)
                
                # Technical indicators
                metrics.rsi = market_data.get('rsi', 50)
                metrics.macd_signal = market_data.get('macd_signal', 0)
                metrics.bollinger_position = market_data.get('bollinger_position', 0)
                
                # Short interest (would need real data source)
                metrics.short_interest = market_data.get('short_interest', 0)
                metrics.days_to_cover = market_data.get('days_to_cover', 0)
            
            # Get social signals if available
            if self.social_aggregator:
                social_signals = await self.social_aggregator.get_combined_signals([ticker])
                if ticker in social_signals:
                    signal = social_signals[ticker]
                    
                    if signal.get('reddit'):
                        metrics.reddit_mentions_24h = signal['reddit'].mentions
                        metrics.reddit_sentiment = signal['reddit'].sentiment
                        
                    if signal.get('twitter'):
                        metrics.twitter_mentions_24h = signal['twitter'].mentions
                        metrics.twitter_velocity = signal['twitter'].author_influence
            
            # Options flow (placeholder - would need real options data)
            metrics.options_volume = np.random.randint(1000, 50000)
            metrics.put_call_ratio = np.random.uniform(0.3, 1.5)
            metrics.unusual_options_activity = np.random.random() > 0.7
            
            return metrics
            
        except Exception as e:
            print(f"Error gathering metrics for {ticker}: {e}")
            return None
    
    def _generate_analysis(self, metrics: MemeMetrics, score_data: Dict) -> Dict:
        """Generate human-readable analysis"""
        analysis = {
            'summary': '',
            'bullish_factors': [],
            'bearish_factors': [],
            'key_levels': {},
            'recommendation': ''
        }
        
        # Determine overall sentiment
        if score_data['total_score'] >= 70:
            analysis['summary'] = f"🔥 STRONG MEME POTENTIAL - Multiple bullish catalysts aligning"
        elif score_data['total_score'] >= 50:
            analysis['summary'] = f"📈 MODERATE INTEREST - Some positive signals emerging"
        else:
            analysis['summary'] = f"💤 LOW ACTIVITY - Limited meme potential currently"
        
        # Bullish factors
        if metrics.reddit_mentions_delta > 5:
            analysis['bullish_factors'].append(
                f"Reddit mentions surging {metrics.reddit_mentions_delta:.1f}x normal"
            )
        if metrics.short_interest > 20:
            analysis['bullish_factors'].append(
                f"High short interest ({metrics.short_interest:.1f}%) - squeeze potential"
            )
        if metrics.volume_ratio > 3:
            analysis['bullish_factors'].append(
                f"Volume spike {metrics.volume_ratio:.1f}x average"
            )
        if metrics.rsi < 30:
            analysis['bullish_factors'].append("Oversold RSI - bounce potential")
        
        # Bearish factors
        if metrics.reddit_sentiment < -0.3:
            analysis['bearish_factors'].append("Negative social sentiment")
        if metrics.put_call_ratio > 1.5:
            analysis['bearish_factors'].append("Heavy put buying in options")
        if metrics.rsi > 70 and metrics.price_change_24h < 0:
            analysis['bearish_factors'].append("Overbought and losing momentum")
        
        # Key levels
        analysis['key_levels'] = {
            'entry': metrics.price * 0.98,  # 2% below current
            'stop_loss': metrics.price * 0.92,  # 8% stop
            'target_1': metrics.price * 1.15,  # 15% gain
            'target_2': metrics.price * 1.30,  # 30% gain
            'moon': metrics.price * 2.0  # 100% gain for the degenerates
        }
        
        # Recommendation based on score
        if score_data['signal'] == 'STRONG_BUY':
            analysis['recommendation'] = (
                f"YOLO ZONE - Strong meme momentum building. "
                f"Consider entry near ${analysis['key_levels']['entry']:.2f} "
                f"with stop at ${analysis['key_levels']['stop_loss']:.2f}. "
                f"First target ${analysis['key_levels']['target_1']:.2f}"
            )
        elif score_data['signal'] == 'BUY':
            analysis['recommendation'] = (
                f"ACCUMULATE - Positive signals emerging. "
                f"Scale in with 50% position, add on dips"
            )
        elif score_data['signal'] == 'WATCH':
            analysis['recommendation'] = (
                f"MONITOR - Not quite there yet. Wait for catalyst or better entry"
            )
        else:
            analysis['recommendation'] = (
                f"AVOID - No clear meme potential. Look elsewhere for tendies"
            )
        
        return analysis
    
    async def scan_watchlist(self, tickers: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Scan entire watchlist and rank opportunities
        """
        tickers = tickers or self.config.INITIAL_WATCHLIST
        
        print(f"\n{'='*60}")
        print(f"🚀 MEME SCANNER ACTIVATED - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Scanning {len(tickers)} tickers...")
        print(f"{'='*60}")
        
        results = []
        metrics_list = []
        
        for ticker in tickers:
            result = await self.scan_ticker(ticker)
            results.append(result)
            
            # Collect metrics for ranking
            if 'error' not in result:
                metrics = await self._gather_metrics(ticker)
                if metrics:
                    metrics_list.append(metrics)
        
        # Rank opportunities
        if metrics_list:
            rankings = self.score_calculator.rank_opportunities(metrics_list)
            
            # Display top picks
            print(f"\n{'='*60}")
            print("🏆 TOP MEME PICKS")
            print(f"{'='*60}")
            
            for idx, row in rankings.head(5).iterrows():
                print(f"\n#{idx+1} {row['ticker']} - Score: {row['total_score']:.1f}")
                print(f"   Signal: {row['signal']} | Confidence: {row['confidence']:.1%}")
                print(f"   Price: ${row['price']:.2f} | Volume: {row['volume_ratio']:.1f}x")
                print(f"   Short Interest: {row['short_interest']:.1f}%")
            
            # Store results
            self.scan_history.append({
                'timestamp': datetime.now(),
                'results': results,
                'rankings': rankings
            })
            
            self.top_picks = rankings.head(5).to_dict('records')
            
            return rankings
        
        return pd.DataFrame()
    
    async def continuous_monitoring(self, 
                                  tickers: Optional[List[str]] = None,
                                  interval_minutes: int = 5):
        """
        Continuously monitor watchlist for opportunities
        """
        tickers = tickers or self.config.INITIAL_WATCHLIST
        interval_seconds = interval_minutes * 60
        
        print(f"\n🤖 Starting continuous monitoring...")
        print(f"Watching {len(tickers)} tickers")
        print(f"Scan interval: {interval_minutes} minutes")
        print(f"Alert threshold: {self.config.MEME_SCORE_ALERT}")
        print("\nPress Ctrl+C to stop...\n")
        
        while True:
            try:
                # Run scan
                rankings = await self.scan_watchlist(tickers)
                
                # Check for extreme opportunities
                extreme_picks = rankings[rankings['total_score'] >= 80]
                if not extreme_picks.empty:
                    print("\n🚨🚨🚨 EXTREME MEME ALERT 🚨🚨🚨")
                    for _, pick in extreme_picks.iterrows():
                        print(f"   {pick['ticker']}: Score {pick['total_score']:.1f}")
                
                # Save state
                self.save_state()
                
                # Wait for next scan
                await asyncio.sleep(interval_seconds)
                
            except KeyboardInterrupt:
                print("\n✋ Monitoring stopped by user")
                break
            except Exception as e:
                print(f"Error in monitoring: {e}")
                await asyncio.sleep(60)  # Wait a minute on error
    
    def save_state(self, filepath: str = 'scanner_state.pkl'):
        """Save scanner state to disk"""
        state = {
            'scan_history': self.scan_history[-100:],  # Keep last 100 scans
            'top_picks': self.top_picks,
            'last_save': datetime.now()
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(state, f)
    
    def load_state(self, filepath: str = 'scanner_state.pkl'):
        """Load scanner state from disk"""
        if Path(filepath).exists():
            with open(filepath, 'rb') as f:
                state = pickle.load(f)
                self.scan_history = state.get('scan_history', [])
                self.top_picks = state.get('top_picks', [])
                print(f"Loaded state from {state.get('last_save')}")
    
    def get_historical_performance(self, ticker: str, days: int = 30) -> Dict:
        """Analyze historical performance of scanner predictions"""
        # This would track actual performance vs predictions
        # Placeholder for backtesting functionality
        return {
            'ticker': ticker,
            'predictions_made': 0,
            'successful_predictions': 0,
            'average_return': 0.0,
            'best_call': None,
            'worst_call': None
        }