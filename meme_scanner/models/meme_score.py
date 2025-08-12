"""
Meme Score Calculator - The Secret Sauce
This is where we turn chaos into alpha
"""
import numpy as np
from dataclasses import dataclass
from typing import Dict, Optional, List
from datetime import datetime, timedelta
import pandas as pd

@dataclass
class MemeMetrics:
    """All the signals that matter for meme stocks"""
    ticker: str
    timestamp: datetime
    
    # Social Metrics
    reddit_mentions_24h: int = 0
    reddit_mentions_delta: float = 0.0  # % change from baseline
    reddit_sentiment: float = 0.0  # -1 to 1
    reddit_upvote_ratio: float = 0.0
    
    twitter_mentions_24h: int = 0
    twitter_velocity: float = 0.0  # mentions per hour acceleration
    twitter_sentiment: float = 0.0
    influencer_mentions: int = 0
    
    # Market Metrics
    price: float = 0.0
    price_change_24h: float = 0.0
    volume: int = 0
    volume_ratio: float = 0.0  # current vs 20-day average
    market_cap: float = 0.0
    
    # Technical Indicators
    rsi: float = 50.0
    macd_signal: float = 0.0
    bollinger_position: float = 0.0  # -1 (below lower) to 1 (above upper)
    
    # Short Interest Data
    short_interest: float = 0.0
    days_to_cover: float = 0.0
    borrow_rate: float = 0.0
    
    # Options Flow
    options_volume: int = 0
    put_call_ratio: float = 1.0
    gamma_exposure: float = 0.0
    unusual_options_activity: bool = False
    
    # Retail Interest
    robinhood_holders: int = 0
    robinhood_holder_change: float = 0.0
    google_trends_score: float = 0.0
    
    # Risk Metrics
    iv_rank: float = 0.0  # Implied volatility rank
    beta: float = 1.0
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for storage/analysis"""
        return {
            'ticker': self.ticker,
            'timestamp': self.timestamp.isoformat(),
            'reddit_mentions_24h': self.reddit_mentions_24h,
            'reddit_sentiment': self.reddit_sentiment,
            'twitter_mentions_24h': self.twitter_mentions_24h,
            'twitter_velocity': self.twitter_velocity,
            'price': self.price,
            'volume_ratio': self.volume_ratio,
            'short_interest': self.short_interest,
            'options_volume': self.options_volume,
            'put_call_ratio': self.put_call_ratio,
        }


class MemeScoreCalculator:
    """
    The brain of the operation - calculates meme potential
    Higher score = Higher degeneracy = Higher potential returns
    """
    
    def __init__(self, weights: Optional[Dict[str, float]] = None):
        """Initialize with custom weights or use defaults"""
        self.weights = weights or {
            'social_momentum': 0.25,
            'short_squeeze_potential': 0.20,
            'options_activity': 0.15,
            'technical_setup': 0.15,
            'volume_surge': 0.15,
            'retail_fomo': 0.10
        }
        
    def calculate_score(self, metrics: MemeMetrics) -> Dict[str, float]:
        """
        Calculate the ultimate meme score
        Returns score (0-100) and component breakdowns
        """
        components = {}
        
        # 1. Social Momentum Score (0-100)
        social_score = self._calculate_social_momentum(metrics)
        components['social_momentum'] = social_score
        
        # 2. Short Squeeze Potential (0-100)
        squeeze_score = self._calculate_squeeze_potential(metrics)
        components['short_squeeze_potential'] = squeeze_score
        
        # 3. Options Activity Score (0-100)
        options_score = self._calculate_options_activity(metrics)
        components['options_activity'] = options_score
        
        # 4. Technical Setup Score (0-100)
        technical_score = self._calculate_technical_setup(metrics)
        components['technical_setup'] = technical_score
        
        # 5. Volume Surge Score (0-100)
        volume_score = self._calculate_volume_surge(metrics)
        components['volume_surge'] = volume_score
        
        # 6. Retail FOMO Score (0-100)
        fomo_score = self._calculate_retail_fomo(metrics)
        components['retail_fomo'] = fomo_score
        
        # Calculate weighted total
        total_score = sum(
            components[key] * self.weights.get(key, 0)
            for key in components
        )
        
        return {
            'total_score': min(100, total_score),
            'components': components,
            'signal': self._get_signal(total_score),
            'confidence': self._calculate_confidence(components)
        }
    
    def _calculate_social_momentum(self, m: MemeMetrics) -> float:
        """Calculate social media momentum score"""
        score = 0.0
        
        # Reddit mentions (0-40 points)
        if m.reddit_mentions_delta > 10:  # 10x increase
            score += 40
        elif m.reddit_mentions_delta > 5:  # 5x increase
            score += 30
        elif m.reddit_mentions_delta > 2:  # 2x increase
            score += 20
        elif m.reddit_mentions_delta > 1:  # Some increase
            score += 10
            
        # Reddit sentiment (0-20 points)
        sentiment_score = (m.reddit_sentiment + 1) * 10  # Convert -1,1 to 0,20
        score += sentiment_score
        
        # Twitter velocity (0-30 points)
        if m.twitter_velocity > 100:  # Extreme acceleration
            score += 30
        elif m.twitter_velocity > 50:
            score += 20
        elif m.twitter_velocity > 20:
            score += 10
            
        # Influencer boost (0-10 points)
        if m.influencer_mentions > 5:
            score += 10
        elif m.influencer_mentions > 2:
            score += 5
            
        return min(100, score)
    
    def _calculate_squeeze_potential(self, m: MemeMetrics) -> float:
        """Calculate short squeeze potential"""
        score = 0.0
        
        # Short interest (0-40 points)
        if m.short_interest > 30:  # Extreme short interest
            score += 40
        elif m.short_interest > 20:
            score += 30
        elif m.short_interest > 15:
            score += 20
        elif m.short_interest > 10:
            score += 10
            
        # Days to cover (0-30 points)
        if m.days_to_cover > 5:
            score += 30
        elif m.days_to_cover > 3:
            score += 20
        elif m.days_to_cover > 2:
            score += 10
            
        # Borrow rate (0-30 points)
        if m.borrow_rate > 50:  # Very expensive to borrow
            score += 30
        elif m.borrow_rate > 20:
            score += 20
        elif m.borrow_rate > 10:
            score += 10
            
        return min(100, score)
    
    def _calculate_options_activity(self, m: MemeMetrics) -> float:
        """Calculate options activity score"""
        score = 0.0
        
        # Unusual options activity (0-40 points)
        if m.unusual_options_activity:
            score += 40
            
        # Put/Call ratio (0-30 points)
        if m.put_call_ratio < 0.5:  # Heavily bullish
            score += 30
        elif m.put_call_ratio < 0.7:
            score += 20
        elif m.put_call_ratio < 1.0:
            score += 10
            
        # Gamma exposure (0-30 points)
        if abs(m.gamma_exposure) > 1000000:  # High gamma
            score += 30
        elif abs(m.gamma_exposure) > 500000:
            score += 20
        elif abs(m.gamma_exposure) > 100000:
            score += 10
            
        return min(100, score)
    
    def _calculate_technical_setup(self, m: MemeMetrics) -> float:
        """Calculate technical analysis score"""
        score = 0.0
        
        # RSI setup (0-35 points)
        if m.rsi < 30:  # Oversold bounce play
            score += 35
        elif m.rsi > 70 and m.price_change_24h > 5:  # Momentum continuation
            score += 25
        elif 40 < m.rsi < 60:  # Neutral zone building
            score += 15
            
        # Bollinger Bands (0-35 points)
        if m.bollinger_position < -0.9:  # Way oversold
            score += 35
        elif m.bollinger_position > 0.9 and m.volume_ratio > 2:  # Breakout
            score += 30
        elif abs(m.bollinger_position) > 0.5:
            score += 15
            
        # MACD momentum (0-30 points)
        if m.macd_signal > 0 and m.price_change_24h > 0:
            score += 30
        elif m.macd_signal > 0:
            score += 15
            
        return min(100, score)
    
    def _calculate_volume_surge(self, m: MemeMetrics) -> float:
        """Calculate volume surge score"""
        if m.volume_ratio > 10:
            return 100
        elif m.volume_ratio > 5:
            return 80
        elif m.volume_ratio > 3:
            return 60
        elif m.volume_ratio > 2:
            return 40
        elif m.volume_ratio > 1.5:
            return 20
        return 0
    
    def _calculate_retail_fomo(self, m: MemeMetrics) -> float:
        """Calculate retail FOMO score"""
        score = 0.0
        
        # Robinhood holders change (0-40 points)
        if m.robinhood_holder_change > 50:
            score += 40
        elif m.robinhood_holder_change > 20:
            score += 25
        elif m.robinhood_holder_change > 10:
            score += 15
            
        # Google trends (0-30 points)
        if m.google_trends_score > 80:
            score += 30
        elif m.google_trends_score > 50:
            score += 20
        elif m.google_trends_score > 25:
            score += 10
            
        # Price action creating FOMO (0-30 points)
        if m.price_change_24h > 20:
            score += 30
        elif m.price_change_24h > 10:
            score += 20
        elif m.price_change_24h > 5:
            score += 10
            
        return min(100, score)
    
    def _get_signal(self, score: float) -> str:
        """Convert score to trading signal"""
        if score >= 80:
            return "STRONG_BUY"
        elif score >= 65:
            return "BUY"
        elif score >= 50:
            return "WATCH"
        elif score >= 35:
            return "NEUTRAL"
        else:
            return "AVOID"
    
    def _calculate_confidence(self, components: Dict[str, float]) -> float:
        """Calculate confidence in the signal based on component agreement"""
        scores = list(components.values())
        
        # High confidence if components agree
        std_dev = np.std(scores)
        mean_score = np.mean(scores)
        
        if std_dev < 15 and mean_score > 60:
            return 0.9  # High confidence - strong agreement
        elif std_dev < 20 and mean_score > 50:
            return 0.7  # Good confidence
        elif std_dev < 30:
            return 0.5  # Moderate confidence
        else:
            return 0.3  # Low confidence - mixed signals
    
    def rank_opportunities(self, metrics_list: List[MemeMetrics]) -> pd.DataFrame:
        """Rank multiple opportunities by score"""
        results = []
        
        for metrics in metrics_list:
            score_data = self.calculate_score(metrics)
            results.append({
                'ticker': metrics.ticker,
                'total_score': score_data['total_score'],
                'signal': score_data['signal'],
                'confidence': score_data['confidence'],
                'price': metrics.price,
                'volume_ratio': metrics.volume_ratio,
                'short_interest': metrics.short_interest,
                **score_data['components']
            })
        
        df = pd.DataFrame(results)
        return df.sort_values('total_score', ascending=False)