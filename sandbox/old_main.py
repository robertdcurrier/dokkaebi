#!/usr/bin/env python3
"""
MEME STOCK SCANNER - MAIN RUNNER
Where degenerate dreams become profitable reality
"""
import asyncio
import argparse
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import ScannerConfig
from meme_scanner.core.meme_scanner import MemeStockScanner
from meme_scanner.data.market_data import MarketDataFetcher


console = Console()


def print_banner():
    """Print the epic banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║     🚀 MEME STOCK SCANNER - TENDIE PRINTER 3000 🚀         ║
    ║                                                              ║
    ║     "Where Social Sentiment Meets Market Madness"           ║
    ║                                                              ║
    ║     Powered by: WSB Energy + Quant Math + Pure Degeneracy   ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    console.print(banner, style="bold cyan")


async def quick_scan(scanner: MemeStockScanner, tickers: list):
    """Run a quick scan of specified tickers"""
    console.print(f"\n[bold yellow]Quick scanning {len(tickers)} tickers...[/bold yellow]\n")
    
    results = []
    for ticker in tickers:
        console.print(f"Scanning {ticker}...", style="dim")
        result = await scanner.scan_ticker(ticker)
        results.append(result)
    
    # Create results table
    table = Table(title="Scan Results", show_header=True, header_style="bold magenta")
    table.add_column("Ticker", style="cyan", width=8)
    table.add_column("Score", justify="right", style="green")
    table.add_column("Signal", justify="center")
    table.add_column("Price", justify="right", style="yellow")
    table.add_column("Volume", justify="right")
    table.add_column("Analysis", width=40)
    
    # Sort by score
    results.sort(key=lambda x: x.get('score', 0), reverse=True)
    
    for result in results:
        if 'error' in result:
            table.add_row(
                result['ticker'],
                "N/A",
                "ERROR",
                "N/A",
                "N/A",
                result['error']
            )
        else:
            # Color code the signal
            signal = result['signal']
            if signal == 'STRONG_BUY':
                signal_style = "[bold green]" + signal + "[/bold green]"
            elif signal == 'BUY':
                signal_style = "[green]" + signal + "[/green]"
            elif signal == 'WATCH':
                signal_style = "[yellow]" + signal + "[/yellow]"
            else:
                signal_style = "[red]" + signal + "[/red]"
            
            table.add_row(
                result['ticker'],
                f"{result['score']:.1f}",
                signal_style,
                f"${result['metrics']['price']:.2f}",
                f"{result['metrics']['volume_ratio']:.1f}x",
                result['analysis']['summary'][:40]
            )
    
    console.print(table)
    
    # Print top pick details
    if results and results[0].get('score', 0) > 50:
        top_pick = results[0]
        console.print(f"\n[bold cyan]TOP PICK: {top_pick['ticker']}[/bold cyan]")
        console.print(f"Score: {top_pick['score']:.1f} | Signal: {top_pick['signal']}")
        console.print(f"Confidence: {top_pick['confidence']:.1%}")
        
        if 'analysis' in top_pick:
            analysis = top_pick['analysis']
            
            if analysis['bullish_factors']:
                console.print("\n[green]Bullish Factors:[/green]")
                for factor in analysis['bullish_factors']:
                    console.print(f"  • {factor}")
            
            if analysis['recommendation']:
                console.print(f"\n[bold]Recommendation:[/bold] {analysis['recommendation']}")
            
            if analysis['key_levels']:
                levels = analysis['key_levels']
                console.print(f"\n[yellow]Key Levels:[/yellow]")
                console.print(f"  Entry: ${levels['entry']:.2f}")
                console.print(f"  Stop Loss: ${levels['stop_loss']:.2f}")
                console.print(f"  Target 1: ${levels['target_1']:.2f}")
                console.print(f"  Target 2: ${levels['target_2']:.2f}")


async def monitor_mode(scanner: MemeStockScanner, tickers: list, interval: int):
    """Run continuous monitoring mode"""
    console.print(f"\n[bold green]Starting continuous monitoring...[/bold green]")
    console.print(f"Watching: {', '.join(tickers)}")
    console.print(f"Interval: {interval} minutes")
    console.print("\n[dim]Press Ctrl+C to stop[/dim]\n")
    
    await scanner.continuous_monitoring(tickers, interval)


async def test_components():
    """Test individual components"""
    console.print("[bold]Testing components...[/bold]\n")
    
    # Test market data fetcher
    console.print("Testing Market Data Fetcher...")
    fetcher = MarketDataFetcher()
    data = fetcher.get_ticker_data('GME')
    
    if data:
        console.print(f"  ✅ GME Price: ${data.get('price', 0):.2f}")
        console.print(f"  ✅ RSI: {data.get('rsi', 0):.1f}")
        console.print(f"  ✅ Volume Ratio: {data.get('volume_ratio', 0):.1f}x")
    else:
        console.print("  ❌ Failed to fetch market data")
    
    # Test config
    console.print("\nTesting Configuration...")
    config = ScannerConfig()
    if config.validate():
        console.print("  ✅ Configuration valid")
    else:
        console.print("  ⚠️  Configuration incomplete (API keys may be missing)")
    
    console.print("\n[green]Component tests complete![/green]")


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Meme Stock Scanner - Find the next moon mission'
    )
    
    parser.add_argument(
        '--tickers', '-t',
        nargs='+',
        default=['DNUT', 'KSS', 'GPRO'],
        help='Tickers to scan (default: DNUT KSS GPRO)'
    )
    
    parser.add_argument(
        '--mode', '-m',
        choices=['quick', 'monitor', 'test'],
        default='quick',
        help='Scanning mode (default: quick)'
    )
    
    parser.add_argument(
        '--interval', '-i',
        type=int,
        default=5,
        help='Monitoring interval in minutes (default: 5)'
    )
    
    parser.add_argument(
        '--no-social',
        action='store_true',
        help='Disable social media scanning'
    )
    
    args = parser.parse_args()
    
    # Print banner
    print_banner()
    
    # Initialize config
    config = ScannerConfig()
    
    if args.no_social:
        config.ENABLE_REDDIT_SCANNING = False
        config.ENABLE_TWITTER_SCANNING = False
        console.print("[yellow]Social media scanning disabled[/yellow]\n")
    
    # Run test mode if requested
    if args.mode == 'test':
        await test_components()
        return
    
    # Initialize scanner
    console.print("[cyan]Initializing scanner...[/cyan]")
    scanner = MemeStockScanner(config)
    
    # Load previous state if exists
    scanner.load_state()
    
    # Run appropriate mode
    if args.mode == 'monitor':
        await monitor_mode(scanner, args.tickers, args.interval)
    else:  # quick mode
        await quick_scan(scanner, args.tickers)
    
    # Save state
    scanner.save_state()
    
    console.print("\n[bold green]Scan complete! May the tendies be with you! 🚀[/bold green]")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[yellow]Scanner stopped by user[/yellow]")
    except Exception as e:
        console.print(f"\n[bold red]Error: {e}[/bold red]")
        raise