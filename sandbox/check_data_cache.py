#!/usr/bin/env python3
"""
Check what's in the DuckDB price cache and how much history we have.
"""

import os
import sys
import duckdb
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

# Check different potential cache locations
cache_paths = [
    'data/price_cache.duckdb',
    'sandbox/test_cache.duckdb',
    'sandbox/test_prices.duckdb'
]

def check_cache(db_path):
    """Check a DuckDB cache file."""
    if not os.path.exists(db_path):
        return None
    
    console.print(f"\n[cyan]Checking cache: {db_path}[/cyan]")
    console.print(f"File size: {os.path.getsize(db_path) / 1024 / 1024:.2f} MB")
    
    try:
        conn = duckdb.connect(db_path, read_only=True)
        
        # Check what tables exist
        tables = conn.execute("SHOW TABLES").fetchall()
        console.print(f"Tables found: {[t[0] for t in tables]}")
        
        # If tick_data table exists, analyze it
        if 'tick_data' in [t[0] for t in tables]:
            # Get summary stats
            stats = conn.execute("""
                SELECT 
                    COUNT(DISTINCT symbol) as symbols,
                    COUNT(*) as total_rows,
                    MIN(timestamp) as earliest_date,
                    MAX(timestamp) as latest_date
                FROM tick_data
            """).fetchone()
            
            console.print(f"\n📊 Cache Statistics:")
            console.print(f"  • Symbols: {stats[0]}")
            console.print(f"  • Total rows: {stats[1]:,}")
            console.print(f"  • Date range: {stats[2]} to {stats[3]}")
            
            # Get per-symbol breakdown
            symbol_data = conn.execute("""
                SELECT 
                    symbol,
                    COUNT(*) as days,
                    MIN(timestamp) as first_date,
                    MAX(timestamp) as last_date,
                    ROUND(AVG(close), 2) as avg_price,
                    ROUND(AVG(volume)) as avg_volume
                FROM tick_data
                GROUP BY symbol
                ORDER BY symbol
                LIMIT 20
            """).fetchall()
            
            # Create a nice table
            table = Table(title="Symbol Data Summary (First 20)", show_header=True)
            table.add_column("Symbol", style="cyan")
            table.add_column("Days", justify="right", style="green")
            table.add_column("First Date", style="yellow")
            table.add_column("Last Date", style="yellow")
            table.add_column("Avg Price", justify="right", style="blue")
            table.add_column("Avg Volume", justify="right", style="magenta")
            
            for row in symbol_data:
                table.add_row(
                    row[0],
                    str(row[1]),
                    str(row[2])[:10],
                    str(row[3])[:10],
                    f"${row[4]:.2f}",
                    f"{int(row[5]):,}"
                )
            
            console.print("\n")
            console.print(table)
            
            # Sample some actual data
            sample = conn.execute("""
                SELECT symbol, timestamp, close, volume
                FROM tick_data
                WHERE symbol = 'GME'
                ORDER BY timestamp DESC
                LIMIT 5
            """).fetchall()
            
            console.print("\n📈 Recent GME data (last 5 days):")
            for row in sample:
                console.print(f"  {row[1]}: ${row[2]:.2f} (Volume: {row[3]:,})")
        
        conn.close()
        return True
        
    except Exception as e:
        console.print(f"[red]Error reading cache: {e}[/red]")
        return False

def check_alpaca_default_history():
    """Check how much history Alpaca gives us by default."""
    console.print("\n[bold cyan]Alpaca Default History Settings:[/bold cyan]")
    console.print("""
    When we call get_historical_data() without dates:
    • Default period: 1 year (365 days)
    • But we're getting ~250 days (trading days only, excludes weekends/holidays)
    
    Period options we can use:
    • '1d', '5d': Last 1-5 days
    • '1mo', '3mo', '6mo': Last 1-6 months  
    • '1y', '2y', '5y': Last 1-5 years
    • 'max': All available history
    
    Current CLI default: --period 1mo (about 22 trading days)
    """)

def main():
    console.print(Panel.fit(
        "[bold cyan]DOKKAEBI Data Cache Inspector[/bold cyan]",
        style="bright_blue"
    ))
    
    # Check for caches
    found_cache = False
    for cache_path in cache_paths:
        if os.path.exists(cache_path):
            found_cache = True
            check_cache(cache_path)
    
    if not found_cache:
        console.print("\n[yellow]No cache files found![/yellow]")
        console.print("The DuckDB cache would be created when using the old Yahoo downloader.")
        console.print("With Alpaca, we're getting fresh data directly from the API each time.")
    
    # Explain Alpaca history
    check_alpaca_default_history()
    
    console.print("\n[bold green]💡 To get more history:[/bold green]")
    console.print("python src/price_downloader/cli.py download GME --period 5y")
    console.print("\n[bold green]💡 To get less (faster download):[/bold green]")
    console.print("python src/price_downloader/cli.py download GME --period 1mo")

if __name__ == "__main__":
    main()