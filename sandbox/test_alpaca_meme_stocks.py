#!/usr/bin/env python3
"""
Test Alpaca with MEME STOCKS - Let's get those tendies!
"""

import os
import sys
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set Alpaca credentials
os.environ['ALPACA_API_KEY'] = 'PKU1N7FUI5SNL5UQ9PCS'
os.environ['ALPACA_API_SECRET'] = 'Y5xtRqY4CSNLgYeIDpSUnBxoLPEYdMFuYiD5PwNJ'

from src.price_downloader.providers.alpaca_provider import AlpacaProvider
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

def test_meme_stocks():
    """Download price data for meme stocks using Alpaca."""
    
    # Header
    console.print(Panel(
        "[bold cyan]DOKKAEBI Price Downloader - Alpaca Edition[/bold cyan]\n"
        "[yellow]NO MORE YAHOO FINANCE BULLSHIT![/yellow]",
        style="bright_blue"
    ))
    
    # Initialize Alpaca provider
    console.print("\n[bold green]Initializing Alpaca provider...[/bold green]")
    provider = AlpacaProvider()
    
    # Test connection
    if provider.test_connection():
        console.print("✅ [green]Connection successful![/green]\n")
    else:
        console.print("❌ [red]Connection failed![/red]")
        return
    
    # Meme stocks to download
    meme_stocks = ['GME', 'AMC', 'DNUT', 'GPRO', 'BB', 'CLOV']
    
    console.print("[bold yellow]Downloading meme stock data...[/bold yellow]\n")
    
    # Create results table
    table = Table(
        title="🚀 Meme Stock Price Data (Last 30 Days)",
        show_header=True,
        header_style="bold magenta"
    )
    
    table.add_column("Symbol", style="cyan", width=8)
    table.add_column("Latest Close", justify="right", style="green")
    table.add_column("30-Day High", justify="right", style="yellow")
    table.add_column("30-Day Low", justify="right", style="red")
    table.add_column("Avg Volume", justify="right", style="blue")
    table.add_column("Days of Data", justify="center")
    
    # Download data for each stock
    for symbol in meme_stocks:
        console.print(f"Downloading {symbol}...", style="dim")
        
        try:
            # Get historical data
            data = provider.get_historical_data(
                symbol,
                start=datetime.now() - timedelta(days=30)
            )
            
            if not data.empty:
                latest_close = data['Close'].iloc[-1]
                high_30d = data['High'].max()
                low_30d = data['Low'].min()
                avg_volume = data['Volume'].mean()
                
                table.add_row(
                    symbol,
                    f"${latest_close:.2f}",
                    f"${high_30d:.2f}",
                    f"${low_30d:.2f}",
                    f"{avg_volume:,.0f}",
                    str(len(data))
                )
                
                console.print(f"  ✅ {symbol}: Got {len(data)} days", style="green")
            else:
                table.add_row(
                    symbol,
                    "N/A",
                    "N/A", 
                    "N/A",
                    "N/A",
                    "0"
                )
                console.print(f"  ❌ {symbol}: No data", style="red")
                
        except Exception as e:
            console.print(f"  ❌ {symbol}: Error - {e}", style="red")
            table.add_row(
                symbol,
                "ERROR",
                "ERROR",
                "ERROR",
                "ERROR",
                "0"
            )
    
    # Display results
    console.print("\n")
    console.print(table)
    
    # Summary
    console.print("\n[bold green]✨ Download complete![/bold green]")
    console.print("[dim]Alpaca Markets: Professional data without the bullshit![/dim]\n")
    
    # Test batch download
    console.print("[bold cyan]Testing batch download...[/bold cyan]")
    
    batch_symbols = ['AAPL', 'MSFT', 'GOOGL']
    batch_data = provider.get_batch_data(batch_symbols)
    
    console.print(f"Batch results:")
    for symbol, data in batch_data.items():
        if not data.empty:
            console.print(f"  ✅ {symbol}: {len(data)} days")
        else:
            console.print(f"  ❌ {symbol}: No data")

if __name__ == "__main__":
    test_meme_stocks()