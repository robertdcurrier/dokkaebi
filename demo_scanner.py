#!/usr/bin/env python3
"""
Demo Scanner - Shows the meme scanner in action with simulated data
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime
import numpy as np
import pandas as pd
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from meme_scanner.models.meme_score import MemeMetrics, MemeScoreCalculator

console = Console()

def generate_mock_metrics(ticker: str) -> MemeMetrics:
    """Generate realistic mock metrics for a ticker"""
    
    # Create different profiles for different tickers
    profiles = {
        'DNUT': {  # High meme potential
            'reddit_delta': np.random.uniform(4, 8),
            'short_interest': np.random.uniform(20, 30),
            'volume_ratio': np.random.uniform(3, 6),
            'rsi': np.random.uniform(25, 40),
            'twitter_velocity': np.random.uniform(60, 120)
        },
        'KSS': {  # Moderate potential
            'reddit_delta': np.random.uniform(2, 4),
            'short_interest': np.random.uniform(15, 20),
            'volume_ratio': np.random.uniform(2, 3.5),
            'rsi': np.random.uniform(40, 55),
            'twitter_velocity': np.random.uniform(30, 60)
        },
        'GPRO': {  # High short squeeze potential
            'reddit_delta': np.random.uniform(3, 6),
            'short_interest': np.random.uniform(25, 35),
            'volume_ratio': np.random.uniform(4, 8),
            'rsi': np.random.uniform(20, 35),
            'twitter_velocity': np.random.uniform(50, 100)
        },
        'GME': {  # The OG meme stock
            'reddit_delta': np.random.uniform(2, 5),
            'short_interest': np.random.uniform(15, 25),
            'volume_ratio': np.random.uniform(2, 4),
            'rsi': np.random.uniform(35, 65),
            'twitter_velocity': np.random.uniform(40, 80)
        }
    }
    
    # Get profile or use default
    profile = profiles.get(ticker, {
        'reddit_delta': np.random.uniform(1, 3),
        'short_interest': np.random.uniform(10, 20),
        'volume_ratio': np.random.uniform(1, 2.5),
        'rsi': np.random.uniform(40, 60),
        'twitter_velocity': np.random.uniform(10, 50)
    })
    
    # Generate metrics
    return MemeMetrics(
        ticker=ticker,
        timestamp=datetime.now(),
        # Social metrics
        reddit_mentions_24h=int(np.random.uniform(50, 500)),
        reddit_mentions_delta=profile['reddit_delta'],
        reddit_sentiment=np.random.uniform(-0.2, 0.8),
        reddit_upvote_ratio=np.random.uniform(0.7, 0.95),
        twitter_mentions_24h=int(np.random.uniform(100, 1000)),
        twitter_velocity=profile['twitter_velocity'],
        twitter_sentiment=np.random.uniform(-0.1, 0.7),
        influencer_mentions=int(np.random.uniform(0, 5)),
        # Market metrics
        price=np.random.uniform(5, 100),
        price_change_24h=np.random.uniform(-5, 15),
        volume=int(np.random.uniform(1e6, 1e8)),
        volume_ratio=profile['volume_ratio'],
        market_cap=np.random.uniform(1e8, 1e10),
        # Technical
        rsi=profile['rsi'],
        macd_signal=np.random.uniform(-0.5, 0.5),
        bollinger_position=np.random.uniform(-1, 1),
        # Short data
        short_interest=profile['short_interest'],
        days_to_cover=np.random.uniform(1, 6),
        borrow_rate=np.random.uniform(5, 50),
        # Options
        options_volume=int(np.random.uniform(5000, 50000)),
        put_call_ratio=np.random.uniform(0.3, 1.5),
        gamma_exposure=np.random.uniform(100000, 2000000),
        unusual_options_activity=np.random.random() > 0.6,
        # Retail
        robinhood_holders=int(np.random.uniform(10000, 100000)),
        robinhood_holder_change=np.random.uniform(-10, 50),
        google_trends_score=np.random.uniform(10, 90)
    )

def display_banner():
    """Display the scanner banner"""
    banner = Panel.fit(
        Text.from_markup(
            "[bold cyan]🚀 MEME STOCK SCANNER DEMO 🚀[/bold cyan]\n"
            "[yellow]Live Market Simulation[/yellow]\n"
            "[dim]Where degenerates find tendies[/dim]"
        ),
        border_style="cyan"
    )
    console.print(banner)

def scan_tickers(tickers: list):
    """Scan a list of tickers and display results"""
    calculator = MemeScoreCalculator()
    results = []
    
    console.print("\n[bold yellow]Scanning tickers...[/bold yellow]\n")
    
    # Generate metrics and calculate scores
    for ticker in tickers:
        metrics = generate_mock_metrics(ticker)
        score_data = calculator.calculate_score(metrics)
        
        results.append({
            'ticker': ticker,
            'metrics': metrics,
            'score_data': score_data
        })
        
        # Show progress
        console.print(f"  ✓ {ticker} scanned", style="dim green")
    
    # Sort by score
    results.sort(key=lambda x: x['score_data']['total_score'], reverse=True)
    
    # Create results table
    table = Table(title="\n📊 Scan Results", show_header=True, header_style="bold magenta")
    table.add_column("Rank", style="cyan", width=6)
    table.add_column("Ticker", style="bold", width=8)
    table.add_column("Score", justify="right", width=8)
    table.add_column("Signal", justify="center", width=12)
    table.add_column("Price", justify="right", style="yellow", width=10)
    table.add_column("24h %", justify="right", width=8)
    table.add_column("Volume", justify="right", width=8)
    table.add_column("Short %", justify="right", width=8)
    table.add_column("RSI", justify="right", width=6)
    table.add_column("Key Factors", width=40)
    
    for idx, result in enumerate(results, 1):
        metrics = result['metrics']
        score_data = result['score_data']
        
        # Color code signal
        signal = score_data['signal']
        if signal == 'STRONG_BUY':
            signal_display = f"[bold green]{signal}[/bold green]"
        elif signal == 'BUY':
            signal_display = f"[green]{signal}[/green]"
        elif signal == 'WATCH':
            signal_display = f"[yellow]{signal}[/yellow]"
        else:
            signal_display = f"[red]{signal}[/red]"
        
        # Color code 24h change
        change = metrics.price_change_24h
        if change > 0:
            change_display = f"[green]+{change:.1f}%[/green]"
        else:
            change_display = f"[red]{change:.1f}%[/red]"
        
        # Determine key factors
        factors = []
        if metrics.reddit_mentions_delta > 5:
            factors.append("🔥 Reddit surge")
        if metrics.short_interest > 25:
            factors.append("🩳 High shorts")
        if metrics.volume_ratio > 4:
            factors.append("📊 Volume spike")
        if metrics.rsi < 30:
            factors.append("📉 Oversold")
        if metrics.unusual_options_activity:
            factors.append("🎯 Unusual options")
        
        table.add_row(
            f"#{idx}",
            metrics.ticker,
            f"{score_data['total_score']:.1f}",
            signal_display,
            f"${metrics.price:.2f}",
            change_display,
            f"{metrics.volume_ratio:.1f}x",
            f"{metrics.short_interest:.1f}%",
            f"{metrics.rsi:.0f}",
            " ".join(factors[:3])  # Show top 3 factors
        )
    
    console.print(table)
    
    # Show top pick details
    if results and results[0]['score_data']['total_score'] > 50:
        top_result = results[0]
        metrics = top_result['metrics']
        score_data = top_result['score_data']
        
        # Create detailed panel for top pick
        details = f"""
