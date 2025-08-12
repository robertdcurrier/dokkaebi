#!/usr/bin/env python3
"""
Simple test of the meme scanner components
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime
import numpy as np
from meme_scanner.models.meme_score import MemeMetrics, MemeScoreCalculator

def test_meme_scoring():
    """Test the meme scoring system"""
    print("🚀 MEME SCANNER TEST - SCORING ENGINE")
    print("="*60)
    
    # Create test metrics for DNUT
    metrics = MemeMetrics(
        ticker="DNUT",
        timestamp=datetime.now(),
        # Social metrics
        reddit_mentions_24h=150,
        reddit_mentions_delta=5.2,  # 5.2x increase
        reddit_sentiment=0.65,
        reddit_upvote_ratio=0.88,
        twitter_mentions_24h=320,
        twitter_velocity=75.0,  # 75% acceleration
        twitter_sentiment=0.55,
        influencer_mentions=3,
        # Market metrics
        price=15.25,
        price_change_24h=8.5,  # 8.5% gain
        volume=5_000_000,
        volume_ratio=4.2,  # 4.2x average
        market_cap=2_500_000_000,
        # Technical
        rsi=38,  # Oversold territory
        macd_signal=0.15,
        bollinger_position=-0.7,  # Near lower band
        # Short data
        short_interest=22.5,  # High short interest
        days_to_cover=3.8,
        borrow_rate=35.0,
        # Options
        options_volume=25000,
        put_call_ratio=0.45,  # Bullish
        gamma_exposure=750000,
        unusual_options_activity=True,
        # Retail
        robinhood_holders=50000,
        robinhood_holder_change=25.0,
        google_trends_score=65
    )
    
    # Calculate score
    calculator = MemeScoreCalculator()
    result = calculator.calculate_score(metrics)
    
    # Display results
    print(f"\nTicker: {metrics.ticker}")
    print(f"Price: ${metrics.price:.2f} ({metrics.price_change_24h:+.1f}%)")
    print(f"Volume: {metrics.volume_ratio:.1f}x average")
    print(f"\n📊 MEME SCORE: {result['total_score']:.1f}/100")
    print(f"📈 Signal: {result['signal']}")
    print(f"🎯 Confidence: {result['confidence']:.1%}")
    
    print("\n📋 Component Breakdown:")
    for component, score in result['components'].items():
        bar = "█" * int(score/5) + "░" * (20 - int(score/5))
        print(f"  {component:25s} [{bar}] {score:.1f}")
    
    # Test with multiple tickers
    print("\n" + "="*60)
    print("🏆 RANKING MULTIPLE OPPORTUNITIES")
    print("="*60)
    
    test_tickers = [
        ("DNUT", 5.2, 22.5, 4.2, 38),
        ("KSS", 2.1, 15.0, 2.5, 45),
        ("GPRO", 8.5, 28.0, 6.1, 25),
        ("GME", 3.0, 18.5, 3.8, 55),
        ("AMC", 1.5, 12.0, 1.8, 62)
    ]
    
    metrics_list = []
    for ticker, reddit_delta, short_int, vol_ratio, rsi in test_tickers:
        m = MemeMetrics(
            ticker=ticker,
            timestamp=datetime.now(),
            reddit_mentions_delta=reddit_delta,
            short_interest=short_int,
            volume_ratio=vol_ratio,
            rsi=rsi,
            price=np.random.uniform(5, 50),
            twitter_velocity=np.random.uniform(10, 100),
            put_call_ratio=np.random.uniform(0.3, 1.5),
            unusual_options_activity=np.random.random() > 0.5
        )
        metrics_list.append(m)
    
    # Rank opportunities
    rankings = calculator.rank_opportunities(metrics_list)
    
    print("\nTop Meme Opportunities:")
    print(rankings[['ticker', 'total_score', 'signal', 'confidence', 
                   'short_interest', 'volume_ratio']].to_string(index=False))
    
    print("\n✅ Test completed successfully!")
    
    # Test analysis generation
    print("\n" + "="*60)
    print("💡 ANALYSIS GENERATION TEST")
    print("="*60)
    
    # Create extreme bullish scenario
    extreme_metrics = MemeMetrics(
        ticker="MOON",
        timestamp=datetime.now(),
        reddit_mentions_delta=15.0,  # 15x increase!
        short_interest=35.0,  # Extreme short interest
        volume_ratio=10.0,  # 10x volume
        rsi=28,  # Very oversold
        days_to_cover=6.0,
        put_call_ratio=0.3,  # Very bullish options
        unusual_options_activity=True,
        twitter_velocity=150.0,
        price=10.0,
        price_change_24h=25.0
    )
    
    extreme_result = calculator.calculate_score(extreme_metrics)
    print(f"\nExtreme Scenario: MOON")
    print(f"Score: {extreme_result['total_score']:.1f}")
    print(f"Signal: {extreme_result['signal']}")
    print(f"Confidence: {extreme_result['confidence']:.1%}")
    
    if extreme_result['total_score'] >= 80:
        print("\n🚨 EXTREME MEME ALERT! THIS IS THE WAY! 🚀🚀🚀")

if __name__ == "__main__":
    test_meme_scoring()