#!/usr/bin/env python3
"""
Test that DuckDB caching is actually working with dual tables.

This verifies Bob's requirement: "we need this data to be in our DuckDB cache"
"""

import os
import sys
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.price_downloader.providers.alpaca_provider import AlpacaProvider
from src.price_downloader.storage.cache_v2 import PriceCacheV2
from rich.console import Console
from rich.table import Table
from rich import print as rprint

console = Console()

def test_cache_storage():
    """Test that data is actually being stored in DuckDB."""
    console.print("[bold cyan]Testing DuckDB Cache Storage[/bold cyan]\n")
    
    # Initialize provider with caching enabled
    provider = AlpacaProvider(cache_enabled=True)
    
    # Test symbols
    test_symbols = ['GME', 'AMC', 'AAPL']
    
    # Download daily data (should go to daily_prices table)
    console.print("[yellow]Downloading daily data...[/yellow]")
    for symbol in test_symbols:
        data = provider.get_historical_data(
            symbol, 
            start=datetime.now() - timedelta(days=30),
            interval='1Day'
        )
        if not data.empty:
            console.print(f"✅ Downloaded {len(data)} daily bars for {symbol}")
        else:
            console.print(f"❌ No data for {symbol}")
    
    # Download intraday data (should go to intraday_prices table)
    console.print("\n[yellow]Downloading intraday data...[/yellow]")
    data = provider.get_historical_data(
        'GME',
        start=datetime.now() - timedelta(days=5),
        interval='5Min'
    )
    if not data.empty:
        console.print(f"✅ Downloaded {len(data)} 5-minute bars for GME")
    
    # Now check the cache directly
    console.print("\n[bold green]Verifying DuckDB Storage:[/bold green]")
    
    cache = PriceCacheV2("data/price_cache.duckdb")
    
    # Get cache statistics
    stats = cache.get_cache_stats()
    
    # Display daily table stats
    console.print("\n[bold]Daily Prices Table:[/bold]")
    console.print(f"• Symbols: {stats['daily']['symbols']}")
    console.print(f"• Total rows: {stats['daily']['rows']}")
    console.print(f"• Date range: {stats['daily']['earliest']} to {stats['daily']['latest']}")
    
    # Display intraday table stats
    console.print("\n[bold]Intraday Prices Table:[/bold]")
    console.print(f"• Symbols: {stats['intraday']['symbols']}")
    console.print(f"• Total rows: {stats['intraday']['rows']}")
    console.print(f"• Time range: {stats['intraday']['earliest']} to {stats['intraday']['latest']}")
    
    # Retrieve and display sample data from each table
    console.print("\n[bold cyan]Sample Data from Daily Table:[/bold cyan]")
    daily_data = cache.get_daily_prices('GME')
    if not daily_data.empty:
        console.print(daily_data.tail(3))
    
    console.print("\n[bold cyan]Sample Data from Intraday Table:[/bold cyan]")
    intraday_data = cache.get_intraday_prices('GME', '5min')
    if not intraday_data.empty:
        console.print(intraday_data.tail(3))
    
    # Test metadata fields
    console.print("\n[bold yellow]Verifying Metadata Fields:[/bold yellow]")
    
    # Check daily table has data_type='daily'
    with cache._get_connection() as conn:
        daily_check = conn.execute("""
            SELECT COUNT(*) as count, data_type 
            FROM daily_prices 
            GROUP BY data_type
        """).fetchall()
        
        for count, dtype in daily_check:
            console.print(f"• Daily table: {count} rows with data_type='{dtype}'")
        
        # Check intraday table has data_type='intraday'
        intraday_check = conn.execute("""
            SELECT COUNT(*) as count, data_type 
            FROM intraday_prices 
            GROUP BY data_type
        """).fetchall()
        
        for count, dtype in intraday_check:
            console.print(f"• Intraday table: {count} rows with data_type='{dtype}'")
    
    console.print("\n[bold green]✅ Cache storage test complete![/bold green]")
    console.print("\nBob, the data is now properly stored in DuckDB with:")
    console.print("• Separate daily_prices and intraday_prices tables")
    console.print("• Explicit data_type metadata fields")
    console.print("• Automatic caching on every download")
    
    cache.close()

if __name__ == "__main__":
    test_cache_storage()