[bold cyan]🏆 TOP PICK: {metrics.ticker}[/bold cyan]

[yellow]Score:[/yellow] {score_data['total_score']:.1f}/100
[yellow]Signal:[/yellow] {score_data['signal']}
[yellow]Confidence:[/yellow] {score_data['confidence']:.1%}

[bold]Component Scores:[/bold]
"""
        for component, score in score_data['components'].items():
            bar = "█" * int(score/10) + "░" * (10 - int(score/10))
            details += f"  {component:25s} [{bar}] {score:.0f}\n"
        
        details += f"""
[bold]Key Metrics:[/bold]
  Reddit Momentum: {metrics.reddit_mentions_delta:.1f}x baseline
  Twitter Velocity: {metrics.twitter_velocity:.1f}% acceleration
  Short Interest: {metrics.short_interest:.1f}%
  Days to Cover: {metrics.days_to_cover:.1f}
  Options P/C Ratio: {metrics.put_call_ratio:.2f}
  
[bold]Technical Levels:[/bold]
  Current Price: ${metrics.price:.2f}
  Entry Target: ${metrics.price * 0.98:.2f}
  Stop Loss: ${metrics.price * 0.92:.2f}
  Target 1: ${metrics.price * 1.15:.2f} (+15%)
  Target 2: ${metrics.price * 1.30:.2f} (+30%)
  Moon Target: ${metrics.price * 2.00:.2f} (+100%)
"""
        
        if score_data['total_score'] >= 70:
            details += "\n[bold red]⚠️ HIGH MEME ALERT - POTENTIAL SQUEEZE INCOMING![/bold red]"
        
        panel = Panel(details, title="Detailed Analysis", border_style="green")
        console.print(panel)
    
    # Show alerts
    console.print("\n[bold]📢 Alerts:[/bold]")
    for result in results:
        if result['score_data']['total_score'] >= 70:
            console.print(
                f"  🚨 [bold red]{result['ticker']}[/bold red] - "
                f"EXTREME MEME ACTIVITY DETECTED! Score: {result['score_data']['total_score']:.1f}"
            )
        elif result['score_data']['total_score'] >= 60:
            console.print(
                f"  ⚠️  [yellow]{result['ticker']}[/yellow] - "
                f"High social momentum building. Score: {result['score_data']['total_score']:.1f}"
            )

def main():
    """Main demo function"""
    display_banner()
    
    # Default tickers
    tickers = ['DNUT', 'KSS', 'GPRO', 'GME', 'AMC', 'BB', 'NOK', 'PLTR']
    
    # Get command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == '--help':
            console.print("\nUsage: python demo_scanner.py [tickers...]")
            console.print("Example: python demo_scanner.py DNUT KSS GPRO")
            return
        else:
            tickers = sys.argv[1:]
    
    console.print(f"\n[dim]Monitoring {len(tickers)} tickers: {', '.join(tickers)}[/dim]")
    
    # Run scan
    scan_tickers(tickers)
    
    console.print("\n[bold green]✅ Scan complete! May your tendies be plentiful! 🚀[/bold green]\n")
    
    # Show disclaimer
    disclaimer = Panel(
        "[dim]This is a demonstration with simulated data.\n"
        "Not financial advice. Always do your own research.\n"
        "Past memes do not guarantee future tendies.[/dim]",
        title="Disclaimer",
        border_style="dim"
    )
    console.print(disclaimer)

if __name__ == "__main__":
    main()